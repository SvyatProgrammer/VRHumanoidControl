import streamlit as st
import pandas as pd
import plotly.express as px
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

with st.sidebar:
    st.header("Настройки")
    dg_key = st.text_input("Deepgram Key", type="password", value=dg_env_key)
    q_key = st.text_input("Groq Key", type="password", value=q_env_key)

if dg_key and q_key:
    c_up, c_rec = st.columns(2)
    with c_up: uploaded_file = st.file_uploader("Загрузить файл", type=["mp3", "wav", "m4a"])
    with c_rec: audio_bytes = audio_recorder(text="Записать аудио")

    if (uploaded_file or audio_bytes):
        final_audio = uploaded_file.read() if uploaded_file else audio_bytes
        temp_fn = "temp_analysis.wav"
        with open(temp_fn, "wb") as f: f.write(final_audio)

        if st.button("Запустить аудит", use_container_width=True):
            try:
                with st.status("Обработка данных...") as status:
                    raw_dialogue = transcribe_with_diarization(temp_fn, dg_key)
                    dialogue = anonymize_dialogue(raw_dialogue)
                    emo_results = analyze_emotions(dialogue, q_key)
                    status.update(label="Анализ завершен", state="complete")

                t_chat, t_metrics, t_audit = st.tabs(["Диалог", "Профили", "Заключение"])

                with t_chat:
                    for i, (speaker, text) in enumerate(dialogue):
                        emo = emo_results[i] if i < len(emo_results) else {}
                        with st.chat_message(f"Speaker {speaker}", avatar="assistant" if speaker == 0 else "user"):
                            if emo.get('hostility', 0) > 40: st.error(emo.get('summary'))
                            elif emo.get('hostility', 0) > 20: st.warning(emo.get('summary'))
                            else: st.info(emo.get('summary', ''))
                            st.caption(f"Adequacy: {emo.get('adequacy', '-')} | Seriousness: {emo.get('seriousness', '-')} | Hostility: {emo.get('hostility', '-')}%")

                with t_metrics:
                    df = pd.DataFrame(emo_results)
                    if not df.empty:
                        cols = st.columns(len(SPEAKER_COLORS))
                        for i, c in enumerate(cols):
                            with c: 
                                speaker_data = df[df["speaker"] == i]
                                if not speaker_data.empty:
                                    st.metric("Adequacy", f"{speaker_data['adequacy'].mean():.0f}")
                                    st.metric("Hostility", f"{speaker_data['hostility'].mean():.0f}%")

                with t_audit:
                    analysis_result = run_analysis(dialogue, q_key)
                    st.markdown(analysis_result)

            except Exception as e:
                st.error(f"Ошибка: {e}")