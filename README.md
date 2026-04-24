# Pro AI Profiler 2026

Защищённое веб-приложение для аудита и анализа переговоров с использованием AI.

## Возможности

- **Загрузка аудио** — поддержка MP3, WAV, M4A
- **Запись в реальном времени** — встроенный рекордер
- **Транскрибация с диаризацией** — разделение спикеров (Deepgram)
- **Анонимизация** — автоматическое обезличивание данных
- **Анализ эмоций** — определение тональности высказываний
- **AI-анализ** — LLM-обработка через Groq

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| UI | Streamlit |
| Транскрибация | Deepgram API |
| LLM | Groq (Llama, Qwen) |
| Контейнеризация | Docker + Docker Compose |


## Структура проекта

```
AI_Analyst_Docker/
├── app.py                  # Main приложение Streamlit
├── docker-compose.yml      # Конфигурация Docker Compose
├── Dockerfile              # Образ приложения
├── requirements.txt        # Python зависимости
└── services/
    ├── ai_service.py      # AI анализ (Groq)
    ├── dg_service.py      # Транскрибация (Deepgram)
    ├── emotion_service.py # Анализ эмоций
    └── security_service.py# Анонимизация
```

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DEEPGRAM_API_KEY` | API ключ Deepgram |
| `GROQ_API_KEY` | API ключ Groq |****

## Руководство по установке проекта

### Шаг 1. Скачать проект с GitHub на устройство

Открой терминал (или командную строку) и выполни:

```bash
git clone <ссылка_на_репозиторий>
```

Если git не установлен, скачай проект вручную как ZIP-архив со страницы GitHub и распакуй.

После клонирования перейди в папку проекта:

```bash
cd <имя_папки_проекта>
```

---

### Шаг 2. Установить и запустить Docker

**Если Docker ещё не установлен:**
- Скачай Docker Desktop с [официального сайта](https://www.docker.com/products/docker-desktop/)
- Установи его (на Windows потребуется включить WSL2)
- Запусти Docker Desktop и дождись, пока индикатор внизу слева станет зелёным

**Проверить, что Docker работает:**

```bash
docker --version
docker-compose --version
```

---

### Шаг 3. Перейти в папку AI_Analyst_Docker

Внутри скачанного проекта выполни:

```bash
cd AI_Analyst_Docker
```

---

### Шаг 4. Скопировать файл .env.example в .env

**Windows (cmd):**

```cmd
copy .env.example .env
```

**Windows (PowerShell) / macOS / Linux:**

```bash
cp .env.example .env
```

---

### Шаг 5. Получить API-ключи

1. **Groq** — открой [https://console.groq.com/keys](https://console.groq.com/keys)  
   Зарегистрируйся / войди и нажми **Create API Key**. Скопируй ключ.

2. **Deepgram** — открой [https://console.deepgram.com/project/3f860c19-66a3-4b0d-b059-d1e9dfc43853/keys](https://console.deepgram.com/project/3f860c19-66a3-4b0d-b059-d1e9dfc43853/keys)  
   Если проект не твой — зайди в свой проект Deepgram и создай ключ.

---

### Шаг 6. Вставить ключи в файл .env

Открой файл `.env` любым текстовым редактором (Блокнот, VS Code, nano, vim).

Найди строки:

```
GROQ_API_KEY=
DEEPGRAM_API_KEY=
```

Вставь ключи без кавычек, например:

```
GROQ_API_KEY=gsk_твой_ключ_здесь
DEEPGRAM_API_KEY=твой_ключ_deepgram
```

Сохрани файл.

---

### Шаг 7. Запустить проект через Docker Compose

В папке `AI_Analyst_Docker` выполни:

```bash
docker-compose up --build
```

При первом запуске Docker скачает все необходимые образы — это может занять несколько минут.

---

### Шаг 8. Готово 

Проект запущен и работает. Обычно веб-интерфейс доступен по адресу:

👉 **http://localhost:3000** (или порт, указанный в docker-compose.yml)

Чтобы остановить проект — нажми `Ctrl + C` в терминале.

Чтобы запустить снова (без пересборки):

```bash
docker-compose up
```
