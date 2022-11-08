from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, inch, mm
from reportlab.platypus import Image, Paragraph, PageBreak, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.platypus.tableofcontents import TableOfContents, SimpleIndex
from reportlab.lib.colors import white, black, grey, dimgrey, darkgrey, darkslategrey
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
from reportlab.rl_config import defaultPageSize
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from peakrdl_examples import myFirstPage, myLaterPages

from reportlab.rl_config import canvas_basefontname as _baseFontName, \
                                underlineWidth as _baseUnderlineWidth, \
                                underlineOffset as _baseUnderlineOffset, \
                                underlineGap as _baseUnderlineGap, \
                                strikeWidth as _baseStrikeWidth, \
                                strikeOffset as _baseStrikeOffset, \
                                strikeGap as _baseStrikeGap, \
                                spaceShrinkage as _spaceShrinkage, \
                                platypus_link_underline as _platypus_link_underline, \
                                hyphenationLang as _hyphenationLang, \
                                hyphenationMinWordLength as _hyphenationMinWordLength, \
                                uriWasteReduce as _uriWasteReduce, \
                                embeddedHyphenation as _embeddedHyphenation

PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]

_baseFontNameB = tt2ps(_baseFontName,1,0)
_baseFontNameI = tt2ps(_baseFontName,0,1)
_baseFontNameBI = tt2ps(_baseFontName,1,1)

############################################################################
# Class for implementing the afterFlowable method
# which is used for registering the TOC enteries
############################################################################
class MySimpleDocTemplate(SimpleDocTemplate):

    # Used for registering the required items
    # into the table of contents
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name

            if style == 'Header1P':
                key = 'h1p-%s' % self.seq.nextf('Header1P')
                self.canv.bookmarkPage(key, fit="FitH")
                self.notify('TOCEntry', (0, text, self.page, key))

            elif style == 'Header1PS':
                # Pad spaces  
                text = ' &nbsp;'*3 + text
                key = 'h1ps-%s' % self.seq.nextf('Header1PS')
                self.canv.bookmarkPage(key, fit="FitH")
                self.notify('TOCEntry', (1, text, self.page, key))

############################################################################
# Main Pdf creater class with required properties
# for creating the pdf contents and adding the data 
# into the pdf document
############################################################################
class PDFCreator:

    def __init__(self, output_file: str, **kwargs):
        """
        Constructor for the PDF Creator class
        """

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        # Define variables used during creation
        global doc, elements, styleSheet, doc_color
        global table_data_regfile_list,table_data_reg_list, table_data_field_list, toc

        # Create the document
        doc = MySimpleDocTemplate(output_file, pagesize=A4)

        # container for the 'Flowable' objects
        elements = []

        ## Table data
        table_data_regfile_list = []
        table_data_reg_list = []
        table_data_field_list = []

        # Document color
        #doc_color = darkgrey
        #doc_color = dimgrey
        #doc_color = black
        doc_color  = colors.HexColor(0x24001e)

        # Create the style sheet
        styleSheet = getSampleStyleSheet()

        # Add more custom styles
        self.add_more_styles()

        # First page
        elements.append(PageBreak())

        # TOC
        h1 = ParagraphStyle(name = 'Heading1',
                            fontName=_baseFontNameB,
                            textColor=doc_color,
                            fontSize = 14,
                            spaceBefore=10,
                            leading = 16)

        h2 = ParagraphStyle(name = 'Heading2',
                            fontName=_baseFontName,
                            textColor=doc_color,
                            fontSize = 12,
                            leading = 14)

        # Table of contents 
        toc = TableOfContents()
        toc.levelStyles = [h1, h2]

        elements.append(Paragraph('Table of Contents', styleSheet["Header1Toc"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(toc)
        elements.append(PageBreak())

    ############################################################################
    # Creating the style sheet Template
    ############################################################################
    def add_more_styles(self):

        styleSheet.add(ParagraphStyle(name='Header1P',
                                      fontName=_baseFontNameB,
                                      textColor=doc_color,
                                      fontSize=30,
                                      leading=12),
                       alias='H1p')
        
        styleSheet.add(ParagraphStyle(name='Header1PS',
                                      fontName=_baseFontNameB,
                                      textColor=doc_color,
                                      fontSize=26,
                                      leading=12),
                       alias='H1pS')

        styleSheet.add(ParagraphStyle(name='Header1Toc',
                                      fontName=_baseFontNameB,
                                      textColor=doc_color,
                                      fontSize=30,
                                      leading=12),
                       alias='H1t')

        styleSheet.add(ParagraphStyle(name='Header2P',
                                      fontName=_baseFontNameB,
                                      textColor=doc_color,
                                      fontSize=20,
                                      leading=12),
                       alias='H2p')

        styleSheet.add(ParagraphStyle(name='BodyTextP',
                                      fontName=_baseFontName,
                                      textColor=doc_color,
                                      fontSize=10,
                                      leading=12),
                       alias='BTP')

        styleSheet.add(ParagraphStyle(name='BodyTextT',
                                      fontName=_baseFontName,
                                      textColor=doc_color,
                                      #alignment=TA_CENTER,
                                      fontSize=10,
                                      leading=12),
                       alias='BTT')

        return

    ############################################################################
    # Build the document and write it to the disk 
    ############################################################################
    def build_document(self):
        doc.multiBuild(elements, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    ############################################################################
    # Create the regfile map information
    ############################################################################
    def create_regfile_info(self, map_info_dict: dict):
        for key in map_info_dict:
            if key == "Name":
                elements.append(Paragraph(map_info_dict[key], styleSheet["H1p"]))
                elements.append(Spacer(0, 0.5*inch))
            elif key == "Desc":
                elements.append(Paragraph(map_info_dict[key], styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            elif key == "Base_address":
                elements.append(Paragraph(('<b>Base Address : </b>' + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Absolute_address":
                elements.append(Paragraph(('<b>Absolute Address: </b>' + ('&nbsp;')*2 + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Base_offset":
                elements.append(Paragraph(('<b>Base Offset : </b>' + ('&nbsp;')*13 + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Size":
                elements.append(Paragraph(('<b>Size(bytes): </b>' + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            else:
                print("Error - Not a valid key for the addrmap")
        ## Actual Header data
        P_offset_header = Paragraph('<b>Offset</b>',styleSheet["BodyTextT"])    
        P_identifier_header = Paragraph('<b>Identifier</b>',styleSheet["BodyTextT"])    
        P_name_header = Paragraph('<b>Name</b>',styleSheet["BodyTextT"])    

        # Clear any previous values
        table_data_regfile_list.clear()

        table_data_regfile_list.append([P_offset_header, P_identifier_header, P_name_header])   
              
    ############################################################################
    # Create the address map information
    ############################################################################
    def create_addrmap_info(self, map_info_dict: dict):
        for key in map_info_dict:
            if key == "Name":
                elements.append(Paragraph(map_info_dict[key], styleSheet["H1p"]))
                elements.append(Spacer(0, 0.5*inch))
            elif key == "Desc":
                elements.append(Paragraph(map_info_dict[key], styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            elif key == "Base_address":
                elements.append(Paragraph(('<b>Base Address: </b>' + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Size":
                elements.append(Paragraph(('<b>Size(bytes): </b>' + map_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            else:
                print("Error - Not a valid key for the addrmap")

        # Add the Register list
        elements.append(Paragraph('Registers List', styleSheet["H2p"]))
        elements.append(Spacer(0, 0.4*inch))

        ## Actual Header data
        P_offset_header = Paragraph('<b>Offset</b>',styleSheet["BodyTextT"])    
        P_identifier_header = Paragraph('<b>Identifier</b>',styleSheet["BodyTextT"])    
        P_name_header = Paragraph('<b>Name</b>',styleSheet["BodyTextT"])    

        # Clear any previous values
        table_data_reg_list.clear()

        table_data_reg_list.append([P_offset_header, P_identifier_header, P_name_header])

    ############################################################################
    # Create the register information  
    ############################################################################
    def create_register_info(self, reg_info_dict: dict):
        for key in reg_info_dict:
            if key == "Name":
                tag_id = "<a name=\"" +  (reg_info_dict[key]).replace(" ","") + "\"/>"
                dummy = "" # done so that the jump doesn't mask the required data
                elements.append(Paragraph((tag_id + dummy), styleSheet["BodyTextP"]))
                elements.append(Paragraph(reg_info_dict[key], styleSheet["H1pS"]))
                elements.append(Spacer(0, 0.5*inch))
            elif key == "Desc1":
                elements.append(Paragraph(reg_info_dict[key], styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            elif key == "Desc2":
                elements.append(Paragraph(reg_info_dict[key], styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            elif key == "Absolute_address":
                elements.append(Paragraph(('<b>Absolute Address: </b>' + ('&nbsp;')*2 + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Base_offset":
                elements.append(Paragraph(('<b>Base Offset: </b>' + ('&nbsp;')*13 + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Reset":
                elements.append(Paragraph(('<b>Reset: </b>' + ('&nbsp;')*23 + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Access":
                elements.append(Paragraph(('<b>Access: </b>' + ('&nbsp;')*20 + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Size":
                elements.append(Paragraph(('<b>Size(bytes): </b>' + ('&nbsp;')*14 + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            else:
                print("Error - Not a valid key (%s) for the register" %key)

        # Add the Fields list
        elements.append(Paragraph('Fields List', styleSheet["H2p"]))
        elements.append(Spacer(0, 0.4*inch))

        ## Actual Header data
        P_offset_header     = Paragraph('<b>Bits</b>',styleSheet["BodyTextT"])    
        P_identifier_header = Paragraph('<b>Identifier</b>',styleSheet["BodyTextT"])    
        P_access_header     = Paragraph('<b>Access</b>',styleSheet["BodyTextT"])    
        P_reset_header      = Paragraph('<b>Reset</b>',styleSheet["BodyTextT"])    
        P_name_header       = Paragraph('<b>Name / Description </b>',styleSheet["BodyTextT"])    


        # Clear any previous values
        table_data_field_list.clear()

        table_data_field_list.append([P_offset_header, 
                                      P_identifier_header, 
                                      P_access_header, 
                                      P_reset_header,
                                      P_name_header])
    ############################################################################
    # Create the reglist's list info
    ############################################################################
    def create_regfile_list_info(self, reglist_info_dict: dict, is_reserved: bool):
        # Offset
        P_offset = Paragraph(reglist_info_dict['Offset'],styleSheet["BodyTextP"])    

        # Identifier
        if is_reserved:
            P_identifier = Paragraph(reglist_info_dict['Identifier'],styleSheet["BodyTextP"])    
        else:
            # <a href="#ID" color="blue"> Text </a>
            link = '<a href="#%s" color="blue">' % (reglist_info_dict['Id'] + (reglist_info_dict['Name']).replace(" ",""))
            P_identifier = Paragraph((link + reglist_info_dict['Identifier'] + "</a>"),styleSheet["BodyTextP"])    

        # Name
        P_name = Paragraph(reglist_info_dict['Name'],styleSheet["BodyTextP"])    

        table_data_regfile_list.append([P_offset, P_identifier, P_name])

    ############################################################################
    # Create the register's list info
    ############################################################################
    def create_reg_list_info(self, reg_info_dict: dict, is_reserved: bool):

        # Offset
        P_offset = Paragraph(reg_info_dict['Offset'],styleSheet["BodyTextP"])    

        # Identifier
        if is_reserved:
            P_identifier = Paragraph(reg_info_dict['Identifier'],styleSheet["BodyTextP"])    
        else:
            # <a href="#ID" color="blue"> Text </a>
            link = '<a href="#%s" color="blue">' % (reg_info_dict['Id'] + (reg_info_dict['Name']).replace(" ",""))
            P_identifier = Paragraph((link + reg_info_dict['Identifier'] + "</a>"),styleSheet["BodyTextP"])    

        # Name
        P_name = Paragraph(reg_info_dict['Name'],styleSheet["BodyTextP"])    

        table_data_reg_list.append([P_offset, P_identifier, P_name])

    ############################################################################
    # Create the field's list info 
    ############################################################################
    def create_fields_list_info(self, field_info_dict: dict):

        P_bits       = Paragraph(field_info_dict['Bits'],styleSheet["BodyTextP"])    
        P_identifier = Paragraph(field_info_dict['Identifier'],styleSheet["BodyTextP"])    
        P_access     = Paragraph(field_info_dict['Access'],styleSheet["BodyTextP"])    
        P_reset      = Paragraph(field_info_dict['Reset'],styleSheet["BodyTextP"])    
        P_name       = Paragraph(field_info_dict['Name'],styleSheet["BodyTextP"])    
        P_desc       = Paragraph(field_info_dict['Description'],styleSheet["BodyTextP"])    

        table_data_field_list.append([P_bits, 
                                      P_identifier, 
                                      P_access,
                                      P_reset,
                                      [P_name,P_desc],
                                      ])

    def dump_regfile_list_info(self):

        t=Table(table_data_regfile_list,
                colWidths=[120,120,200],
                splitByRow=1,
                repeatRows=1,
                style=[
                    ('GRID',(0,0),(-1,-1),0.5,doc_color),
                    ('LINEABOVE',(0,1),(-1,1),1,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor(0xD9D9D9))
                    ])

        elements.append(t)
        #elements.append(Spacer(1, 1*inch))
        
        # Page break
        elements.append(PageBreak())

    ############################################################################
    # Used for dumping the registers table info into the pdf document 
    ############################################################################
    def dump_reg_list_info(self):

        t=Table(table_data_reg_list,
                colWidths=[120,120,200],
                splitByRow=1,
                repeatRows=1,
                style=[
                    ('GRID',(0,0),(-1,-1),0.5,doc_color),
                    ('LINEABOVE',(0,1),(-1,1),1,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor(0xD9D9D9))
                    ])

        elements.append(t)
        #elements.append(Spacer(1, 1*inch))
        
        # Page break
        elements.append(PageBreak())

    ############################################################################
    # Used for dumping the fields table info into the pdf document
    ############################################################################
    def dump_field_list_info(self):

        t=Table(table_data_field_list,
                colWidths=[45,80,50,83,192],
                splitByRow=1,
                repeatRows=1,
                style=[
                    ('GRID',(0,0),(-1,-1),0.5,doc_color),
                    ('LINEABOVE',(0,1),(-1,1),1,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor(0xD9D9D9)),
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('VALIGN',(0,1),(-1,-1),'MIDDLE'),
                    ])

        elements.append(t)
        #elements.append(Spacer(1, 1*inch))

        # Page break
        elements.append(PageBreak())
