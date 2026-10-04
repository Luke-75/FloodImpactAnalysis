# flimpanal_ai.py

from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI


class AnalysisRequest(BaseModel):
    location: str = Field(min_length=1)
    radius_km: float = Field(default=2.0, gt=0, le=10)

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Location must not be empty.")

        return value


class ExtractedAnalysisRequest(BaseModel):
    location: str
    radius_km: float | None = None


AI_MODEL = "gpt-5-nano"

SYSTEM_PROMPT = """
Extract the location and analysis radius from the user's flood analysis request.

Rules:
- Return the location requested by the user.
- Return the radius in kilometers.
- If the user does not specify a radius, leave radius_km unspecified. Do not invent or modify a radius.
- Do not invent a location that the user did not provide.
"""


def parse_analysis_request(query: str) -> AnalysisRequest:

    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    
    load_dotenv(dotenv_path=env_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=openai_api_key)

    response = client.responses.parse(
        model=AI_MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        text_format=ExtractedAnalysisRequest,
    )

    extracted = response.output_parsed

    if extracted.radius_km is None:
        return AnalysisRequest(
            location=extracted.location,
        )

    return AnalysisRequest(
        location=extracted.location,
        radius_km=extracted.radius_km,
    )

    #return response.output_parsed





if __name__ == "__main__":
    print(parse_analysis_request("Analyze flooding within 20 km of Prague."))




