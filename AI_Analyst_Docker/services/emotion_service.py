from groq import Groq
import json
import re

def analyze_emotions(dialogue_list, groq_api):
    client = Groq(api_key=groq_api)
    formatted_dialogue = ""
    for i, (speaker, text) in enumerate(dialogue_list):
        formatted_dialogue += f"[{i}] Спикер {speaker}: {text}\n"

    prompt = f"""
    Проведи психологический анализ диалога. Для каждого сообщения выстави оценки 0-100.
    КРИТЕРИИ: Adequacy, Seriousness, Hostility, Pressure, Logic.
    Диалог:
    {formatted_dialogue}
    Верни JSON список:
    [
      {{
        "index": 0, 
        "speaker": 0,
        "adequacy": 80, 
        "seriousness": 90, 
        "hostility": 5, 
        "pressure": 0, 
        "logic": 100,
        "summary": "Причина оценки"
      }}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Выдавай только чистый JSON список."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        return json.loads(json_match.group(0)) if json_match else json.loads(content)
    except:
        return []