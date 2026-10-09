import os
import json
from pathlib import Path

from openai import AzureOpenAI
from dotenv import load_dotenv

# Credentials live next to this module (src/.env), not necessarily the process cwd.
load_dotenv(Path(__file__).resolve().parent / ".env")

client = AzureOpenAI(
    api_version = os.getenv("API_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
)

def generate_candidate_brief(candidate_result):
    """Generate structured Tempo candidate insights into a concise coach preparation brief."""

    prompt = f"""You are an assistant helping a career coach prepare for an upcoming 1 to 1 session.
    Use ONLY the information provided below.

    Candidate Information:
    {json.dumps(candidate_result, indent=2, default=str)}

    Create a concise coach preparation brief. 
    Return exactly 5 bullet points.

    Prioritize :
    1. Important progress since the previous meeting.
    2. Agreed actions that were completed.
    3. Agreed actions that appear to be incomplete or missing.
    4. Relevant candidate activities.
    5. The most useful point for the coach to discuss.

        Do not invent information.
        Do not assume an activity was completed unless the data says so.
        If there is insufficient information, say so clearly.
    """

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": ("You generate factual, concise preparation brief for career coaches.")
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print("LLM summary module loaded successfully")