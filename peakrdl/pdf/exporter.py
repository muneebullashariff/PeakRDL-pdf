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

        # Get the today's date (mm-dd-yyyy)
        self.today_date = datetime.date.today().strftime('%m-%d-%Y')

        # Get the current time (hh:mm:ss)
        self.current_time = time.strftime('%H:%M:%S') 

    def set_address_width(self, node: Node):
        self.address_width = self.get_address_width(node)

    def export(self, node: Node, path: str, **kwargs):
        """
        Perform the export!

        Parameters
        ----------
        node: systemrdl.Node
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


        ## If it is the root node, skip to top addrmap
        #if isinstance(node, RootNode):
        #    node = node.top
        #self.top = node

        ## First, traverse the model and collect some information
        #self.bus_width_db = {}
        #RDLWalker().walk(self.top, PreExportListener(self))


        context = {
            'top_node': node,
            'RegNode': RegNode,
            'RegfileNode': RegfileNode,
            'AddrmapNode': AddrmapNode,
            'MemNode': MemNode,
            'AddressableNode': AddressableNode,
            'isinstance': isinstance,
            'class_needs_definition': self.class_needs_definition,
            'get_class_name': self.get_class_name,
            'get_class_friendly_name': self.get_class_friendly_name,
            'get_inst_name': self.get_inst_name,
            'is_field_reserved': self.is_field_reserved,
            'get_inst_map_name': self.get_inst_map_name,
            'get_field_access': self.get_field_access,
            'get_reg_access': self.get_reg_access,
            'get_address_width': self.get_address_width,
            'get_base_address': self.get_base_address,
            'get_array_address_offset_expr': self.get_array_address_offset_expr,
            'get_endianness': self.get_endianness,
            'get_bus_width': self.get_bus_width,
            'get_mem_access': self.get_mem_access,
            'roundup_to': self.roundup_to,
            'roundup_pow2': self.roundup_pow2,
            'get_today_date': self.today_date,
            'get_current_time': self.current_time
        }

        self.generate_output_pdf(node, path)

    ###
    # Generate the output pdf files
    ###
    def generate_output_pdf(self, root: RootNode, path: str):

        # Create the object
        pdf_create = PDFCreator(path)

        #pdf_create.creation() 

        strg = []
        addrmap_strg = {}
        addrmap_reg_list_strg = {}
        strg.append("-------------------------")

        for node in root.descendants(in_post_order=True):
            # Traverse all the address maps
            if isinstance(node, AddrmapNode):
                # set the address width variable 
                self.set_address_width(node)

                addrmap_strg['Name'] = self.get_name(node)
                addrmap_strg['Desc'] = self.get_addrmap_desc(node)
                addrmap_strg['Base_address'] = self.get_base_address(node)
                addrmap_strg['Size'] = self.get_addrmap_size(node)
                pdf_create.create_addrmap_info(addrmap_strg)

                # Create a list of all registers for the map
                for reg_id, reg in enumerate(node.registers()):

                    # Reserved addresses at the start of the address map
                    if reg_id == 0 and reg.address_offset != 0:
                        addrmap_reg_list_strg['Offset']     = self.format_address(reg.address_offset-1)
                        addrmap_reg_list_strg['Identifier'] = "-" 
                        addrmap_reg_list_strg['Name']       = "-"
                        pdf_create.create_reg_list_info(addrmap_reg_list_strg)
                    # Reserved addresses in between the address map
                    elif (reg_id != 0) and (reg_previous.address_offset + reg_previous.total_size) < reg.address_offset:
                        index = 0
                        while((reg_previous.address_offset + reg_previous.total_size + index) < reg.address_offset):
                            addrmap_reg_list_strg['Offset']     = self.format_address(reg_previous.address_offset + reg_previous.total_size + index)
                            addrmap_reg_list_strg['Identifier'] = "-" 
                            addrmap_reg_list_strg['Name']       = "-"
                            pdf_create.create_reg_list_info(addrmap_reg_list_strg)
                            index = index + reg.total_size

                    # Normal registers in the address map
                    addrmap_reg_list_strg['Offset']     = self.format_address(reg.address_offset) 
                    addrmap_reg_list_strg['Identifier'] = self.get_inst_name(reg)
                    addrmap_reg_list_strg['Name']       = self.get_name(reg)
                    pdf_create.create_reg_list_info(addrmap_reg_list_strg)

                    # Store previous item
                    reg_previous = reg

                pdf_create.dump_reg_list_info()

                # Traverse all the registers
                for reg in node.registers():
                    if isinstance(reg, RegNode):
                        strg.append(self.get_inst_name(reg))
                        #strg.append(exporter._get_reg_access(reg))


                        # Reverse the fields order - MSB first
                        fields_list = []
                        for field in reg.fields():
                            if isinstance(field, FieldNode):
                                fields_list.append(field)

                        fields_list.reverse()

                        # Traverse all the fields
                        for field in fields_list:
                            strg.append(self.get_inst_name(field))
                            strg.append(self.get_field_access(field))

                        strg.append("-------------------------")

        # Display the contents
        for k in addrmap_strg:
            print(k)
        
    def get_name(self, node: Node) -> str:
        s = node.get_property("name")
        return s

    def get_addrmap_desc(self, node: Node) -> str:
        s = (node.get_property("desc")).replace("\n"," ")
        return s

    def get_addrmap_size(self, node: Node) -> str:
        # Get the hex value 
        s = hex(node.size)
        return s

    def get_package_name(self, path: str) -> str:
        s = os.path.splitext(os.path.basename(path))[0]
        s = re.sub(r'[^\w]', "_", s)
        return s


    def get_include_guard(self, path: str) -> str:
        s = os.path.basename(path)
        s = re.sub(r'[^\w]', "_", s).upper()
        return s


    def get_class_name(self, node: Node) -> str:
        """
        Returns the class type name.
        Shall be unique enough to prevent type name collisions
        """
        if self.reuse_class_definitions:
            scope_path = node.inst.get_scope_path(scope_separator="__")

            if (scope_path is not None) and (node.type_name is not None):
                if scope_path:
                    class_name = scope_path + "__" + node.type_name
                else:
                    class_name = node.type_name
            else:
                # Unable to determine a reusable type name. Fall back to hierarchical path
                class_name = node.get_rel_path(
                    self.top.parent,
                    hier_separator="__", array_suffix="", empty_array_suffix=""
                )
                # Add prefix to prevent collision when mixing namespace methods
                class_name = "xtern__" + class_name
        else:
            class_name = node.get_rel_path(
                self.top.parent,
                hier_separator="__", array_suffix="", empty_array_suffix=""
            )

        return class_name


    def get_class_friendly_name(self, node: Node) -> str:
        """
        Returns a useful string that helps identify the class definition in
        a comment
        """
        if self.reuse_class_definitions:
            scope_path = node.inst.get_scope_path()

            if (scope_path is not None) and (node.type_name is not None):
                if scope_path:
                    friendly_name = scope_path + "::" + node.type_name
                else:
                    friendly_name = node.type_name
            else:
                # Unable to determine a reusable type name. Fall back to hierarchical path
                friendly_name = node.get_rel_path(
                    self.top.parent,
                    hier_separator="__", array_suffix="", empty_array_suffix=""
                )
        else:
            friendly_name = node.get_rel_path(self.top.parent)

        return type(node.inst).__name__ + " - " + friendly_name


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
        is_reserved = re.search("reserved",field.inst_name, re.IGNORECASE)

        if is_reserved:
            return True
        else:
            return False

    def get_inst_map_name(self, node: Node) -> str:
        """
        Returns the address map name
        """

        amap = node.owning_addrmap
        amap_name = amap.get_property("map_name_p");

        if amap_name:
            amap_name = amap_name.upper()
        else:
            amap_name = "reg_map"

        return amap_name

    def class_needs_definition(self, node: Node) -> bool:
        """
        Checks if the class that defines this node already exists.
        If not, returns True, indicating that a definition shall be emitted.

        If returning True, then the act of calling this function also registers
        the class definition into the namespace database so that future calls
        for equivalent node types will return False
        """
        type_name = self._get_class_name(node)

        if type_name in self.namespace_db:
            obj = self.namespace_db[type_name]

            # Sanity-check for collisions
            if (obj is None) or (obj is not node.inst.original_def):
                raise RuntimeError("Namespace collision! Type-name generation is not robust enough to create unique names!")

            # This object likely represents the existing class definition
            # Ok to omit the re-definition
            return False

        # Need to emit a new definition
        # First, register it in the namespace
        self.namespace_db[type_name] = node.inst.original_def
        return True


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
                return "W1C"
            elif onwrite == OnWriteType.woset:
                return "W1S"
            elif onwrite == OnWriteType.wot:
                return "W1T"
            elif onwrite == OnWriteType.wzc:
                return "W0C"
            elif onwrite == OnWriteType.wzs:
                return "W0S"
            elif onwrite == OnWriteType.wzt:
                return "W0T"
            elif onwrite == OnWriteType.wclr:
                return "WC"
            elif onwrite == OnWriteType.wset:
                return "WS"
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


    def get_mem_access(self, mem: MemNode) -> str:
        sw = mem.get_property("sw")
        if sw == AccessType.r:
            return "R"
        else:
            return "RW"

    def get_reg_access(self, reg: RegNode) -> str:
        """
        Get register's UVM access for the map - string
        """

        regaccess = reg.get_property("regaccess_p")

        if regaccess:
            return regaccess
        else:
            return "RW"

    def get_address_width(self, node: Node) -> str:
        """
        Returns the address width for the register access
        """

        amap = node.owning_addrmap
        address_width = amap.get_property("address_width_p");
    
        if address_width:
            # Convert it to decimal value
            address_width = int(address_width)
        else: 
            # Default value
            address_width = 32;
    
        return address_width 

    def get_base_address(self, node: Node) -> str:
        """
        Returns the base address for the register block 
        """
        
        # Get the property value
        amap = node.owning_addrmap
        base_address = amap.get_property("base_address_p");

        # Get the formatted base_address
        if base_address:
            base_address = self.format_address(base_address)
        else:
            base_address = self.format_address(0)

        return base_address 

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

    def get_reg_offset(self, node: RegNode) -> str:
        add_offset = node.address_offset
        s = self.format_address(add_offset)
        return s

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

