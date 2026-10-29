import json
from openai import AsyncOpenAI

from app.config.config import settings


def get_client():
    if not settings.OPENAI_API_KEY:
        return None
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
    )


get_openai_client = get_client


async def classify_text(text: str, categories: list[str]) -> str:
    client = get_client()
    if client:
        try:
            prompt = (
                f"Classify this text into exactly ONE category from: {', '.join(categories)}.\n"
                f"Text: \"{text}\"\n"
                f"Reply with ONLY the category name."
            )
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            raw = (response.choices[0].message.content or "").strip().lower()
            for cat in categories:
                if cat.lower() in raw:
                    return cat
        except Exception:
            pass

    lower_text = text.lower()
    for cat in categories:
        if cat.lower() in lower_text:
            return cat

    return categories[0] if categories else "neutral"


async def generate_workflow(description: str, custom_name: str | None = None) -> dict:
    client = get_client()
    if client:
        try:
            prompt = (
                f"Convert this description into a workflow JSON:\n"
                f"Description: \"{description}\"\n\n"
                f"Allowed step types:\n"
                f"- text_transform: {{\"type\": \"text_transform\", \"operation\": \"uppercase\"|\"lowercase\"|\"trim\"|\"reverse\"}}\n"
                f"- arithmetic: {{\"type\": \"arithmetic\", \"operation\": \"add\"|\"subtract\"|\"multiply\"|\"division\", \"operand\": 10}}\n"
                f"- ai_classify: {{\"type\": \"ai_classify\", \"categories\": [\"positive\", \"negative\", \"neutral\"]}}\n\n"
                f"Return valid JSON with keys: 'name', 'description', and 'steps'."
            )
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a workflow designer. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)
            steps = parsed.get("steps", [])
            if steps:
                return {
                    "name": custom_name or parsed.get("name", "Generated Workflow"),
                    "description": parsed.get("description", description),
                    "steps": steps,
                }
        except Exception:
            pass

    return {
        "name": custom_name or "Generated Workflow",
        "description": description,
        "steps": _fallback_steps(description),
    }


def _fallback_steps(description: str) -> list[dict]:
    steps = []
    desc = description.lower()
    if "upper" in desc:
        steps.append({"type": "text_transform", "operation": "uppercase"})
    elif "lower" in desc:
        steps.append({"type": "text_transform", "operation": "lowercase"})

    if "classif" in desc or "sentiment" in desc:
        steps.append(
            {
                "type": "ai_classify",
                "categories": ["positive", "negative", "neutral"],
            }
        )

    return steps or [
        {"type": "text_transform", "operation": "trim"},
        {"type": "text_transform", "operation": "uppercase"},
    ]


class OpenAIService:
    classify_text = staticmethod(classify_text)
    generate_workflow = staticmethod(generate_workflow)

