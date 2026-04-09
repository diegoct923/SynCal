from openai import OpenAI
import json

client = OpenAI()

SYSTEM_PROMPT = """You are a system that classifies user intent and extracts structured task data.

Return ONLY a valid JSON object. No explanations, no extra text.

STRICT RULES:
- Output must be valid JSON (parsable by json.loads)
- Use double quotes for all keys and strings
- No trailing commas
- No text outside JSON
- Always include all fields
- If unknown, use null

OUTPUT FORMAT:
{
  "type": "ADD" | "LIST" | "CONNECT_NOTION" | "ERROR",
  "task": string | null,
  "date": string | null,
  "time": string | null,
  "duration": number | null,
  "priority": "low" | "medium" | "high" | null,
  "message": string | null
}

TYPE RULES:
- If user wants to create a task → "ADD"
- If user wants to see tasks → "LIST"
- If user wants to connect Notion → "CONNECT_NOTION"
- If unclear → "ERROR"

FIELD RULES:
- task → short clean description
- date → YYYY-MM-DD
- time → HH:MM (24h)
- duration → minutes (integer), default 60 if task exists but not specified
- priority:
  - "high" if words like urgente/importante
  - otherwise "medium"
- message → only used if type = "ERROR"

INTERPRETATION:
- "hoy" → current date
- "mañana" → current date + 1 day

EXAMPLES:

Input: "estudiar redes mañana 2 horas urgente"
Output:
{
  "type": "ADD",
  "task": "estudiar redes",
  "date": "2026-04-09",
  "time": null,
  "duration": 120,
  "priority": "high",
  "message": null
}

Input: "ver tareas"
Output:
{
  "type": "LIST",
  "task": null,
  "date": null,
  "time": null,
  "duration": null,
  "priority": null,
  "message": null
}

Input: "conectar notion"
Output:
{
  "type": "CONNECT_NOTION",
  "task": null,
  "date": null,
  "time": null,
  "duration": null,
  "priority": null,
  "message": null
}
"""

def is_valid(data): #aux para validar jsons
    required = ["task", "date", "time", "duration", "priority"]

    if not isinstance(data, dict):
        return False

    if not all(k in data for k in required):
        return False

    if data["priority"] not in ["low", "medium", "high"]:
        return False

    return True

def parse_message_ia(message:str) -> dict:
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    content = response.choices[0].message.content

    if not content:
        return {"type": "ERROR", "message": "Empty response from model"}

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {
        "type": "ERROR",
        "message": "Invalid JSON",
        "raw": content
    }
    
    if not is_valid(data):
        return {
        "type": "ERROR",
        "message": "Invalid structure",
        "data": data
        }

    return data
