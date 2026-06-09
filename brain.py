# importing the libraries
import os
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai
from pdf2image import convert_from_bytes

# reading the env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# prompt for x-ray analysis
PROMPT = """You are an experienced radiologist and medical imaging specialist.
    Analyze this medical scan and provide a structured response with these sections:

    1. Scan Type & View - identify what type of scan this is
    2. Key Findings - list all observable findings in detail
    3. Impression - your overall diagnostic impression
    4. Recommendations - suggested next steps

    Be clinical, precise and detailed. Always end with:
    'This analysis is AI-generated and must be reviewed by a licensed medical professional.'"""

PROMPT_2 = """YOU are the doctor you got the report you can understand the technicalities but the patient
            cannot, so try to explain it to the patient in simple terms do not use jargons 
            1) State the problems
            2) State the possible solutions to the problems
            
            AND always end with 'This analysis is AI-generated and must be reviewed by a licensed medical professional.'"""

# Initialize client 
client = genai.Client(api_key=GEMINI_API_KEY)

# extracting image from a pdf
def extract_image_from_pdf(pdf_bytes):
    pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
    return pages[0]

# giving the user response based on whether they are able to upload a file or an image or nothing
def analyze_scan(image_bytes, media_type):
    try:
        if media_type == "application/pdf":
            image = extract_image_from_pdf(image_bytes)
        elif media_type in ["image/jpeg", "image/png", "image/webp"]:
            image = Image.open(io.BytesIO(image_bytes))
        else:
            return "Error: Please upload a valid image or a PDF."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, PROMPT]
        )
        return response.text
    except Exception as e:
        print(f"API Error during analysis: {e}")
        return None
    

def simplify_report(report):
    if not report or "failed" in report.lower() or "busy" in report.lower():
        return None
        
    try:
        summary = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[report, PROMPT_2]
        )
        return summary.text

    except Exception as e:
        print(f"API Error during simplification: {e}")
        return None