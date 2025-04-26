import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import tempfile

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY is missing in .env file")
    st.stop()

genai.configure(api_key=api_key)

# Extract text from PDF
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

# Analyze resume using Gemini
def analyze_resume(resume_text, job_description=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
You are an experienced HR. Please review the following resume and provide a detailed analysis including strengths, weaknesses, and suggestions for improvement. Focus on relevance to the job description if provided.

Resume:
{resume_text}
"""
    if job_description:
        prompt += f"\n\nJob Description:\n{job_description}"

    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit App UI
st.title("📄 AI Resume Analyzer (Gemini-Powered)")

resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_description = st.text_area("Optional: Paste Job Description")

if st.button("Analyze Resume"):
    if not resume_file:
        st.warning("Please upload a resume.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(resume_file.read())
            resume_path = tmp_file.name

        resume_text = extract_text_from_pdf(resume_path)
        if not resume_text:
            st.error("❌ Could not extract text from the resume.")
        else:
            with st.spinner("Analyzing resume with Gemini AI..."):
                result = analyze_resume(resume_text, job_description)
            st.subheader("📊 Analysis Result")
            st.write(result)
