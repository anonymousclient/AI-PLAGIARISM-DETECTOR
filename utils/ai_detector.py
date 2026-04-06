import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def detect_ai_content(text):
    """
    Analyzes text using Gemini API to determine the probability of it being AI-generated.
    Returns a score from 0-100.
    """
    if not text or len(text.strip()) < 50:
        return 0  # Not enough text to analyze reliably

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[AI ERROR] No GEMINI_API_KEY found in environment.")
        return -1

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Simplified prompt for reliability
        prompt = f"Determine the AI-generated probability (0-100) of this text. Return ONLY the integer. Text: {text[:5000]}"
        
        response = model.generate_content(prompt)
        import re
        match = re.search(r'\d+', response.text)
        if match:
            score = int(match.group())
            return min(max(score, 0), 100)
        else:
            return -1
            
    except Exception as e:
        print(f"[AI ERROR] Gemini analysis failed: {e}")
        return -1
