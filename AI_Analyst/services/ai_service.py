from crewai import Agent, Task, Crew, LLM
import os

def run_analysis(dialogue_list, groq_api):
    if not dialogue_list:
        return "❌ Ошибка: диалог пуст. Нечего анализировать."
    
    os.environ["GROQ_API_KEY"] = groq_api
    my_model = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_api)
    
    full_text = "\n".join([f"Спикер {s}: {t}" for s, t in dialogue_list])

    analyst = Agent(
        role='Бизнес-профайлер',
        goal='Сделать выжимку из бизнес-требований.',
        backstory='Ты аналитик, который вытягивает суть из хаоса переговоров.',
        llm=my_model,
        allow_delegation=False
    )

    architect = Agent(
        role='Системный аналитик',
        goal='Составить подробное техническое задание.',
        backstory='Ты мастер структурирования ТЗ.',
        llm=my_model,
        allow_delegation=False
    )

    t1 = Task(
        description=f"Проанализируй диалог: \n{full_text}\n и составь отчет о целях клиента.",
        agent=analyst,
        expected_output="Бизнес-цели проекта."
    )

    t2 = Task(
        description=f"На основе диалога: \n{full_text}\n разработай структуру ТЗ (стек, функции).",
        agent=architect,
        expected_output="Готовое ТЗ в формате Markdown."
    )

    crew = Crew(agents=[analyst, architect], tasks=[t1, t2])
    return crew.kickoff()