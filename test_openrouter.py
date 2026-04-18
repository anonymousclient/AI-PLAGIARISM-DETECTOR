import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPEN_ROUTER_KEY")
print(f"Key Found: {key[:5]}...{key[-5:] if key else 'None'}")

try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    content = response.choices[0].message.content
    print(f"Response: {content.encode('utf-8', 'ignore').decode('utf-8')}")
except Exception as e:
    print(f"FULL ERROR: {e}")
