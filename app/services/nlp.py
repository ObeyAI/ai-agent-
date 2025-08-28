import os
from dotenv import load_dotenv
load_dotenv()
# optional OpenAI integration: import and create client when OPENAI_API_KEY provided
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
nlp_client = None
if OPENAI_KEY:
    try:
        from openai import OpenAI
        nlp_client = OpenAI(api_key=OPENAI_KEY)
    except Exception as e:
        nlp_client = None
