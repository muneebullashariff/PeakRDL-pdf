import sys
import os
import re
import datetime
import time
import hashlib
import operator
import math
import shutil
import markdown
from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from systemrdl.rdltypes import AccessType, OnReadType, OnWriteType
from systemrdl import RDLWalker

from .pdf_creator import PDFCreator
from .pre_export_listener import PreExportListener

from typing import Any, Optional, Tuple, List, Dict, Union
from collections import OrderedDict
from .search_indexer import SearchIndexer
from systemrdl.component import Component
import xml.dom.minidom

class BigInt:
    def __init__(self, v: int):
        self.v = v

def get_node_uid(node: Node) -> str:
    """
    Returns the node's UID string
    """
    node_path = node.get_path(array_suffix="", empty_array_suffix="")
    path_hash = hashlib.sha1(node_path.encode('utf-8')).hexdigest()
    return path_hash

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

        self.RALData = [] # type: List[Dict[str, Any]]
        self.RootNodeIds = [] # type: List[int]
        self.current_id = -1
        self.indexer = None # type: SearchIndexer

        markdown_inst = kwargs.pop("markdown_inst", None)

        if markdown_inst is None:
            self.markdown_inst = markdown.Markdown(
                extensions = [
                    'extra',
                    'admonition',
                    'mdx_math',
                ],
                extension_configs={
                    'mdx_math':{
                        'add_preview': True
                    }
                }
            )
        else:
            self.markdown_inst = markdown_inst

        # Create the global variable for pdf creation
        global pdf_create

    def set_address_width(self, node: Node):
        self.address_width = self.get_address_width(node)

    def set_base_address(self, node:Node):
        # Get the property value
        amap = node.owning_addrmap
        self.base_address = amap.get_property("base_address_p", default=0x0);

    def export(self, nodes: 'Union[Node, List[Node]]', path: str, **kwargs):
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

        if not isinstance(nodes, list):
            nodes = [nodes]

        # If it is the root node, skip to top addrmap
        for i, node in enumerate(nodes):
            if isinstance(node, RootNode):
                nodes[i] = node.top

        self.RALData = []
        self.current_id = -1
        self.indexer = SearchIndexer()

        self.use_uppercase_inst_name = kwargs.pop("use_uppercase_inst_name", True)

        self.skip_not_present = kwargs.pop("skip_not_present", True) # type: ignore

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        self.pdf_create = PDFCreator(path)


        # Traverse trees
        for node in nodes:
            if node.get_property('bridge'):
                node.env.msg.warning(
                    "HTML generator does not have proper support for bridge addmaps yet. The 'bridge' property will be ignored.",
                    node.inst.property_src_ref.get('bridge', node.inst.inst_src_ref)
                )
            uid = get_node_uid(node)
            #print(uid)
            self.visit_addressable_node(node)

        root_id = 0
        # Call the method for initiating the document creation
        self.create_regfile_list(node,root_id)

        for regfile_id, regfile in enumerate(node.children()):
            #print("create_regmap_list regfile_id:%x"%(regfile_id))
            self.create_regmap_list(regfile, root_id, regfile_id)
            #for child in regfile.children():
            #    print(child)
            self.create_registers_info(regfile, root_id, regfile_id)

        self.pdf_create.build_document()

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
                    self.create_registers_info(node, root_id)

        # Dump all the data into the pdf file 
            # Dump all the data into the pdf file 
        # Dump all the data into the pdf file 
            # Dump all the data into the pdf file 
        # Dump all the data into the pdf file 
        self.pdf_create.build_document()


    #####################################################################
    # Create the nodes list
    #####################################################################
    def visit_addressable_node(self, node: Node, parent_id: 'Optional[int]'=None) -> int:
        self.current_id += 1
        this_id = self.current_id
        child_ids = [] # type: List[int]

        self.indexer.add_node(node, this_id)

        ral_entry = {
            'parent'    : parent_id,
            'children'  : child_ids,
            'name'      : node.inst.inst_name,
            'offset'    : BigInt(node.inst.addr_offset),
            'size'      : BigInt(node.size),
        }
        if node.inst.is_array:
            ral_entry['dims'] = node.inst.array_dimensions
            ral_entry['stride'] = BigInt(node.inst.array_stride)
            ral_entry['idxs'] = [0] * len(node.inst.array_dimensions)

        if isinstance(node, RegNode):
            ral_fields = []
            for i, field in enumerate(node.fields(skip_not_present=self.skip_not_present)):
                self.indexer.add_node(field, this_id, i)

                field_reset = field.get_property("reset", default=0)
                if isinstance(field_reset, Node):
                    # Reset value is a reference. Dynamic RAL data does not
                    # support this, so stuff a 0 in its place
                    field_reset = 0

                ral_field = {
                    'name' : field.inst.inst_name,
                    'lsb'  : field.inst.lsb,
                    'msb'  : field.inst.msb,
                    'reset': BigInt(field_reset),
                    'disp' : 'H'
                }

                field_enum = field.get_property("encode")
                if field_enum is not None:
                    ral_field['encode'] = True
                    ral_field['disp'] = 'E'

                ral_fields.append(ral_field)

            ral_entry['fields'] = ral_fields

        # Insert entry now to ensure proper position in list
        self.RALData.append(ral_entry)

        # Insert root nodes to list
        if parent_id is None:
            self.RootNodeIds.append(this_id)

        # Recurse to children
        children = OrderedDict()
        for child in node.children(skip_not_present=self.skip_not_present):
            if not isinstance(child, AddressableNode):
                continue
            child_id = self.visit_addressable_node(child, this_id)
            child_ids.append(child_id)
            children[child_id] = child
            

        # Generate page for this node
        #self.create_regfile_list(this_id, node, children)
        #self.create_regmap_list(node, 0)
        #self.create_registers_info(node, 0)
        #print(this_id)
        return this_id

    #####################################################################
    # Create the regfile list for all regiters
    #####################################################################
    def create_regfile_list(self, node: Node, root_id: int): 
        regfile_map_strg = {}
        regfile_map_strg['Name'] = "%s %s" % ((root_id+1),self.get_name(node))
        regfile_map_strg['Absolute_address'] = self.get_reg_absolute_address(node)
        regfile_map_strg['Base_offset'] = self.get_reg_offset(node)
        regfile_map_strg['Size'] = self.get_addrmap_size(node)
        regfile_map_strg['Desc'] = self.get_node_html_desc(node)

        #print("=====================================")
        #print(self.get_reg_absolute_address(node))
        #print("=====================================")

        #print(regfile_map_strg)
        self.pdf_create.create_regfile_info(regfile_map_strg)

        #print(node.__dict__)
        #print(node.inst)
        for regfile_id, regfile in enumerate(node.children()):
            regfile_list_strg = {}

            child_name = self.get_inst_name(regfile)
            #print(self.get_inst_name(regfile))

            child = node.get_child_by_name(child_name)
            #print(self.get_child_addr_digits(regfile))
            #print(regfile.inst.addr_offset)

            # Reserved addresses at the start of the address map
            if regfile_id == 0 and regfile.inst.addr_offset != 0:
                offset_range = "%s till %s" % ((self.format_address(0)),self.format_address(regfile.inst.addr_offset-1))
                regfile_list_strg['Offset']     = offset_range 
                regfile_list_strg['Identifier'] = "-" 
                regfile_list_strg['Name']       = "-"
                self.pdf_create.create_regfile_list_info(regfile_list_strg, 1)
                #print(offset_range)
            # Reserved addresses in between the address map - for single space
            elif (regfile_id != 0) and (regfile_previous.inst.addr_offset + 2*regfile_previous.total_size) == regfile.inst.addr_offset:
                regfile_list_strg['Offset']     = self.format_address(regfile_previous.inst.addr_offset + regfile_previous.total_size)
                regfile_list_strg['Identifier'] = "-" 
                regfile_list_strg['Name']       = "-"
                self.pdf_create.create_regfile_list_info(regfile_list_strg, 1)
            # Reserved addresses in between the address map - for a range fo free spaces
            elif (regfile_id != 0) and (regfile_previous.inst.addr_offset + regfile_previous.total_size) < regfile.inst.addr_offset:
                start_addr = regfile_previous.inst.addr_offset + regfile_previous.total_size

                index = 0
                while((regfile_previous.inst.addr_offset + regfile_previous.total_size + index) < regfile.inst.addr_offset):
                    index = index + regfile.total_size
                    
                end_addr = regfile_previous.inst.addr_offset + regfile_previous.total_size + index

                offset_range = "%s till %s" % ((self.format_address(start_addr)),self.format_address(end_addr-1))
                regfile_list_strg['Offset']     = offset_range 
                regfile_list_strg['Identifier'] = "-" 
                regfile_list_strg['Name']       = "-"
                self.pdf_create.create_regfile_list_info(regfile_list_strg, 1)

            # Normal registers in the address map
            regfile_list_strg['Offset']     = self.format_address(regfile.inst.addr_offset) 
            regfile_list_strg['Identifier'] = self.get_inst_name(regfile)
            regfile_list_strg['Id']         = "%s.%s" % ((root_id+1),(regfile_id+1))
            regfile_list_strg['Name']       = self.get_inst_name(regfile)

            #print(regfile_list_strg)
            self.pdf_create.create_regfile_list_info(regfile_list_strg, 0)

            regfile_previous = regfile
        
        self.pdf_create.dump_regfile_list_info()

    #####################################################################
    # Create the regmap list for all regiters
    #####################################################################
    def create_regmap_list(self, node: Node, root_id: int, regfile_id: int):
        addrmap_strg = {}
        # set the required variable 
        self.set_address_width(node)
        self.set_base_address(node)

        addrmap_strg['Name'] = "%s.%s %s" % ((root_id+1),(regfile_id+1),self.get_name(node))
        addrmap_strg['Base_address'] = self.get_base_address(node)
        addrmap_strg['Size'] = self.get_addrmap_size(node)
        addrmap_strg['Desc'] = self.get_node_html_desc(node)
        self.pdf_create.create_regmap_info(addrmap_strg)

        # Create a list of all registers for the map
        for reg_id, reg in enumerate(node.children()):
            addrmap_reg_list_strg = {}
            
            # Reserved addresses at the start of the address map
            if reg_id == 0 and reg.address_offset != 0:
                offset_range = "%s till %s" % ((self.format_address(0)),self.format_address(reg.address_offset-1))
                addrmap_reg_list_strg['Offset']     = offset_range 
                addrmap_reg_list_strg['Identifier'] = "-" 
                addrmap_reg_list_strg['Name']       = "-"
                self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 1)

            # Reserved addresses in between the address map - for single space
            elif (reg_id != 0) and (reg_previous.address_offset + 2*reg_previous.total_size) == reg.address_offset:
                addrmap_reg_list_strg['Offset']     = self.format_address(reg_previous.address_offset + reg_previous.total_size)
                addrmap_reg_list_strg['Identifier'] = "-" 
                addrmap_reg_list_strg['Name']       = "-"
                self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 1)

            # Reserved addresses in between the address map - for a range fo free spaces
            elif (reg_id != 0) and (reg_previous.address_offset + reg_previous.total_size) < reg.address_offset:
                start_addr = reg_previous.address_offset + reg_previous.total_size

                index = 0
                while((reg_previous.address_offset + reg_previous.total_size + index) < reg.address_offset):
                    index = index + reg.total_size
                    
                end_addr = reg_previous.address_offset + reg_previous.total_size + index

                offset_range = "%s till %s" % ((self.format_address(start_addr)),self.format_address(end_addr-1))
                addrmap_reg_list_strg['Offset']     = offset_range 
                addrmap_reg_list_strg['Identifier'] = "-" 
                addrmap_reg_list_strg['Name']       = "-"
                self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 1)

            # Normal registers in the address map
            addrmap_reg_list_strg['Offset']     = self.format_address(reg.address_offset) 
            addrmap_reg_list_strg['Identifier'] = self.get_inst_name(reg)
            addrmap_reg_list_strg['Id']         = "%s.%s.%s" % ((root_id+1),(regfile_id+1),(reg_id+1))
            addrmap_reg_list_strg['Name']       = self.get_inst_name(reg)
            self.pdf_create.create_reg_list_info(addrmap_reg_list_strg, 0)

            # Store previous item
            reg_previous = reg

        self.pdf_create.dump_reg_list_info()

    #####################################################################
    # Create the regiters info
    #####################################################################
    def create_registers_info(self, node: AddrmapNode, root_id: int, regfile_id: int): 
        # Traverse all the registers for separate register(s) section
        for reg_id, reg in enumerate(node.registers()):
            registers_strg = {}
            registers_strg['Name'] = "%s.%s.%s %s" % ((root_id+1),(regfile_id+1),(reg_id+1),self.get_inst_name(reg))
            registers_strg['Absolute_address'] = self.get_reg_absolute_address(reg)
            registers_strg['Base_offset'] = self.get_reg_offset(reg)
            registers_strg['Reset'] = self.get_reg_reset(reg)
            registers_strg['Access'] = self.get_reg_access(reg)
            registers_strg['Size'] = self.get_reg_size(reg)
            registers_strg['Desc'] = self.get_desc(reg)

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
        s = s.replace("  "," ")
        return s

    def get_node_html_desc(self, node: Node, increment_heading: int=0) -> 'Optional[str]':
        """
        Wrapper function to get HTML description
        If no description, returns None

        Performs the following transformations on top of the built-in HTML desc
        output:
        - Increment any heading tags
        - Transform img paths that point to local files. Copy referenced image to output
        """

        desc = node.get_html_desc(self.markdown_inst)
        if desc is None:
            return desc

        # Keep HTML semantically correct by promoting heading tags if desc ends
        # up as a child of existing headings.
        if increment_heading > 0:
            def heading_replace_callback(m: 're.Match') -> str:
                new_heading = "<%sh%d>" % (
                    m.group(1),
                    min(int(m.group(2)) + increment_heading, 6)
                )
                return new_heading
            desc = re.sub(r'<(/?)[hH](\d)>', heading_replace_callback, desc)

        # Transform image references
        # If an img reference points to a file on the local filesystem, then
        # copy it to the output and transform the reference
        if increment_heading > 0:
            def img_transform_callback(m: 're.Match') -> str:
                dom = xml.dom.minidom.parseString(m.group(0))
                img_src = dom.childNodes[0].attributes["src"].value

                if os.path.isabs(img_src):
                    # Absolute local path, or root URL
                    pass
                elif re.match(r'(https?|file)://', img_src):
                    # Absolute URL
                    pass
                else:
                    # Looks like a relative path
                    # See if it points to something relative to the source file
                    path = self.try_resolve_rel_path(node.inst.def_src_ref, img_src)
                    if path is not None:
                        img_src = path

                if os.path.exists(img_src):
                    with open(img_src, 'rb') as f:
                        md5 = hashlib.md5(f.read()).hexdigest()
                    new_path = os.path.join(
                        self.output_dir, "content",
                        "%s_%s" % (md5[0:8], os.path.basename(img_src))
                    )
                    shutil.copyfile(img_src, new_path)
                    dom.childNodes[0].attributes["src"].value = os.path.join(
                        "content",
                        "%s_%s" % (md5[0:8], os.path.basename(img_src))
                    )
                    return dom.childNodes[0].toxml()

                return m.group(0)

            desc = re.sub(r'<\s*img.*/>', img_transform_callback, desc)
        return desc


    def get_enum_html_desc(self, enum_member) -> str: # type: ignore
        s = enum_member.get_html_desc(self.markdown_inst)
        if s:
            return s
        else:
            return ""

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

    def get_child_addr_digits(self, node: AddressableNode) -> int:
        return math.ceil(math.log2(node.size) / 4)

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
        address_width = 32; #change addrwidth heres

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
        elif no_of_nib == 8:
            format_number = no_of_nib + 1
        # 8bit address     
        else:
            format_number = no_of_nib

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

