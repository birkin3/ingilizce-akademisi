import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json

# --- 1. API AYARLARI ---
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk"
genai.configure(api_key=API_KEY)

# Hata yapmayan akıllı içerik üretici
def get_lesson_content(level, topic):
    # AI ile bağlanmayı dene
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Sen İngilizce öğretmenisin. Seviye: {level}, Konu: {topic}. 
        Dersi Türkçe anlat. İngilizce örneklerin yanına parantez içinde OKUNUŞUNU yaz.
        Format: TEACHER: [Konuşma] BOARD: [Tahta Notları]"""
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        # EĞER BAĞLANTI HATASI VARSA, YEDEK DERSİ AÇ:
        return f"""TEACHER: Merhaba! Şu an internette küçük bir sorun var ama dersimize engel değil! {topic} konusuna bakalım.
        BOARD: 📝 {topic} (Yedek Mod)
        ---
        1. I am a student (Ay em e stüdınt) : Ben bir öğrenciyim.
        2. You are happy (Yu ar hepi) : Sen mutlusun.
        3. She is a teacher (Şi iz e tiıçır) : O bir öğretmendir.
        ---
        Lütfen bağlantını kontrol et, ben buradayım!"""

# --- 2. DEV MÜFREDAT ---
CURRICULUM = {
    "A1": ["Greetings (Tanışma)", "Present Simple (Geniş Zaman)", "Numbers (Sayılar)"],
    "A2": ["Past Simple (Geçmiş Zaman)", "Future (Gelecek Zaman)"],
    "B1": ["Present Perfect", "Passive Voice"],
    "B2": ["Reported Speech", "Conditionals"],
    "C1-C2": ["Advanced Grammar", "Idioms"]
}

# --- 3. TASARIM (RENKLİ ARKA PLAN) ---
st.set_page_config(layout="wide", page_title="İngilizce Akademisi")
st.markdown("""
<style>
    @keyframes slowRainbow {
        0% { background-color: #e3f2fd; } 25% { background-color: #fff9c4; }
        50% { background-color: #ffccbc; } 75% { background-color: #c8e6c9; }
        100% { background-color: #e3f2fd; }
    }
    .stApp { animation: slowRainbow 60s infinite linear; }
    .blackboard {
        background-color: #1a3a32; color: #fff; border: 12px solid #5d4037;
        padding: 25px; border-radius: 5px; font-family: 'Courier New';
        min-height: 450px; box-shadow: 10px 10px 30px rgba(0,0,0,0.5); font-size: 20px;
    }
    .teacher-bubble {
        background: white; padding: 15px; border-radius: 20px;
        border: 3px solid #4A90E2; color: #333; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DURUM YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "level" not in st.session_state: st.session_state.level = "A1"
if "topic_idx" not in st.session_state: st.session_state.topic_idx = 0

# --- 5. GİRİŞ ---
if not st.session_state.user:
    st.title("🎓 İngilizce Akademisi")
    c1, c2 = st.columns(2)
    if c1.button("Hatice Kübra"): st.session_state.user = "Hatice Kübra"; st.rerun()
    if c2.button("Mehmet Akif"): st.session_state.user = "Mehmet Akif"; st.rerun()
    st.stop()

# --- 6. SOL PANEL ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.session_state.level = st.selectbox("Seviye:", list(CURRICULUM.keys()))
    st.write("---")
    topics = CURRICULUM[st.session_state.level]
    st.session_state.topic_idx = st.radio("Konular:", range(len(topics)), format_func=lambda x: topics[x])
    
    if st.button("🚪 Çıkış"): st.session_state.user = None; st.rerun()

# --- 7. DERS EKRANI ---
current_topic = topics[st.session_state.topic_idx]
lesson_data = get_lesson_content(st.session_state.level, current_topic)

col_b, col_t = st.columns([3, 1])

with col_b:
    # Kara Tahta
    b_text = lesson_data.split("BOARD:")[1] if "BOARD:" in lesson_data else lesson_data
    st.markdown(f'<div class="blackboard">{b_text}</div>', unsafe_allow_html=True)
    
    # Soru Kutusu
    u_q = st.chat_input
