import sys
import os
from systemrdl import RDLCompiler, RDLCompileError
from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from peakrdl.pdf import PDFExporter

# Ignore this. Only needed for this example
this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(this_dir, "../input_files"))

input_dir = this_dir + "/input_files/"
output_dir = this_dir + "/output_files/"

# Get the input .rdl file from the command line
input_files = sys.argv[1:]

## TODO: Need to see if the input_files are more than 1

## Compile and elaborate the input .rdl file
rdlc = RDLCompiler()

try:
    for input_file in input_files:
        input_file = input_dir + input_file 
        rdlc.compile_file(input_file)

    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)

## Generate the PDF output files
dest_pdf_fl = "test.pdf" 

exporter = PDFExporter()

exporter.export(root, 
                os.path.join(output_dir, dest_pdf_fl),
                use_uppercase_inst_name=True)

# TODO: 
# Have option to merge the pdf files or separate files
# Header and footer information 
# Optional company Logo
