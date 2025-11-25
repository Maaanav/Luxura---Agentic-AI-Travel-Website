import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=API_KEY)

def ask_llm(prompt: str, system: str = "You must return ONLY valid JSON.") -> dict:
    """
    Calls OpenAI with structured output using response_format.
    Requires system message to contain the word 'json'.
    """

    if "json" not in system.lower():
        system += " (Return only JSON)"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}  
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        logger.error(f"Structured LLM error: {e}")
        return {}
