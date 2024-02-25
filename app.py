import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from google.protobuf import json_format

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Set API key

# Improved `get_gemini_response` function with error handling and structured output
def get_gemini_response(input):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(input)
        return response.text  # Convert response to dictionary
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

# Enhanced `input_pdf_text` function with progress bar and error handling
def input_pdf_text(uploaded_file):
    if not uploaded_file:
        st.error("Please upload a PDF resume.")
        return None

    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        with st.spinner("Extracting text..."):
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Define clear prompt template with placeholders
prompt_template = """
Hey ATS, act like a skilled recruiter with deep understanding of {tech_roles}.
Evaluate the resume based on the job description: {job_description}.
Consider the competitive job market and provide actionable feedback for improvement.
Assign matching percentage based on JD and missing keywords with high accuracy.

Resume: {resume}

Response format: {{'JD Match': '%', "MissingKeywords": [], "Profile summary": "", "Feedback": ""}}
"""

# Streamlit app with additional features and improvements
st.title("ATS Resume Screener")
st.text("Get feedback on your resume and improve your chances of landing the job!")

# Add selection of tech roles for tailored feedback
tech_roles = st.multiselect(
    "Select your relevant tech roles:",
    ["Software Engineering", "Data Science", "Machine Learning", "Cloud Computing"],
)

# Add progress bar for better user experience
with st.form("resume_form"):
    jd = st.text_area("Paste the job description")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload your resume in PDF format")
    submit = st.form_submit_button("Submit")

if submit:
    text = input_pdf_text(uploaded_file)
    if text:
        with st.spinner("Analyzing resume..."):
            prompt = prompt_template.format(
                tech_roles=", ".join(tech_roles), job_description=jd, resume=text
            )
            response = get_gemini_response(prompt)
            if response:
                st.subheader("ATS Feedback:")
                st.json(response)  # Display response in a formatted way
            else:
                st.error("An error occurred while processing your resume.")
    else:
        st.error("An error occurred while processing your resume.")
