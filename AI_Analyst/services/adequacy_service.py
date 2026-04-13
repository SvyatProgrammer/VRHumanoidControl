from crewai import Agent, Task, Crew, LLM
import os
import json
import re

def extract_json_from_text(text):
    """Улучшенная функция извлечения JSON"""
    try:
        # Пытаемся найти блок JSON между фигурными скобками
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except:
        pass
    return None

def evaluate_customer_adequacy(dialogue_list, groq_api):
    if not dialogue_list:
        return {
            'adequacy_score': 0, 'can_proceed': False, 'criteria': {},
            'risks': ['Диалог пуст'], 'recommendations': [], 'analysis': 'Нет данных'
        }
    
    os.environ["GROQ_API_KEY"] = groq_api
    my_model = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_api)
    
    full_text = "\n".join([f"Спикер {s}: {t}" for s, t in dialogue_list])
    
    adequacy_analyst = Agent(
        role='Эксперт по оценке требований',
        goal='Оценить адекватность заказчика по шкале от 0 до 100.',
        backstory='Ты опытный IT-консультант. Ты видишь проблемных клиентов по тексту.',
        llm=my_model,
        allow_delegation=False
    )
    
    risk_analyst = Agent(
        role='Аналитик рисков',
        goal='Выявить потенциальные риски при работе с заказчиком.',
        backstory='Ты специалист по управлению рисками в IT-проектах.',
        llm=my_model,
        allow_delegation=False
    )
    
    task_adequacy = Task(
        description=f"""Проанализируй диалог и оцени адекватность заказчика (каждый критерий от 0 до 100):
        1. Четкость требований
        2. Реалистичность сроков
        3. Четкость бюджета
        4. Логичность
        5. Техническая грамотность
        6. Готовность к сотрудничеству
        
        Диалог:
        {full_text}
        
        Верни СТРОГИЙ JSON (без лишнего текста вокруг):
        {{
            "criterias": {{"clarity": 0, "timeline": 0, "budget": 0, "logic": 0, "tech_knowledge": 0, "cooperation": 0}},
            "overall_score": 0,
            "analysis": "подробный текст анализа"
        }}""",
        agent=adequacy_analyst,
        expected_output="JSON с оценками по критериям"
    )
    
    task_risks = Task(
        description=f"""Выяви риски в диалоге:
        {full_text}
        
        Верни СТРОГИЙ JSON:
        {{
            "risks": [{{"risk": "описание", "probability": "высокая/средняя/низкая"}}],
            "recommendations": ["совет 1", "совет 2"]
        }}""",
        agent=risk_analyst,
        expected_output="JSON с рисками и рекомендациями"
    )
    
    crew = Crew(agents=[adequacy_analyst, risk_analyst], tasks=[task_adequacy, task_risks])
    
    try:
        result = crew.kickoff()
        data = extract_json_from_text(str(result))
        
        if data:
            criteria = data.get('criterias', {})
            overall = data.get('overall_score', sum(criteria.values()) / len(criteria) if criteria else 0)
            
            # Вытягиваем риски (так как задачи выполняются последовательно, результат содержит данные обеих)
            return {
                'adequacy_score': int(overall),
                'can_proceed': overall >= 70,
                'criteria': criteria,
                'risks': data.get('risks', []),
                'recommendations': data.get('recommendations', []),
                'analysis': data.get('analysis', "Анализ завершен успешно.")
            }
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        
    return {'adequacy_score': 0, 'can_proceed': False, 'criteria': {}, 'risks': [f'Ошибка: {str(e)}'], 'recommendations': [], 'analysis': 'Ошибка'}