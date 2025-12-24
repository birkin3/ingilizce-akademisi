import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json
import os

# --- 1. AYARLAR VE API ---
API_KEY = "AIzaSyDIzvdFif990ghFmAvDJhkpz0greTeQmNo" 
genai.configure(api_key=API_KEY)

# Hangi modelin çalıştığını otomatik bulan akıllı fonksiyon
@st.cache_resource
def get_best_model():
    # Google'ın kabul edebileceği tüm farklı model yazım şekilleri
    possible_models = [
        'gemini-1.5-flash', 
        'models/gemini-1.5-flash', 
        'gemini-pro', 
        'models/gemini-pro'
    ]
    
    for model_name in possible_models:
        try:
            m = genai.GenerativeModel(model_name)
            # Modeli test et (boş cevap dönse de hata vermemesi lazım)
            m.generate_content("test") 
            return m
        except:
            continue
    return None

model = get_best_model()
DB_FILE = "user_data.json"

# --- 2. VERİ YÖNETİMİ ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {"users": {}}
    return {"users": {}}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# Tasarım Ayarları
st.markdown("""
<style>
    .blackboard { background-color: #1a3a32; color: white; border: 8px solid #5d3a1a; padding: 20px; border-radius: 10px; font-family: 'Comic Sans MS'; min-height: 250px; margin: 10px 0; }
    .bubble { background-color: #e8f4f8; color: #333; padding: 15px; border-radius: 20px; border: 1px solid #bce8f1; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. GİRİŞ EKRANI ---
data = load_data()

if "current_user" not in st.session_state:
    st.title("🎓 İngilizce Akademisi")
    
    with st.expander("➕ Yeni Öğrenci Ekle"):
        new_name = st.text_input("Öğrenci Adı:")
        if st.button("Sisteme Kaydet"):
            if new_name and new_name not in data["users"]:
                data["users"][new_name] = {"level": "A1", "unit": 1, "lesson": 1, "score": 0}
                save_data(data)
                st.success("Kaydedildi!")

    user_list = list(data["users"].keys())
    if user_list:
        selected = st.selectbox("Profil Seçin:", user_list)
        if st.button("Derslere Gir 🚀"):
            st.session_state.current_user = selected
            st.rerun()
    st.stop()

# --- 4. DERS AKIŞI ---
u_name = st.session_state.current_user
u_info = data["users"][u_name]

st.sidebar.title(f"👤 {u_name}")
st.sidebar.info(f"Seviye: {u_info['level']} | Ünite: {u_info['unit']}")
st.sidebar.metric("⭐ Puan", u_info['score'])

if st.sidebar.button("🚪 Çıkış"):
    del st.session_state.current_user
    st.rerun()

@st.cache_data(show_spinner="Öğretmen ders hazırlıyor...")
def generate_lesson(level, unit, lesson):
    if model is None: return "ERROR: Model bulunamadı."
    prompt = f"Sen öğretmensin. Seviye:{level}, Ünite:{unit}, Ders:{lesson}. Önce TEACHER: etiketiyle konuşma balonuna kısa giriş yaz. Sonra BOARD: etiketiyle tahtaya dersi anlat. En son QUIZ: etiketiyle 1 soru sor."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Hata: {str(e)}"

content = generate_lesson(u_info['level'], u_info['unit'], u_info['lesson'])

# EKRAN TASARIMI
if "Hata:" in content or "ERROR" in content:
    st.error("API bağlantısı kurulamadı. Lütfen anahtarınızı kontrol edip 'Reboot App' yapın.")
else:
    # Öğretmen ve Balon
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://img.freepik.com/free-vector/teacher-character-collection_23-2148519532.jpg", width=120)
    with col2:
        t_text = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
        st.markdown(f'<div class="bubble">{t_text}</div>', unsafe_allow_html=True)
        if st.button("🔊 Dinle"):
            tts = gTTS(text=t_text, lang='en')
            fp = BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp)

    # Tahta
    b_text = content.split("BOARD:")[1].split("QUIZ:")[0].strip()
    st.markdown(f'<div class="blackboard">{b_text}</div>', unsafe_allow_html=True)

    # İlerleme Butonları
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ Geri") and u_info['lesson'] > 1:
            data["users"][u_name]["lesson"] -= 1
            save_data(data); st.rerun()
    with c3:
        if st.button("İleri ➡️"):
            data["users"][u_name]["lesson"] += 1
            save_data(data); st.rerun()
