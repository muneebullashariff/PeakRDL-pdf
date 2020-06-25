from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import white, black, grey, dimgrey, darkgrey, darkslategrey
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
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
_baseFontNameB = tt2ps(_baseFontName,1,0)
_baseFontNameI = tt2ps(_baseFontName,0,1)
_baseFontNameBI = tt2ps(_baseFontName,1,1)

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
        global table_data_reg_list, table_data_field_list

        # Create the document
        doc = SimpleDocTemplate(output_file, pagesize=A4)

        # container for the 'Flowable' objects
        elements = []

        ## Table data
        table_data_reg_list = []
        table_data_field_list = []

        # Document color
        #doc_color = darkgrey
        #doc_color = dimgrey
        #doc_color = black
        doc_color  = colors.HexColor(0x040003)
        doc_color  = colors.HexColor(0x0f000d)
        doc_color  = colors.HexColor(0x24001e)

        # Create the style sheet
        styleSheet = getSampleStyleSheet()

        # Add more custom styles
        self.add_more_styles()

    # Creating the style sheet Template
    def add_more_styles(self):


        styleSheet.add(ParagraphStyle(name='Header1P',
                                      fontName=_baseFontNameB,
                                      textColor=doc_color,
                                      fontSize=30,
                                      leading=12),
                       alias='H1p')
        
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

        styleSheet.add(ParagraphStyle(name='Heading3P',
                                      fontName=_baseFontName,
                                      textColor=doc_color,
                                      fontSize=16,
                                      leading=12),
                                      #parent=styleSheet['Normal'],
                                      #fontName = _baseFontNameBI,
                                      #fontSize=12,
                                      #leading=14,
                                      #spaceBefore=12,
                                      #spaceAfter=6),
                       alias='H3p')

        return
    
    # write the document to disk
    def build_document(self):
        doc.build(elements)

    def create_addrmap_info(self, map_info_dict: dict):
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
            elif key == "Size":
                elements.append(Paragraph(('<b>Size(bytes) : </b>' + map_info_dict[key]), 
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
        table_data_reg_list.append([P_offset_header, P_identifier_header, P_name_header])

    def create_register_info(self, reg_info_dict: dict):
        for key in reg_info_dict:
            if key == "Name":
                elements.append(Paragraph(reg_info_dict[key], styleSheet["H1p"]))
                elements.append(Spacer(0, 0.5*inch))
            elif key == "Desc":
                elements.append(Paragraph(reg_info_dict[key], styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            elif key == "Absolute_address":
                elements.append(Paragraph(('<b>Absolute Address : \t</b>' + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Base_offset":
                elements.append(Paragraph(('<b>Base Offset : </b>' + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Access":
                elements.append(Paragraph(('<b>Access : </b>' + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Reset":
                elements.append(Paragraph(('<b>Reset : </b>' + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
            elif key == "Size":
                elements.append(Paragraph(('<b>Size(bytes) : </b>' + reg_info_dict[key]), 
                                    styleSheet["BodyTextP"]))
                elements.append(Spacer(0, 0.2*inch))
            else:
                print("Error - Not a valid key (%s) for the register" %key)

        # Add the Fields list
        elements.append(Paragraph('Fields List', styleSheet["H2p"]))
        elements.append(Spacer(0, 0.4*inch))

        ## Actual Header data
        P_offset_header = Paragraph('<b>Bits</b>',styleSheet["BodyTextT"])    
        P_identifier_header = Paragraph('<b>Identifier</b>',styleSheet["BodyTextT"])    
        P_access_header = Paragraph('<b>Access</b>',styleSheet["BodyTextT"])    
        P_reset_header = Paragraph('<b>Reset</b>',styleSheet["BodyTextT"])    
        P_name_header = Paragraph('<b>Name / Description </b>',styleSheet["BodyTextT"])    


        # Clear any previous values
        table_data_field_list.clear()

        table_data_field_list.append([P_offset_header, 
                                      P_identifier_header, 
                                      P_access_header, 
                                      P_reset_header,
                                      P_name_header])

    ###
    # Create the register's list info
    ###
    def create_reg_list_info(self, reg_info_dict: dict, is_reserved: bool):

        P_offset = Paragraph(reg_info_dict['Offset'],styleSheet["BodyTextP"])    

        if is_reserved:
            P_identifier = Paragraph(reg_info_dict['Identifier'],styleSheet["BodyTextP"])    
        else:
            link = "<a href=\"#" + (reg_info_dict['Name']).replace(" ","") + "\" color=\"blue\">"
            P_identifier = Paragraph((link + reg_info_dict['Identifier'] + "</a>"),styleSheet["BodyTextP"])    

        P_name = Paragraph(reg_info_dict['Name'],styleSheet["BodyTextP"])    

        table_data_reg_list.append([P_offset, P_identifier, P_name])

    ###
    # Create the field's list info 
    ###
    def create_fields_list_info(self, field_info_dict: dict):

        # Bits 
        P_bits = Paragraph(field_info_dict['Bits'],styleSheet["BodyTextP"])    

        # Identifier
        P_identifier = Paragraph(field_info_dict['Identifier'],styleSheet["BodyTextP"])    

        # Access
        P_access = Paragraph(field_info_dict['Access'],styleSheet["BodyTextP"])    

        # Reset 
        P_reset = Paragraph(field_info_dict['Reset'],styleSheet["BodyTextP"])    

        # Name
        P_name = Paragraph(field_info_dict['Name'],styleSheet["BodyTextP"])    

        # Description
        P_desc = Paragraph(field_info_dict['Description'],styleSheet["BodyTextP"])    

        table_data_field_list.append([P_bits, 
                                      P_identifier, 
                                      P_access,
                                      P_reset,
                                      [P_name,P_desc],
                                      ])

        # TODO: Give the the coloumn width for fields column
        ##MSHA
        #self.dump_field_list_info()

    def dump_reg_list_info(self):

        t=Table(table_data_reg_list,
                splitByRow=1,
                repeatRows=1,
                style=[
                    ('GRID',(0,0),(-1,-1),0.5,doc_color),
                    ('LINEABOVE',(0,1),(-1,1),1,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor(0xD9D9D9))
                    ])
                            #('BOX',(0,0),(1,-1),2,colors.red),
                            #('LINEBEFORE',(2,1),(2,-2),1,colors.blue),
                            #('BOX',(0,0),(-1,-1),2,colors.black),
                            #('GRID',(0,0),(-1,-1),0.5,colors.black),
                            #('VALIGN',(3,0),(3,0),'BOTTOM'),
                            #('BACKGROUND',(3,1),(3,1),colors.khaki),
                            #('ALIGN',(3,1),(3,1),'CENTER'),
                            #('BACKGROUND',(3,2),(3,2),colors.beige),
                            #('ALIGN',(3,2),(3,2),'LEFT'),
                            #])

        # Table 1
        elements.append(t)

        
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="SlaveSelectRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="MasterTriggerRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="ErrorAddressRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="StatusInformationRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="GlobalControlRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph('<a name="ReceiveDataRegister"/>Link test', styleSheet["H2p"]))
        elements.append(Spacer(1, 1*inch))

        # Space
        elements.append(Spacer(1, 1*inch))
        
    def dump_field_list_info(self):

        t=Table(table_data_field_list,
                colWidths=[45,80,50,70,190],
                splitByRow=1,
                repeatRows=1,
                style=[
                    ('GRID',(0,0),(-1,-1),0.5,doc_color),
                    ('LINEABOVE',(0,1),(-1,1),1,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor(0xD9D9D9)),
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('VALIGN',(0,1),(-1,-1),'MIDDLE'),
                    ])
                            #('BOX',(0,0),(1,-1),2,colors.red),
                            #('LINEBEFORE',(2,1),(2,-2),1,colors.blue),
                            #('BOX',(0,0),(-1,-1),2,colors.black),
                            #('GRID',(0,0),(-1,-1),0.5,colors.black),
                            #('VALIGN',(3,0),(3,0),'BOTTOM'),
                            #('BACKGROUND',(3,1),(3,1),colors.khaki),
                            #('ALIGN',(3,1),(3,1),'CENTER'),
                            #('BACKGROUND',(3,2),(3,2),colors.beige),
                            #('ALIGN',(3,2),(3,2),'LEFT'),
                            #])

        # Table 1
        elements.append(t)

        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="SlaveSelectRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="MasterTriggerRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="ErrorAddressRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="StatusInformationRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="GlobalControlRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))
        #elements.append(Paragraph('<a name="ReceiveDataRegister"/>Link test', styleSheet["H2p"]))
        #elements.append(Spacer(1, 7*inch))

        # Space
        elements.append(Spacer(1, 1*inch))


    def creation(self):

        # Image
        I = Image('muneeb.jpg')
        I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
        I.drawWidth = 1.25*inch

        # Paragraphs
        P0 = Paragraph('''
        A paragraph
        1''',
        styleSheet["BodyText"])

        P = Paragraph(''' The ReportLab Left
        Logo
        Image''',
        styleSheet["BodyText"])

        ## Some Info
        elements.append(P0)
        elements.append(P)

        ## Actual data
        data= [['A', 'B', 'C', P0, 'D'],
               ['00', '01', '02', [I,P], '04'],
               ['10', '11', '12', [P,I], '14'],
               ['20', '21', '22', '23', '24'],
               ['30', '31', '32', '33', '34'],
               ['40', '41', '42', '43', '44']]

        t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
                            ('BOX',(0,0),(1,-1),2,colors.red),
                            ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                            ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                            ('BACKGROUND', (0, 0), (0, 1), colors.pink),
                            ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                            ('BACKGROUND', (2, 2), (2, 3), colors.orange),
                            ('BOX',(0,0),(-1,-1),2,colors.black),
                            ('GRID',(0,0),(-1,-1),0.5,colors.black),
                            ('VALIGN',(3,0),(3,0),'BOTTOM'),
                            ('BACKGROUND',(3,0),(3,0),colors.limegreen),
                            ('BACKGROUND',(3,1),(3,1),colors.khaki),
                            ('ALIGN',(3,1),(3,1),'CENTER'),
                            ('BACKGROUND',(3,2),(3,2),colors.beige),
                            ('ALIGN',(3,2),(3,2),'LEFT'),
                            ])
        #t._argW[3]=1.5*inch

        # Table 1
        elements.append(t)

        # Space
        elements.append(Spacer(1, 1*inch))
        elements.append(t)
