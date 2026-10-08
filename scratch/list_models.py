import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}"
}
response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
print(response.json())
