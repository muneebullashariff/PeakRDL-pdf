import sys
import os
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.uvm import UVMExporter
from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode

## Compile and elaborate the input .rdl file
rdlc = RDLCompiler()

src_rdl_fl = "tru_cfg.rdl"

try:
    rdlc.compile_file(src_rdl_fl)
    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)

## Generate the UVM output files
# Export as package or include files
export_as_package_l = False
if export_as_package_l:
    dest_uvm_fl = "tru_registers_pkg_uvm.sv" 
else:
    dest_uvm_fl = "tru_registers_uvm.sv" 

exporter = UVMExporter()

exporter.export(root, 
                dest_uvm_fl, 
                export_as_package=export_as_package_l, 
                use_uvm_factory=True, 
                use_uvm_reg_enhanced=False,
                use_uppercase_inst_name=True,
                reuse_class_definitions=False)

strg = []
strg.append("-------------------------")

# Traverse all the address maps
for node in root.descendants(in_post_order=True):
    if isinstance(node, AddrmapNode):
        print(exporter._get_inst_map_name(node))
        print(node.get_property("name"))
        desc = node.get_property("desc")
        print(desc.replace("\n"," "))

    # Traverse all the registers
    for reg in node.registers():
        if isinstance(reg, RegNode):
            strg.append(exporter._get_inst_name(reg))
            #strg.append(exporter._get_reg_access(reg))


            # Reverse the fields order - MSB first
            strg_field = []
            for field in reg.fields():
                if isinstance(field, FieldNode):
                    strg_field.append(field)

            strg_field.reverse()

            # Traverse all the fields
            for field in strg_field:
                strg.append(exporter._get_inst_name(field))
                strg.append(exporter._get_field_access(field))

            strg.append("-------------------------")

for k in strg:
    print(k)
