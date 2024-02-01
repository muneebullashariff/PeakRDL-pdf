# PeakRDL-pdf
Generate PDF Registers Description document from compiled SystemRDL input  

## Install from Github using pip
```
mkdir path_to_folder  
cd path_to_folder  
git clone https://github.com/muneebullashariff/PeakRDL-pdf.git  
cd PeakRDL-pdf
pip3 install -e .      
# The following is only necessary if using -e above. if not using -e, it will be installed automaticaly
pip3 install reportlab
```
Advantages of this approach are:  
1. You can install package in your home projects directory.
2. Package includes .git dir, so it's regular Git repository. You can push to your fork right away.

--------------------------------------------------------------------------------

## Exporter Usage
### Standalone usage
Pass the elaborated output of the [SystemRDL Compiler](https://github.com/muneebullashariff/systemrdl-compiler)
to the exporter.

```python
import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.pdf import PDFExporter

rdlc = RDLCompiler()

try:
    rdlc.compile_file("path/to/my.rdl")
    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)

exporter = PDFExporter()
exporter.export(root, "test.pdf")
```
### As a peakrdl export plugin
The PeakRDL tool suite has a plugin infrastructure got both input and output plugins.
PeakRDL-pdf can be used an export plugin:
```
cd examples
python3 -m peakrdl pdf -o test.pdf input_files/atxmega_spi.rdl
```
In this mode, two more flags are supported:  
`--use-uppercase-inst-name`  
    If True, (default) then all instance names will be Uppercase   
`--template-path`  
    You need to supply a Python file containing the definition of two functions: `myFirstPage` and `myLaterPages`.  
    This allows customizing the PDF output.  
    If not given, peakrdl-pdf will use the default implementation.  

```
cd examples
python3 -m peakrdl pdf -o test.pdf --template-path front_pg_later_pgs_info.py input_files/atxmega_spi.rdl
```
--------------------------------------------------------------------------------

## Reference

### `pdfExporter.export(node, path, **kwargs)`
Perform the export!

**Parameters**

* `node`
    * Top-level node to export. Can be the top-level `RootNode` or any internal `AddrmapNode`.
* `path`
    * Output file.

**Optional Parameters**

* `use_uppercase_inst_name`
    * If True, (default) then all instance names will be Uppercase 
    * If False, then all the instance names will be Lowercase
* `onFirstPage`  
    The name of a Python function to render the first page
* `onLaterPages`  
    The name of a python function to render all other pages
