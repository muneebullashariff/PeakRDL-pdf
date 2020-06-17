# PeakRDL-pdf
Generate PDF Registers Description document from compiled SystemRDL input  

## Install from Github using pip
mkdir path_to_folder  
cd path_to_folder  
git clone https://github.com/muneebullashariff/PeakRDL-pdf.git  
cd to PeakRDL-pdf   
pip install -e .      


Advantages of this approach are:  
1 - You can install package in your home projects directory.   
2 - Package includes .git dir, so it's regular Git repository. You can push to your fork right away.    

--------------------------------------------------------------------------------

## Exporter Usage
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
