import sys
import os
import re
import datetime
import time

from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from systemrdl.rdltypes import AccessType, OnReadType, OnWriteType
from systemrdl import RDLWalker

from .pdf_creator import PDFCreator
from .pre_export_listener import PreExportListener

class PDFExporter:
    
    def __init__(self, **kwargs):
        """
        Constructor for the PDF Exporter class
        """

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        # Define variables used during export

        # Top-level node
        self.top = None

        # Dictionary of group-like nodes (addrmap, regfile) and their bus
        # widths.
        # key = node path
        # value = max accesswidth/memwidth used in node's descendants
        self.bus_width_db = {}

        # Dictionary of root-level type definitions
        # key = definition type name
        # value = representative object
        #   components, this is the original_def (which can be None in some cases)
        self.namespace_db = {}

        # Used for making the instance name(s) in uppercase or lowercase
        self.use_uppercase_inst_name = True

        # Used for address width - Default 32bits
        self.address_width = 32 

        # Used for absoulte address calculations
        self.base_address = 0x0

        # Get the today's date (mm-dd-yyyy)
        self.today_date = datetime.date.today().strftime('%m-%d-%Y')

        # Get the current time (hh:mm:ss)
        self.current_time = time.strftime('%H:%M:%S') 

        # Create the global variable for pdf creation
        global pdf_create

    def set_address_width(self, node: Node):
        self.address_width = self.get_address_width(node)

    def set_base_address(self, node:Node):
        # Get the property value
        amap = node.owning_addrmap
        self.base_address = amap.get_property("base_address_p", default=0x0);

    def export(self, node_list: list, path: str, **kwargs):
        """
        Perform the export!

        Parameters
        ----------
        node_list: List of systemrdl.Node(s)
            Top-level node to export. Can be the top-level `RootNode` or any
            internal `AddrmapNode`.

        path: str
            Output file.

        use_uppercase_inst_name: bool
            If True (Default), all the instance names will be in uppercase

            if False, all the instance names will be in lowercase
        """

        self.use_uppercase_inst_name = kwargs.pop("use_uppercase_inst_name", True)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        # Call the method for initiating the document creation
        self.generate_output_pdf(node_list, path)

    #####################################################################
    # Generate the output pdf files
    #####################################################################
    def generate_output_pdf(self, root_list: list, path: str):

        # Create the object
        self.pdf_create = PDFCreator(path)

        # Go through multiple input files 
        # root_list is elaborated output of input .rdl file(s)
        for root_id, root in enumerate(root_list):
            for node in root.descendants(in_post_order=True):

                # Traverse all the address maps
                if isinstance(node, AddrmapNode):
                    self.create_regmap_list(node, root_id)
                    self.create_regmap_registers_info(node, root_id)

            # Dump all the data into the pdf file 
            self.pdf_create.build_document()

    #####################################################################
    # Create the regmap list for all regiters
    #####################################################################
    def create_regmap_list(self, node: AddrmapNode, root_id: int): 
        addrmap_strg = {}
        # set the required variable 
        self.set_address_width(node)
        self.set_base_address(node)

        addrmap_strg['Name'] = "%s %s" % ((root_id+1),self.get_name(node))
        addrmap_strg['Desc'] = self.get_desc(node)
        addrmap_strg['Base_address'] = self.get_base_address(node)
        addrmap_strg['Size'] = self.get_addrmap_size(node)
        self.pdf_create.create_addrmap_info(addrmap_strg)

        # Create a list of all registers for the map
        for reg_id, reg in enumerate(node.registers()):
            addrmap_reg_list_strg = {}
            
            # Reserved addresses at the start of the address map
            if reg_id == 0 and reg.address_offset != 0:
                addrmap_reg_list_strg['Offset']     = self.format_address(reg.address_offset-1)
                addrmap_reg_list_strg['Identifier'] = "-" 
                addrmap_reg_list_strg['Name']       = "-"
                self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 1)
            # Reserved addresses in between the address map
            elif (reg_id != 0) and (reg_previous.address_offset + reg_previous.total_size) < reg.address_offset:
                index = 0
                while((reg_previous.address_offset + reg_previous.total_size + index) < reg.address_offset):
                    addrmap_reg_list_strg['Offset']     = self.format_address(reg_previous.address_offset + reg_previous.total_size + index)
                    addrmap_reg_list_strg['Identifier'] = "-" 
                    addrmap_reg_list_strg['Name']       = "-"
                    self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 1)
                    index = index + reg.total_size

            # Normal registers in the address map
            addrmap_reg_list_strg['Offset']     = self.format_address(reg.address_offset) 
            addrmap_reg_list_strg['Identifier'] = self.get_inst_name(reg)
            addrmap_reg_list_strg['Id']         = "%s.%s" % ((root_id+1),(reg_id+1))
            addrmap_reg_list_strg['Name']       = self.get_name(reg)
            self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 0)

            # Store previous item
            reg_previous = reg

        self.pdf_create.dump_reg_list_info()

    #####################################################################
    # Create the regiters info
    #####################################################################
    def create_regmap_registers_info(self, node: AddrmapNode, root_id: int): 
        # Traverse all the registers for separate register(s) section
        for reg_id, reg in enumerate(node.registers()):
            registers_strg = {}
            registers_strg['Name'] = "%s.%s %s" % ((root_id+1),(reg_id+1),self.get_name(reg))
            registers_strg['Desc'] = self.get_desc(reg)
            registers_strg['Absolute_address'] = self.get_reg_absolute_address(reg)
            registers_strg['Base_offset'] = self.get_reg_offset(reg)
            registers_strg['Reset'] = self.get_reg_reset(reg)
            registers_strg['Access'] = self.get_reg_access(reg)
            registers_strg['Size'] = self.get_reg_size(reg)

            self.pdf_create.create_register_info(registers_strg)

            # Reverse the fields order - MSB first
            fields_list = []
            for field in reg.fields():
                if isinstance(field, FieldNode):
                    fields_list.append(field)

            fields_list.reverse()

            # Traverse all the fields
            for field in fields_list:
                fields_list_strg = {}
                fields_list_strg['Bits']        = self.get_field_bits(field)
                fields_list_strg['Identifier']  = self.get_inst_name(field)
                fields_list_strg['Access']      = self.get_field_access(field)
                fields_list_strg['Reset']       = self.get_field_reset(field)
                fields_list_strg['Name']        = self.get_name(field)
                fields_list_strg['Description'] = self.get_desc(field)

                self.pdf_create.create_fields_list_info(fields_list_strg)

            self.pdf_create.dump_field_list_info()

    #####################################################################
    # Below methods are used for getting the required data from
    # the elaborated object
    #####################################################################
    def get_name(self, node: Node) -> str:
        s = node.get_property("name")
        return s

    def get_desc(self, node: Node) -> str:
        s = (node.get_property("desc", default="")).replace("\n"," ")
        return s

    def get_addrmap_size(self, node: Node) -> str:
        # Get the hex value 
        s = hex(node.size)
        return s

    def get_inst_name(self, node: Node) -> str:
        """
        Returns the class instance name
        """

        if self.use_uppercase_inst_name:
            return node.inst_name.upper()
        else:
            return node.inst_name.lower()

    def is_field_reserved(self, field: FieldNode) -> bool:
        """
        Returns True if the field is reserved
        """

        # Check if the field is reserved type 
        is_field_rsvd = re.search("reserved",field.inst_name, re.IGNORECASE)

        if is_field_rsvd:
            return True
        else:
            return False

    def get_inst_map_name(self, node: Node) -> str:
        """
        Returns the address map name
        """

        # Default value
        amap_name = "reg_map";

        # Check if the udp is defined
        is_defined = self.check_udp("map_name_p", node)
        
        if not is_defined:
            return amap_name
   
        # Get the upd value 
        amap = node.owning_addrmap
        amap_name = amap.get_property("map_name_p", default=amap_name);

        return amap_name.upper()

    def get_field_bits(self, field: FieldNode) -> str:
        """
        Get the bits [msb:lsb]
        """

        if field.msb != field.lsb:
            s = "[%s:%s]" % (field.msb,field.lsb)
        else:
            s = "[%s]" % (field.msb)

        return s

    def get_field_access(self, field: FieldNode) -> str:
        """
        Get field's UVM access string
        """
        sw = field.get_property("sw")
        onread = field.get_property("onread")
        onwrite = field.get_property("onwrite")

        if sw == AccessType.rw:
            if (onwrite is None) and (onread is None):
                return "RW"
            elif (onread == OnReadType.rclr) and (onwrite == OnWriteType.woset):
                return "W1SRC"
            elif (onread == OnReadType.rclr) and (onwrite == OnWriteType.wzs):
                return "W0SRC"
            elif (onread == OnReadType.rclr) and (onwrite == OnWriteType.wset):
                return "WSRC"
            elif (onread == OnReadType.rset) and (onwrite == OnWriteType.woclr):
                return "W1CRS"
            elif (onread == OnReadType.rset) and (onwrite == OnWriteType.wzc):
                return "W0CRS"
            elif (onread == OnReadType.rset) and (onwrite == OnWriteType.wclr):
                return "WCRS"
            elif onwrite == OnWriteType.woclr:
                return "RW1C"
            elif onwrite == OnWriteType.woset:
                return "RW1S"
            elif onwrite == OnWriteType.wot:
                return "RW1T"
            elif onwrite == OnWriteType.wzc:
                return "RW0C"
            elif onwrite == OnWriteType.wzs:
                return "RW0S"
            elif onwrite == OnWriteType.wzt:
                return "RW0T"
            elif onwrite == OnWriteType.wclr:
                return "RWC"
            elif onwrite == OnWriteType.wset:
                return "RWS"
            elif onread == OnReadType.rclr:
                return "WRC"
            elif onread == OnReadType.rset:
                return "WRS"
            else:
                return "RW"

        elif sw == AccessType.r:
            if onread is None:
                return "RO"
            elif onread == OnReadType.rclr:
                return "RC"
            elif onread == OnReadType.rset:
                return "RS"
            else:
                return "RO"

        elif sw == AccessType.w:
            if onwrite is None:
                return "WO"
            elif onwrite == OnWriteType.wclr:
                return "WOC"
            elif onwrite == OnWriteType.wset:
                return "WOS"
            else:
                return "WO"

        elif sw == AccessType.rw1:
            return "W1"

        elif sw == AccessType.w1:
            return "WO1"

        else: # na
            return "NOACCESS"


    def get_field_reset(self, field: FieldNode) -> str:
        """
        Get the field reset value
        """

        # Get the value 
        field_reset = field.get_property('reset',default=0) 

        # Format the value
        field_width = field.width
        no_of_nib = field_width/4

        # 64bit data
        if no_of_nib == 16:
            format_number = no_of_nib + 3
        # 32bit data
        elif no_of_nib == 8:
            format_number = no_of_nib + 1
        #  16bit or 8bit data     
        else:
            format_number = no_of_nib 

        # format the string to have underscore in hex value
        format_str = '{:0' + str(int(format_number)) + '_x}'
        final_value = (format_str.format(field_reset))

        return (str(field_width) +"'h"+ final_value.upper())


    def get_mem_access(self, mem: MemNode) -> str:
        sw = mem.get_property("sw")
        if sw == AccessType.r:
            return "R"
        else:
            return "RW"

    def get_reg_absolute_address(self, node: RegNode) -> str:
        #abs_addr = self.absolute_address
        abs_addr = self.base_address + node.address_offset
        s = self.format_address(abs_addr)
        return s

    def get_reg_offset(self, node: RegNode) -> str:
        add_offset = node.address_offset
        s = self.format_address(add_offset)
        return s

    def get_reg_access(self, node: RegNode) -> str:
        """
        Get register's access for the map
        """

        # Default value
        regaccess = "RW";

        # Check if the udp is defined
        is_defined = self.check_udp("regaccess_p", node)
        
        if not is_defined:
            return regaccess
   
        # Get the upd value 
        regaccess = node.get_property("regaccess_p", default=regaccess)

        return regaccess

    def get_reg_reset(self, node: RegNode) -> str:
        """
        Concatenate the value of the individual fields
        to form the register value
        """

        reg_reset = 0;
        
        # Deduce the reset value
        for field in node.fields():
            if isinstance(field, FieldNode):
                field_reset = field.get_property('reset',default=0) 
                field_lsb_pos = field.lsb
                reg_reset |= field_reset << field_lsb_pos
        

        # Format the value
        register_width = node.get_property('regwidth')
        no_of_nib = register_width/4

        # 64bit data
        if no_of_nib == 16:
            format_number = no_of_nib + 3
        # 32bit data
        elif no_of_nib == 8:
            format_number = no_of_nib + 1
        #  16bit or 8bit data     
        else:
            format_number = no_of_nib 

        # format the string to have underscore in hex value
        format_str = '{:0' + str(int(format_number)) + '_x}'
        final_value = (format_str.format(reg_reset))

        return (str(register_width) +"'h"+ final_value.upper())

    def get_reg_size(self, node: RegNode) -> str:
        """
        Get the size of the register
        """

        return (hex(node.total_size))

    def check_udp(self, prop_name: str, node: Node) -> bool:
        """
        Checks if the property name is a udp
        """

        prop_ups = node.list_properties(include_native=False, include_udp=True)

        if prop_name in prop_ups:
            return True
        else:
            return False

    def get_address_width(self, node: Node) -> str:
        """
        Returns the address width for the register access
        """

        # Default value
        address_width = 32;

        amap = node.owning_addrmap

        # Check if the udp is defined
        is_defined = self.check_udp("address_width_p", node)
        
        if not is_defined:
            return address_width
   
        # Get the upd value 
        address_width = amap.get_property("address_width_p", default=address_width);
    
        return (int(address_width)) 

    def get_base_address(self, node: Node) -> str:
        """
        Returns the base address for the register block 
        """
       
        # Default value 
        base_address = 0x0

        # Get the property value
        amap = node.owning_addrmap

        # Check if the udp is defined
        is_defined = self.check_udp("base_address_p", node)
        
        if not is_defined:
            return (self.format_address(base_address)) 

        # Get the value
        base_address = amap.get_property("base_address_p", default=base_address);

        return (self.format_address(base_address)) 

    def format_address(self, address: str) -> str:

        no_of_nib = self.address_width/4

        # 64bit address
        if no_of_nib == 16:
            format_number = no_of_nib + 3
        # 32bit address     
        else:
            format_number = no_of_nib +1

        # format the string to have underscore in hex value
        format_str = '{:0' + str(int(format_number)) + '_x}'
        final_value = (format_str.format(address))

        return (str(self.address_width) +"'h"+ final_value.upper())

    def get_array_address_offset_expr(self, node: AddressableNode) -> str:
        """
        Returns an expression to calculate the address offset
        for example, a 4-dimensional array allocated as:
            [A][B][C][D] @ X += Y
        results in:
            X + i0*B*C*D*Y + i1*C*D*Y + i2*D*Y + i3*Y
        """
        s = "'h%x" % node.raw_address_offset
        if node.is_array:
            for i in range(len(node.array_dimensions)):
                m = node.array_stride
                for j in range(i+1, len(node.array_dimensions)):
                    m *= node.array_dimensions[j]
                s += " + i%d*'h%x" % (i, m)
        return s


    def get_endianness(self, node: Node) -> str:
        amap = node.owning_addrmap
        if amap.get_property("bigendian"):
            return "UVM_BIG_ENDIAN"
        elif amap.get_property("littleendian"):
            return "UVM_LITTLE_ENDIAN"
        else:
            return "UVM_NO_ENDIAN"


    def get_bus_width(self, node: Node) -> int:
        """
        Returns group-like node's bus width (in bytes)
        """
        width = self.bus_width_db[node.get_path()]

        # Divide by 8, rounded up
        if width % 8:
            return width // 8 + 1
        else:
            return width // 8


    def roundup_to(self, x: int, n: int) -> int:
        """
        Round x up to the nearest n
        """
        if x % n:
            return (x//n + 1) * n
        else:
            return (x//n) * n


    def roundup_pow2(self, x):
        return 1<<(x-1).bit_length()

