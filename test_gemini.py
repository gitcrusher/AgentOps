import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_gemini_api_key_here":
    print("Please set GEMINI_API_KEY in .env")
    exit(1)

client = genai.Client(api_key=api_key, http_options={'verify': False})
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Respond with exactly one word: Success'
)
print("Gemini API Test:", response.text)
