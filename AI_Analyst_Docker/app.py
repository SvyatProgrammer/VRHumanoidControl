import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder

from services.dg_service import transcribe_with_diarization
from services.security_service import anonymize_dialogue
from services.emotion_service import analyze_emotions
from services.ai_service import run_analysis

load_dotenv()

st.set_page_config(page_title="Pro AI Profiler 2026", layout="wide")
st.title("Pro AI Profiler: Защищенный аудит переговоров")

dg_env_key = os.getenv("DEEPGRAM_API_KEY", "")
q_env_key = os.getenv("GROQ_API_KEY", "")

SPEAKER_COLORS = ["#00B4D8", "#F94144", "#90BE6D", "#F9C74F", "#577590"]

# --- Sidebar ---
with st.sidebar:
    st.header("Настройки")
    dg_key = st.text_input("Deepgram Key", type="password", value=dg_env_key)
    q_key = st.text_input("Groq Key", type="password", value=q_env_key)

# --- Main logic ---
if dg_key and q_key:
    c_up, c_rec = st.columns(2)

    with c_up:
        uploaded_file = st.file_uploader("Загрузить файл", type=["mp3", "wav", "m4a"])

    with c_rec:
        audio_bytes = audio_recorder(text="Записать аудио")

    if uploaded_file or audio_bytes:

        # --- Получаем аудио ---
        final_audio = None

        if uploaded_file:
            final_audio = uploaded_file.read()
        elif audio_bytes:
            final_audio = audio_bytes

        # --- Проверка ---
        if not final_audio:
            st.error("Аудио не записано или пустое")
            st.stop()

        st.write(f"Размер аудио: {len(final_audio)} байт")  # DEBUG

        # --- Сохраняем ---
        temp_fn = "temp_analysis.wav"
        with open(temp_fn, "wb") as f:
            f.write(final_audio)

        # --- Запуск ---
        if st.button("Запустить аудит", use_container_width=True):
            try:
                with st.status("Обработка данных...") as status:

                    # --- Расшифровка ---
                    raw_dialogue = transcribe_with_diarization(temp_fn, dg_key)

                    if not raw_dialogue:
                        st.error("Ошибка: пустая расшифровка")
                        st.stop()

                    # --- Анонимизация ---
                    dialogue = anonymize_dialogue(raw_dialogue)

                    if not dialogue:
                        st.error("Ошибка: диалог пуст")
                        st.stop()

                    # --- Эмоции ---
                    emo_results = analyze_emotions(dialogue, q_key)

                    # DEBUG
                    st.write("Диалог:", len(dialogue))
                    st.write("Эмоции:", len(emo_results))

                    status.update(label="Анализ завершен", state="complete")

                # --- Tabs ---
                t_chat, t_metrics, t_audit = st.tabs(
                    ["Диалог", "Профили", "Заключение"]
                )

                # --- Диалог ---
                with t_chat:
                    for i, item in enumerate(dialogue):

                        # защита от кривых данных
                        if isinstance(item, (list, tuple)) and len(item) == 2:
                            speaker, text = item
                        else:
                            speaker, text = 0, str(item)

                        # защита от выхода за индекс
                        emo = emo_results[i] if i < len(emo_results) else {
                            "summary": "Нет данных",
                            "adequacy": "-",
                            "seriousness": "-",
                            "hostility": 0
                        }

                        with st.chat_message(
                            f"Speaker {speaker}",
                            avatar="assistant" if speaker == 0 else "user"
                        ):
                            if emo.get('hostility', 0) > 40:
                                st.error(emo.get('summary'))
                            elif emo.get('hostility', 0) > 20:
                                st.warning(emo.get('summary'))
                            else:
                                st.info(emo.get('summary', ''))

                            st.caption(
                                f"Adequacy: {emo.get('adequacy', '-')}"
                                f" | Seriousness: {emo.get('seriousness', '-')}"
                                f" | Hostility: {emo.get('hostility', '-')}%"
                            )

                # --- Метрики ---
                with t_metrics:
                    df = pd.DataFrame(emo_results)

                    if not df.empty and "speaker" in df.columns:
                        for i in range(len(SPEAKER_COLORS)):
                            speaker_data = df[df["speaker"] == i]

                            if not speaker_data.empty:
                                st.metric(
                                    f"Speaker {i} Adequacy",
                                    f"{speaker_data['adequacy'].mean():.0f}"
                                )
                                st.metric(
                                    f"Speaker {i} Hostility",
                                    f"{speaker_data['hostility'].mean():.0f}%"
                                )
                    else:
                        st.warning("Нет данных для метрик")

                # --- Финальный анализ ---
                with t_audit:
                    analysis_result = run_analysis(dialogue, q_key)
                    st.markdown(analysis_result)

            except Exception as e:
                st.error(f"Ошибка: {str(e)}")