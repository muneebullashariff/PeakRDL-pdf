# PeakRDL-pdf
Generate PDF Registers Description document from compiled SystemRDL input  

## Install from Github using pip

```shell
cd to PeakRDL-pdf   
pip3 install -e .      

pip3 install reportlab
pip3 install python-markdown-math

cp simsun.ttf C:\Users\Your_Name\AppData\Local\Programs\Python\Python310\Lib\site-packages\reportlab\fonts

cd peakrdl_examples
python3 pdf_parser.py basic.rdl
```

--------------------------------------------------------------------------------
