from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from flask import make_response
import re
from mongodb_utils import get_messages

# Function to generate text
llm = ChatOpenAI()
def generate_text(texts,report_topics):
    ## Customized Prompt Template for User-Requested Topics

    summarization_template = """
    {text}

    Report should include the topics:
    User Requested: {topics}

    Using the above information which consists of the chat messages and also the extracted text, create a detailed report with a minimum of 1000 words. Ensure the report is well-structured, informative, and includes numerical data where available.

    A default Report should consist of the following topics and if there are no topics requested from the user then answer only the following topics:
    User requested topics:
        Introduction
        Business Analysis
        Market Analysis
        Founders background
        Conclusion
        And these topics too:{topics}

    If there are any additional topics requested by the user then add them too.
    The report should be answered in the below format.

    Default Format:
    Note: Only answer the topics requested by user
    <b>Introduction</b>
    • About the company:
        • Company name: [Insert company name]
        • Company description: [Describe qualitatively]
        • Market size: [Insert numerical data]
        • Growth projections: [Insert numerical data]
        • Target demographics: [Describe qualitatively]

    <b>Business Analysis</b>
    • Business model:
        • Revenue streams: [Describe qualitatively]
        • Target market size: [Insert numerical data]
        • Value proposition: [Describe qualitatively]
        • Revenue projections: [Insert numerical data]
        • Market share: [Insert numerical data]

    <b>Market Analysis</b>
        • Market size: [Insert numerical data]
        • Growth trends: [Describe qualitatively]
        • Competition analysis: [Describe qualitatively]
        • Opportunities: [Describe qualitatively]
        • Market share: [Insert numerical data]
        • Growth projections: [Insert numerical data]

    <b>Founders' Background</b>
        • Qualifications: [Describe qualitatively]
        • Experience: [Describe qualitatively]
        • Past successes: [Insert numerical data]
        • Industry recognition: [Describe qualitatively]
    
    <b>Conclusion</b>
    • Summarize key findings and provide recommendations for the company's future direction.
        • Include numerical data on growth projections, risk mitigation strategies, and performance improvement initiatives.

    Add below topics only if the user requested:

    If there are any topics user requested then add those topics and finally conclusion like above format

        <b>Go-to-Market Strategy</b>
            • Product/service launch: [Describe qualitatively]
            • Distribution channels: [Describe qualitatively]
            • Marketing tactics: [Describe qualitatively]
            • Partnerships: [Describe qualitatively]
            • Customer acquisition costs: [Insert numerical data]
            • Conversion rates: [Insert numerical data]

        <b>Customer Feedback</b>:
            • Satisfaction metrics: [Insert numerical data]
            • Retention rates: [Insert numerical data]

        <b>Risk Assessment</b>
        • Risk factors:
            • List specific risk factors and explain their potential impact.
            • Include numerical data on risk mitigation strategies and their effectiveness.
        • Regulatory Issues: [Describe qualitatively]

        <b>Performance Metrics</b>
        • Key metrics:
            • Revenue growth: [Insert numerical data]
            • Profitability: [Insert numerical data]
            • Customer acquisition cost: [Insert numerical data]
            • Market share: [Insert numerical data]
        • Benchmarking:
            • Performance gaps: [Insert numerical data]
            • Improvement targets: [Insert numerical data]

        <b>Strategic Analysis</b>
        • SWOT Analysis:
            • Strengths: [Describe qualitatively]
            • Weaknesses: [Describe qualitatively]
            • Opportunities: [Describe qualitatively]
            • Threats: [Describe qualitatively]
            • Market positioning: [Insert numerical data]
            • Competitive advantages: [Insert numerical data]

    
    """
    
    summarization_prompt = ChatPromptTemplate.from_template(summarization_template)

    
    summarization_chain = summarization_prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser()
    summarization_response = summarization_chain.invoke({"text": texts,"topics":report_topics})
    summary = summarization_response  # Extract the summary from the response

    return summary

def generate_summary(text_data):
    report_types=[]

    summary=generate_text(text_data,report_types)
    '''# Replace <b> and </b> tags with bold text for subtitles
    subtitle_pattern = r'<b>(.*?)</b>'
    report_content = re.sub(subtitle_pattern, r'<font name="Helvetica-Bold">\1</font>', summary)

        # Generate the PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, watermark="cybersnow doc", topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
    content = []

        # Define custom styles for different elements
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            leading=18
        )
    subheading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=8,
            fontName='Helvetica-Bold'  # Set font to bold for subtitles
        )
    normal_style = styles['BodyText']
    normal_style.leading = 16

        # Add title
    title = Paragraph("Research Report", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 12))

        # Add text data
    paragraphs = report_content.split("\n") 
    for paragraph in paragraphs:
        if paragraph.strip():  # Skip empty paragraphs
            if paragraph.startswith('<font name="Helvetica-Bold">') and paragraph.endswith('</font>'):  # Bold subtitle
                subtitle = Paragraph(paragraph[28:-7], subheading_style)
            else:  # Normal paragraph
                subtitle = Paragraph(paragraph, normal_style)
            content.append(subtitle)
            content.append(Spacer(1, 6))  # Add space between paragraphs

    doc.build(content)

        # Reset buffer position to start
    buffer.seek(0)

        # Return the PDF file as a downloadable attachment
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'

    return response'''

    return summary


