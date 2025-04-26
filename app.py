import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

# Setup
app = Flask(__name__)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing in .env file")

genai.configure(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            return text.strip()
    except:
        pass

    try:
        images = convert_from_path(pdf_path)
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except:
        pass

    return text.strip()

def analyze_resume(resume_text, job_description=None):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are an experienced HR... (same prompt as earlier)
Resume:
{resume_text}
"""

    if job_description:
        prompt += f"\n\nJob Description:\n{job_description}"

    response = model.generate_content(prompt)
    return response.text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        resume = request.files["resume"]
        job_desc = request.form.get("job_description")

        if resume:
            resume_path = "uploaded_resume.pdf"
            resume.save(resume_path)
            resume_text = extract_text_from_pdf(resume_path)

            if resume_text:
                result = analyze_resume(resume_text, job_desc)
            else:
                result = "❌ Could not extract text from the resume."

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
