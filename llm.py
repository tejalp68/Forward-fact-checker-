"""The one Gemini client that every agent uses."""

from langchain_google_genai import ChatGoogleGenerativeAI

from config import GOOGLE_API_KEY, MODEL

llm = ChatGoogleGenerativeAI(
    model=MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
    max_retries=3,
)