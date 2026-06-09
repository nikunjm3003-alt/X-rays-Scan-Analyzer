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

# extracting image from an pdf
def extract_image_from_pdf(pdf_bytes):
    pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
    return pages[0]

# giving the user response based on whether they are able to upload a file or an image or nothing
def analyze_scan(image_bytes , media_type):
    try:
        if media_type == "application/pdf":
            image = extract_image_from_pdf(image_bytes)
        elif media_type in ["image/jpeg","image/png","image/webp"]:
            image = Image.open(io.BytesIO(image_bytes))
        else :
            return "Error please upload an image or a pdf"

        client = genai.Client(api_key =GEMINI_API_KEY)
    
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [image, PROMPT]
        )
        return response.text
    except Exception as e:
        error = str(e)
        if "503" in error or "UNAVAILABLE" in error:
            return "The AI service is temporarily busy. Please wait a moment and try again."
        elif "429" in error or "RESOURCE_EXHAUSTED" in error:
            return "API quota exceeded. Please try again in a few minutes."
        else:
            return f"Analysis failed: {error}"
    

def simplify_report(report):
    client = genai.Client(api_key = GEMINI_API_KEY)

    summary = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = [report,PROMPT_2]
    )
    return summary.text
    

# safety net
# if __name__ == "__main__":
#     with open("test.jpg", "rb") as f:
#         image_bytes = f.read()
#     result = analyze_scan(image_bytes, "image/jpeg")
#     print(result)