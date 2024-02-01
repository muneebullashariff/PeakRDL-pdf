import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


with open(os.path.join("peakrdl_pdf", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setuptools.setup(
    name="peakrdl-pdf",
    version=version,
    author="Muneeb Ulla Shariff",
    description="Generate PDF Registers Description document from compiled SystemRDL input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muneebullashariff/PeakRDL-pdf",
    packages=['peakrdl_pdf'],
    include_package_data=True,
    package_data={
        'peakrdl_pdf': ['example_logo.png'],
    },
    install_requires=[
        "systemrdl-compiler>=1.12.0",
        "reportlab"
    ],
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ),
    project_urls={
        "Source": "https://github.com/muneebullashariff/PeakRDL-pdf",
        "Tracker": "https://github.com/muneebullashariff/PeakRDL-pdf/issues"
    },
    entry_points = {
        'peakrdl.exporters': [
            'pdf = peakrdl_pdf.__peakrdl__:Exporter'
        ]
    }
)
