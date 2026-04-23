from crewai import Agent, Task, Crew, LLM
import os

def run_analysis(dialogue_list, groq_api):
    os.environ["GROQ_API_KEY"] = groq_api
    my_model = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_api)
    full_text = "\n".join([f"Спикер {s}: {t}" for s, t in dialogue_list])

    auditor = Agent(
        role='Технический аудитор',
        goal='Выявить предмет обсуждения и сопоставить требования с реальностью.',
        backstory='Ты эксперт по оценке сложности проектов. Ты отсекаешь лишнее и оставляешь только факты.',
        llm=my_model
    )

    consultant = Agent(
        role='Бизнес-консультант',
        goal='Оценить коммерческую надежность заказчика и риски сотрудничества.',
        backstory='Ты опытный переговорщик, который видит скрытые угрозы и нереалистичные схемы.',
        llm=my_model
    )

    t1 = Task(
        description=f"Определи тему и выдели основные требования из текста: \n{full_text}",
        agent=auditor,
        expected_output="Тема разговора и список требований."
    )

    t2 = Task(
        description="Проверь требования на реализуемость и найди логические противоречия.",
        agent=auditor,
        expected_output="Технический разбор реальности требований."
    )

    t3 = Task(
        description="Оцени надежность заказчика и дай итоговый вердикт: стоит ли работать с ним.",
        agent=consultant,
        expected_output="Бизнес-рекомендация в формате Markdown."
    )

    crew = Crew(agents=[auditor, consultant], tasks=[t1, t2, t3])
    return crew.kickoff()