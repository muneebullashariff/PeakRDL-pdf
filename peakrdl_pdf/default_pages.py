import os
import datetime
from reportlab.lib import colors

# Docuement text color
doc_color  = colors.HexColor(0x24001e)

############################################################################
# Define the fixed features of the first page of the document
############################################################################
Example_logo = os.path.join(os.path.dirname(os.path.realpath(__file__)), "example_logo.png")

def myFirstPage(canvas, doc):
    canvas.saveState()

    # Example Logo
    canvas.drawImage(Example_logo,405,720,width=140,height=60,preserveAspectRatio=True,mask='auto') 

    # Example FPGA
    text_color = colors.HexColor(0x18325e)
    canvas.setFillColor(text_color)
    canvas.setFont('Helvetica-Bold', 22)
    canvas.drawString(380, 620, 'Example')

    canvas.setFont('Helvetica', 19)
    canvas.drawString(478, 620, 'FPGA ')

    # Line
    line_color = colors.HexColor(0x4d82bb)
    canvas.setStrokeColor(line_color)
    canvas.setLineWidth(1.2)
    canvas.line(60,610,532,610)

    # Example Register Specification 
    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Bold', 25)
    canvas.drawString(181, 500, ' Example Registers Specification')

    # Date of creation
    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Roman', 14)
    # Get the today's date (yyyy-Month-dd)
    today_date = datetime.date.today().strftime('%Y-%b-%d')
    canvas.drawString(460, 420, today_date)
         
    # First page Footer
    canvas.setFillColor(colors.red)
    canvas.setFont('Times-Roman', 8)
    canvas.drawString(265, 110, 'Example Corporation')
    
    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Bold', 8)
    canvas.drawString(250, 100, 'Proprietary and Confidential')

    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Roman', 8)
    strg = "Copyright \xa9 " + datetime.date.today().strftime('%Y') + "  - Example Corporation, All Rights Reserved"
    canvas.drawString(200, 90, strg)

    canvas.restoreState()

############################################################################
# Since we want pages after the first to look different from the first 
# we define an alternate layout for the fixed features of the other pages.
# Note that the two functions use the pdfgen level canvas operations to 
# paint the annotations for the pages.
############################################################################
def myLaterPages(canvas, doc):
    canvas.saveState()

    # Header Example logo
    canvas.drawImage(Example_logo,500,790,width=70,height=30,preserveAspectRatio=True,mask='auto') 

    # Footer line
    line_color = colors.HexColor(0x4d82bb)
    canvas.setStrokeColor(line_color)
    canvas.setLineWidth(0.8)
    canvas.line(60,70,532,70)

    # Footer date (yyyy-mm-dd)
    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Roman', 10)
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    canvas.drawString(60, 55, today_date)

    # Footer Info
    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Bold', 8)
    canvas.drawString(260, 60, 'Proprietary and Confidential')

    canvas.setFillColor(doc_color)
    canvas.setFont('Times-Roman', 8)
    strg = "Copyright \xa9 " + datetime.date.today().strftime('%Y') + " - Example Corporation, All Rights Reserved"
    canvas.drawString(200, 50, strg)

    # Footer Page number 
    canvas.setFont('Times-Roman', 10)
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.drawString(500, 55, text)

    canvas.restoreState()

