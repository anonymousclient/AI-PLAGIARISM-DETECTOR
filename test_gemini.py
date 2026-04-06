import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils.similarity import get_ai_probability

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print(f"Key Found: {key[:5]}...{key[-5:] if key else 'None'}")

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"FULL ERROR: {e}")
