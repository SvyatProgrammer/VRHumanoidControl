import streamlit as st
import pandas as pd
import plotly.express as px
from audio_recorder_streamlit import audio_recorder
from services.dg_service import transcribe_with_diarization
from services.emotion_service import analyze_emotions
from services.ai_service import run_analysis
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Pro AI Profiler 2026", layout="wide")
st.title("🎙️ Pro AI Profiler: Анализ и генерация ТЗ")

dg_env_key = os.getenv("DEEPGRAM_API_KEY", "")
q_env_key = os.getenv("GROQ_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Настройки API")
    dg_key = st.text_input("Deepgram Key", type="password", value=dg_env_key)
    q_key = st.text_input("Groq Key", type="password", value=q_env_key)

if dg_key and q_key:
    col_up, col_rec = st.columns(2)
    with col_up: uploaded_file = st.file_uploader("📁 Аудиофайл", type=["mp3", "wav", "m4a"])
    with col_rec: audio_bytes = audio_recorder(text="🎤 Записать встречу")

    if (uploaded_file or audio_bytes):
        final_audio = uploaded_file.read() if uploaded_file else audio_bytes
        temp_fn = "temp_analysis.wav"
        with open(temp_fn, "wb") as f: f.write(final_audio)

        if st.button("🚀 Провести полный бизнес-анализ", use_container_width=True):
            try:
                with st.status("Обработка данных...") as status:
                    st.write("Распознавание спикеров...")
                    dialogue = transcribe_with_diarization(temp_fn, dg_key)
                    st.write("Психологический профайлинг...")
                    emo_results = analyze_emotions(dialogue, q_key)
                    status.update(label="Анализ завершен!", state="complete", expanded=False)

                tab_chat, tab_metrics, tab_tz = st.tabs(["💬 Диалог и Анализ", "📊 Метрики", "📄 Итоговое ТЗ"])

                with tab_chat:
                    for i, (speaker, text) in enumerate(dialogue):
                        emo = emo_results[i] if i < len(emo_results) else {}
                        
                        is_toxic = emo.get('hostility', 0) > 35
                        is_illogical = emo.get('logic', 100) < 70
                        is_weird = emo.get('adequacy', 100) < 50
                        is_not_serious = emo.get('seriousness', 100) < 40
                        
                        avatar = "👨‍💻" if speaker == 0 else "👤"
                        with st.chat_message(f"Speaker {speaker}", avatar=avatar):
                            if is_toxic: st.error(f"⚠️ Агрессия/Сарказм: {emo.get('summary')}")
                            if is_weird: st.warning(f"🧐 Неадекватность: {emo.get('summary')}")
                            
                            st.write(f"{text}")
                            
                            if is_toxic or is_illogical or is_weird or is_not_serious:
                                st.caption(f"🛡️ **Анализ отклонения:** Логика {emo.get('logic')}% | Серьезность {emo.get('seriousness')}% | Давление {emo.get('pressure')}%")

                with tab_metrics:
                    if len(emo_results) > 0:
                        df = pd.DataFrame(emo_results)
                        
                        avg_adeq = df['adequacy'].mean()
                        col_m1, col_m2, col_m3 = st.columns(3)
                        col_m1.metric("Общая Адекватность", f"{int(avg_adeq)}%")
                        col_m2.metric("Конструктивность", f"{int(df['seriousness'].mean())}%")
                        col_m3.metric("Уровень давления", f"{int(df['pressure'].mean())}%")

                        if len(df) > 1:
                            fig = px.area(df, x="index", y=["adequacy", "hostility", "pressure"], 
                                         title="Эмоциональная карта проекта",
                                         color_discrete_map={"adequacy": "#2ecc71", "hostility": "#e74c3c", "pressure": "#f1c40f"})
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📊 Недостаточно данных для построения графика (всего одна реплика).")

                with tab_tz:
                    if avg_adeq > 60:
                        with st.spinner("Агенты составляют ТЗ..."):
                            tz_result = run_analysis(dialogue, q_key)
                            st.markdown(str(tz_result))
                    else:
                        st.error("❌ Низкая адекватность. ТЗ не сформировано.")

            except Exception as e:
                st.error(f"Ошибка: {e}")
            finally:
                if os.path.exists(temp_fn): os.remove(temp_fn)
