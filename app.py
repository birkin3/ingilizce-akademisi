import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json
import os

# --- 1. AYARLAR VE VERİTABANI ---
API_KEY = "AIzaSyAl-0pGFUf5O2cI0O43ZUTXKU_sNPF6rRk" # Buraya kimseyle paylaşmadığın anahtarı koy
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

DB_FILE = "user_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# CSS ile Kara Tahta ve Konuşma Balonu Tasarımı
st.markdown("""
<style>
    .blackboard {
        background-color: #1a3a32;
        color: white;
        border: 10px solid #5d3a1a;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Patrick Hand', cursive;
        min-height: 300px;
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .bubble {
        background-color: #f1f1f1;
        color: black;
        padding: 15px;
        border-radius: 20px;
        position: relative;
        margin-bottom: 20px;
        border: 2px solid #ddd;
    }
    .teacher-img {
        border-radius: 50%;
        border: 3px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. GİRİŞ VE KULLANICI YÖNETİMİ ---
data = load_data()

if "current_user" not in st.session_state:
    st.title("🎓 İngilizce Akademisi Giriş")
    
    # Yeni Kullanıcı Ekleme
    with st.expander("➕ Yeni Öğrenci Ekle"):
        new_name = st.text_input("Öğrenci Adı:")
        if st.button("Kaydet"):
            if new_name and new_name not in data["users"]:
                data["users"][new_name] = {"level": "A1", "unit": 1, "lesson": 1, "score": 0}
                save_data(data)
                st.success(f"{new_name} eklendi! Şimdi giriş yapabilirsiniz.")
    
    # Mevcut Kullanıcı Seçimi
    user_list = list(data["users"].keys())
    if user_list:
        selected_user = st.selectbox("Profil Seçin:", user_list)
        if st.button("Derse Başla 🚀"):
            st.session_state.current_user = selected_user
            st.rerun()
    st.stop()

# --- 3. DERS MANTIĞI VE NAVİGASYON ---
u_name = st.session_state.current_user
u_info = data["users"][u_name]

# Yan Menü (Sidebar)
with st.sidebar:
    st.header(f"👤 {u_name}")
    st.info(f"📍 Mevcut Seviye: {u_info['level']}")
    st.progress(u_info['unit'] / 10)
    st.write(f"**Ünite:** {u_info['unit']} | **Ders:** {u_info['lesson']}")
    st.metric("⭐ Toplam Puan", u_info['score'])
    
    if st.button("🚪 Çıkış Yap"):
        del st.session_state.current_user
        st.rerun()

# Ders İçeriği Oluşturma (AI)
@st.cache_data
def get_lesson_content(level, unit, lesson):
    prompt = f"""
    Sen bir İngilizce öğretmenisin. Seviye: {level}, Ünite: {unit}, Ders: {lesson} için bir ders hazırla.
    Format şu şekilde olsun:
    TEACHER: [Öğretmenin konuşma balonunda söyleyeceği kısa giriş cümlesi]
    BOARD: [Kara tahtada yazacak ders özeti, kurallar ve örnekler. Markdown kullan.]
    IMAGE: [Dersle ilgili bir anahtar kelime]
    QUIZ: [Dersle ilgili 3 adet çoktan seçmeli soru. Soru | A) | B) | C) | DoğruŞık(A/B/C) formatında]
    """
    response = model.generate_content(prompt)
    return response.text

content = get_lesson_content(u_info['level'], u_info['unit'], u_info['lesson'])

# --- 4. GÖRSEL ARAYÜZ (TEACHER & BOARD) ---
col1, col2 = st.columns([1, 3])

with col1:
    # 2D Öğretmen Görseli
    st.image("https://img.freepik.com/free-vector/teacher-character-collection_23-2148519532.jpg", width=150)
    st.write("👩‍🏫 **Teacher**")

with col2:
    # Konuşma Balonu
    teacher_text = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
    st.markdown(f'<div class="bubble">{teacher_text}</div>', unsafe_allow_html=True)

# Kara Tahta
board_text = content.split("BOARD:")[1].split("IMAGE:")[0].strip()
st.markdown(f'<div class="blackboard">{board_text}</div>', unsafe_allow_html=True)

# Görselleştirme
try:
    img_keyword = content.split("IMAGE:")[1].split("QUIZ:")[0].strip()
    st.image(f"https://loremflickr.com/600/300/{img_keyword}", caption=f"Visual: {img_keyword}")
except: pass

# --- 5. TEST VE İLERLEME ---
st.divider()
st.subheader("📝 Küçük Test")
quiz_section = content.split("QUIZ:")[1].strip().split("\n")

for q in quiz_section:
    if "|" in q:
        parts = q.split("|")
        st.write(parts[0])
        ans = st.radio("Cevabını seç:", [parts[1], parts[2], parts[3]], key=q)
        if st.button("Kontrol Et", key=f"btn_{q}"):
            if parts[4].strip() in ans:
                st.success("Doğru! +10 Puan")
                data["users"][u_name]["score"] += 10
                save_data(data)
            else:
                st.error("Yanlış, tekrar dene!")

# İleri - Geri Butonları
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("⬅️ Geri"):
        if u_info['lesson'] > 1:
            data["users"][u_name]["lesson"] -= 1
            save_data(data)
            st.rerun()

with c3:
    if st.button("İleri ➡️"):
        data["users"][u_name]["lesson"] += 1
        if data["users"][u_name]["lesson"] > 5: # 5 derste bir ünite atlasın
            data["users"][u_name]["lesson"] = 1
            data["users"][u_name]["unit"] += 1
        save_data(data)
        st.rerun()

# Seslendirme
if st.button("🔊 Öğretmeni Dinle"):
    tts = gTTS(text=teacher_text, lang='en')
    sound_file = BytesIO()
    tts.write_to_fp(sound_file)
    st.audio(sound_file)

