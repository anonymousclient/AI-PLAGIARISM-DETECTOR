import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

def detect_ai_content(text):
    """
    Analyzes text using OpenRouter API to determine the probability of it being AI-generated.
    Returns a score from 0-100.
    """
    if not text or len(text.strip()) < 50:
        return 0  # Not enough text to analyze reliably

    api_key = os.getenv("OPEN_ROUTER_KEY")
    if not api_key:
        print("[AI ERROR] No OPEN_ROUTER_KEY found in environment.")
        return -1

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Simplified prompt for reliability
        prompt = f"Determine the AI-generated probability (0-100) of this text. Return ONLY the integer. Text: {text[:5000]}"
        
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content
        match = re.search(r'\d+', content)
        if match:
            score = int(match.group())
            return min(max(score, 0), 100)
        else:
            return -1
            
    except Exception as e:
        print(f"[AI ERROR] OpenRouter analysis failed: {e}")
        return -1
