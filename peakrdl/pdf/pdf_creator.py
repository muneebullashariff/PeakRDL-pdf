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
        global doc, elements, styleSheet, table_data, doc_color

        # Create the document
        doc = SimpleDocTemplate(output_file, pagesize=A4)

        # container for the 'Flowable' objects
        elements = []

        ## Table data
        table_data = []

        # Document color
        doc_color = dimgrey

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
                                      alignment=TA_CENTER,
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

        ## Actual data
        P_offset_header = Paragraph('<b>Offset</b>',styleSheet["BodyTextT"])    
        P_identifier_header = Paragraph('<b>Identifier</b>',styleSheet["BodyTextT"])    
        P_name_header = Paragraph('<b>Name</b>',styleSheet["BodyTextT"])    
        table_data.append([P_offset_header, P_identifier_header, P_name_header])

        #self.creation()
        #self.build_document()

    def create_reg_list_info(self, reg_info_dict: dict):

        P_offset = Paragraph(reg_info_dict['Offset'],styleSheet["BodyTextP"])    
        P_identifier = Paragraph(reg_info_dict['Identifier'],styleSheet["BodyTextP"])    
        P_name = Paragraph(reg_info_dict['Name'],styleSheet["BodyTextP"])    

        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])
        table_data.append([P_offset, P_identifier, P_name])

            #if key == "Offset":
            #    print("%s: %s" % (key, reg_info_dict[key]))
            #    elements.append(Paragraph(reg_info_dict[key], styleSheet["H1p"]))
            #    elements.append(Spacer(0, 0.5*inch))
            #elif key == "Identifier":
            #    print("%s: %s" % (key, reg_info_dict[key]))
            #    elements.append(Paragraph(reg_info_dict[key], styleSheet["BodyTextP"]))
            #    elements.append(Spacer(0, 0.2*inch))
            #elif key == "Name":
            #    print("%s: %s" % (key, reg_info_dict[key]))
            #    elements.append(Paragraph(('<b>Base Address : </b>' + reg_info_dict[key]), 
            #                        styleSheet["BodyTextP"]))
            #else:
            #    print("Error - Not a valid key for the addrmap register list")

    def dump_reg_list_info(self):
        
        t=Table(table_data,
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

        # Space
        elements.append(Spacer(1, 1*inch))
        
        #self.creation()
        self.build_document()

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
