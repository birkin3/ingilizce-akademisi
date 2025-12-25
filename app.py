import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json
import os

# --- 1. API AYARLARI ---
API_KEY = "BURAYA_YENI_ANAHTARINI_YAPISTIR" 
genai.configure(api_key=API_KEY)

# Hangi modelin çalıştığını otomatik tespit eden fonksiyon
@st.cache_resource
def get_working_model():
    try:
        # Önce sistemde hangi modellerin senin anahtarınla açık olduğunu listele
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Tercih sıramız
        preferences = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        
        for pref in preferences:
            if pref in available_models:
                return genai.GenerativeModel(pref)
        
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"API Listeleme Hatası: {e}")
    return None

model = get_working_model()

# --- 2. VERİTABANI VE VARSAYILAN KULLANICILAR ---
DB_FILE = "user_progress.json"

def load_data():
    default_data = {
        "users": {
            "Hatice Kübra": {"level": "A1", "unit": 1, "lesson": 1, "score": 0},
            "Mehmet Akif": {"level": "A1", "unit": 1, "lesson": 1, "score": 0}
        }
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Varsayılan kullanıcılar silinmişse geri ekle
                for user in default_data["users"]:
                    if user not in saved["users"]:
                        saved["users"][user] = default_data["users"][user]
                return saved
        except: return default_data
    return default_data

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# CSS Tasarımı (Kara Tahta ve Balon)
st.markdown("""
<style>
    .blackboard { background-color: #1a3a32; color: #f0f0f0; border: 12px solid #5d3a1a; padding: 25px; border-radius: 5px; font-family: 'Arial'; min-height: 280px; margin: 15px 0; box-shadow: inset 0 0 50px #000; }
    .bubble { background-color: white; color: black; padding: 20px; border-radius: 30px; border: 2px solid #ff4b4b; position: relative; margin-bottom: 15px; font-size: 18px; }
    .bubble::after { content: ''; position: absolute; left: 30px; bottom: -20px; border-width: 20px 20px 0; border-style: solid; border-color: white transparent; }
</style>
""", unsafe_allow_html=True)

# --- 3. GİRİŞ EKRANI ---
data = load_data()

if "current_user" not in st.session_state:
    st.title("🎓 İngilizce Akademisi - Hoş Geldiniz")
    
    # Kullanıcı Listesi
    user_list = list(data["users"].keys())
    selected = st.selectbox("Lütfen Öğrenci Seçin:", user_list)
    
    if st.button("Dersi Başlat 🚀"):
        st.session_state.current_user = selected
        st.rerun()
    
    st.divider()
    # Yeni Öğrenci Ekleme
    with st.expander("➕ Yeni Öğrenci Kaydet"):
        new_name = st.text_input("Öğrenci Adı:")
        if st.button("Kaydı Tamamla"):
            if new_name and new_name not in data["users"]:
                data["users"][new_name] = {"level": "A1", "unit": 1, "lesson": 1, "score": 0}
                save_data(data)
                st.success(f"{new_name} başarıyla eklendi!")
                st.rerun()
    st.stop()

# --- 4. DERS EKRANI ---
u_name = st.session_state.current_user
u_info = data["users"][u_name]

# Sidebar Bilgileri
st.sidebar.title(f"👤 {u_name}")
st.sidebar.header(f"Seviye: {u_info['level']}")
st.sidebar.subheader(f"Ünite: {u_info['unit']} | Ders: {u_info['lesson']}")
st.sidebar.metric("⭐ Başarı Puanı", u_info['score'])

if st.sidebar.button("🚪 Başka Öğrenci Seç"):
    del st.session_state.current_user
    st.rerun()

# AI İçerik Üretimi
@st.cache_data(show_spinner="Öğretmen tahtayı hazırlıyor...")
def get_ai_lesson(level, unit, lesson):
    if model is None: return "ERROR: API bağlantısı kurulamadı."
    prompt = f"""
    Sen 2D karakter olan bir İngilizce öğretmenisin. 
    Öğrenci: {u_name}, Seviye: {level}, Ünite: {unit}, Ders: {lesson}.
    1. 'TEACHER:' etiketiyle konuşma balonunda söyleyeceğin neşeli bir giriş yap.
    2. 'BOARD:' etiketiyle kara tahtaya yazılacak ders konusunu, örnek cümleleri ve kelimeleri anlat (Markdown kullan).
    3. 'QUIZ:' etiketiyle ders sonunda 5 adet test sorusu sor. Format: Soru | A) | B) | C) | DoğruCevap(A/B/C)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"Hata: {str(e)}"

content = get_ai_lesson(u_info['level'], u_info['unit'], u_info['lesson'])

if "ERROR" in content or "Hata" in content:
    st.error("Bağlantı Sorunu: API anahtarınız henüz aktifleşmemiş olabilir veya bir kısıtlama var.")
    st.info("Lütfen 5 dakika bekleyip 'Reboot App' yapın.")
else:
    # Görsel Düzen (Öğretmen ve Balon)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.freepik.com/free-vector/teacher-character-collection_23-2148519532.jpg", width=160)
        st.write("👩‍🏫 **Ms. Emily**")
    
    with col2:
        teacher_msg = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
        st.markdown(f'<div class="bubble">{teacher_msg}</div>', unsafe_allow_html=True)
        if st.button("🔊 Öğretmeni Sesli Dinle"):
            tts = gTTS(text=teacher_msg, lang='en')
            fp = BytesIO(); tts.write_to_fp(fp)
            st.audio(fp)

    # Kara Tahta
    board_content = content.split("BOARD:")[1].split("QUIZ:")[0].strip()
    st.markdown(f'<div class="blackboard">{board_content}</div>', unsafe_allow_html=True)

    # Test Bölümü
    with st.expander("📝 Dersi Bitirmek İçin Soruları Çöz"):
        quiz_lines = content.split("QUIZ:")[1].strip().split("\n")
        correct_count = 0
        for i, q in enumerate(quiz_lines):
            if "|" in q:
                p = q.split("|")
                choice = st.radio(p[0], [p[1], p[2], p[3]], key=f"q_{i}")
                if p[4].strip() in choice: correct_count += 1
        
        if st.button("Cevapları Gönder"):
            points = correct_count * 10
            data["users"][u_name]["score"] += points
            save_data(data)
            st.balloons()
            st.success(f"Tebrikler! {points} puan kazandın.")

    # Navigasyon
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("⬅️ Önceki Ders") and u_info['lesson'] > 1:
            data["users"][u_name]["lesson"] -= 1
            save_data(data); st.rerun()
    with nav3:
        if st.button("Sonraki Ders ➡️"):
            data["users"][u_name]["lesson"] += 1
            if data["users"][u_name]["lesson"] > 5:
                data["users"][u_name]["lesson"] = 1
                data["users"][u_name]["unit"] += 1
            save_data(data); st.rerun()
