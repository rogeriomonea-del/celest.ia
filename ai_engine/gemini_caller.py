import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("AIzaSyDzaE0LjTO_htbXN8F3mUqajNYDF1553tI"))

def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text
