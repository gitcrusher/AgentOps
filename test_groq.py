import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Please set GROQ_API_KEY in .env")
    exit(1)

client = Groq(api_key=api_key)
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Respond with exactly one word: Success",
        }
    ],
    model="llama-3.1-8b-instant",
)
print("Groq API Test:", chat_completion.choices[0].message.content)
