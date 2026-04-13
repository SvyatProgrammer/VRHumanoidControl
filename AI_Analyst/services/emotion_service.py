from groq import Groq
import json
import re

def analyze_emotions(dialogue_list, groq_api):
    client = Groq(api_key=groq_api)
    
    # Объединяем диалог для контекстного анализа
    formatted_dialogue = ""
    for i, (speaker, text) in enumerate(dialogue_list):
        formatted_dialogue += f"[{i}] Спикер {speaker}: {text}\n"

    # Промпт, основанный на техниках бизнес-профайлинга
    prompt = f"""
    Ты - эксперт-лингвист и бизнес-профайлер. Твоя задача - провести глубокий психологический анализ диалога.
    Для каждого сообщения [{len(dialogue_list)} шт] выстави оценки от 0 до 100 по следующим критериям:

    КРИТЕРИИ:
    1. Adequacy (Адекватность): Насколько требования реалистичны и обоснованы. 
       (0 - бред/галлюцинации, 100 - идеальное понимание процесса).
    2. Seriousness (Серьезность): Уровень готовности к сделке. Конкретика против "воды".
    3. Hostility (Враждебность): Включая сарказм, пренебрежение, пассивную агрессию и обесценивание.
    4. Pressure (Давление): Попытки манипулировать сроками, ценой или вызывать чувство вины.
    5. Logic (Логика): Связность и отсутствие противоречий с предыдущими фразами.

    Диалог для анализа:
    {formatted_dialogue}

    ОБЯЗАТЕЛЬНО верни ответ СТРОГО в формате JSON списка объектов:
    [
      {{
        "index": 0, 
        "adequacy": 80, 
        "seriousness": 90, 
        "hostility": 5, 
        "pressure": 0, 
        "logic": 100,
        "tags": ["Professional", "Clear goals"],
        "summary": "Краткое пояснение почему такая оценка"
      }},
      ...
    ]
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты выдаешь только чистый JSON без вступлений."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        # Очистка от возможных markdown-тегов
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        return json.loads(json_match.group(0)) if json_match else json.loads(content)
    except Exception as e:
        print(f"Emotion Analysis Error: {e}")
        return []