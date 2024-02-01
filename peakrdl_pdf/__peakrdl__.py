import sys
import os
import argparse
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl_pdf import PDFExporter
import importlib.util

from typing import TYPE_CHECKING

from peakrdl.plugins.exporter import ExporterSubcommandPlugin

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode

def valid_path(path):
    if not path:
        return None
    elif os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")

class Exporter(ExporterSubcommandPlugin):
    short_desc = "Generate PDF Registers Description document from compiled SystemRDL input"
    #long_desc = "..."

    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        arg_group.add_argument(
            "--use-uppercase-inst-name",
            action="store_true",
            default=False,
            help="If True, (default) then all instance names will be Uppercase. If False, then all the instance names will be Lowercase"
        )
        arg_group.add_argument(
            '--template-path',
            type=valid_path,
            default=None,
            help="Specify path for python module containing myFirstPage() and myLaterPages(). If not specified, use default methods"
        )
        pass

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        if not options.template_path:
            from peakrdl_pdf.pages import myFirstPage, myLaterPages
            exporter = PDFExporter(onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        else:
            spec = importlib.util.spec_from_file_location("peakrdl_pdf_pages", options.template_path)
            peakrdl_pdf_pages = importlib.util.module_from_spec(spec)
            sys.modules["peakrdl_pdf_pages"] = peakrdl_pdf_pages
            spec.loader.exec_module(foo)
            exporter = PDFExporter(onFirstPage=peakrdl_pdf_pages.myFirstPage, onLaterPages=peakrdl_pdf_pages.myLaterPages)

        exporter.export([top_node.parent,], options.output)
