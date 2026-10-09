import json

from ollama import chat


MODEL = "qwen2.5:7b"


def analyze_git_activity(git_activity):
    prompt = f"""
You are a software engineering reporting assistant.

Analyze the Git activity below and create a concise daily engineering report.

IMPORTANT:
- Do not invent information.
- Only make conclusions supported by the commits and diffs.
- Keep the report factual.
- Group related changes together.
- Focus on what was actually accomplished.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "summary": "A concise overall summary of the day's work.",
  "accomplishments": [
    "Major accomplishment 1",
    "Major accomplishment 2"
  ],
  "bugs_fixed": [
    "Bug or issue fixed"
  ],
  "technical_changes": [
    "Important technical change"
  ],
  "next_steps": [
    "Potential follow-up work supported by the changes"
  ]
}}

If a section has nothing meaningful to report, return an empty array.

Git activity:

{git_activity}
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    content = response["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Ollama returned invalid JSON:\n\n" + content
        )
