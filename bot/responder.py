import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(prompt):
    # For now, return fixed response
    return "Thank you for your message. We’ll get back to you shortly."
    # You could swap the line above with:
    # return openai.ChatCompletion.create(...)
