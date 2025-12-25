import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json
import os
import time

# --- 1. API VE MODEL AYARLARI ---
# BURAYA ÇALIŞAN ANAHTARINI YAPIŞTIR
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk"
genai.configure(api_key=API_KEY)

# En sağlam modeli bulan fonksiyon (Bunu koruyoruz çünkü çalıştı!)
@st.cache_resource
def get_working_model():
    model_list = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']
    for m_name in model_list:
        try:
            m = genai.GenerativeModel(m_name)
            m.generate_content("test")
            return m
        except: continue
    return None

model = get_working_model()

# --- 2. MÜFREDAT VE VERİTABANI ---
# Sol menüde görünecek konular
CURRICULUM = {
    "A1": [
        "Unit 1: Tanışma (Greetings)",
        "Unit 2: Sayılar ve Renkler",
        "Unit 3: Ailem (My Family)",
        "Unit 4: Günlük Rutinler",
        "Unit 5: Yiyecek ve İçecekler"
    ],
    # A2, B1 gibi seviyeler buraya eklenebilir...
}

DB_FILE = "academy_progress.json"

def load_data():
    defaults = {"users": {
        "Hatice Kübra": {"lvl": "A1", "unit_idx": 0, "history": []},
        "Mehmet Akif": {"lvl": "A1", "unit_idx": 0, "history": []}
    }}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return defaults
    return defaults

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

# --- 3. GÖRSEL TASARIM (CSS) ---
# Arka plan animasyonu, Kara Tahta ve Öğretmen Balonu stilleri
st.markdown("""
<style>
    /* Çok yavaş renk değiştiren arka plan */
    @keyframes dreamyBackground {
        0% { background-color: #eef2f3; color: #333; } /* Açık Mavi tonu */
        33% { background-color: #fff9c4; color: #333; } /* Açık Sarı tonu */
        66% { background-color: #ffccbc; color: #333; } /* Açık Kırmızı/Turuncu tonu */
        100% { background-color: #eef2f3; color: #333; }
    }
    .stApp {
        animation: dreamyBackground 60s linear infinite;
    }
    
    /* Kara Tahta Tasarımı (Dikey dikdörtgen) */
    .chalkboard {
        background-color: #1a3a32; /* Koyu yeşil */
        color: #f0f0f0; /* Tebeşir beyazı */
        border: 15px solid #5d3a1a; /* Ahşap çerçeve */
        padding: 30px;
        border-radius: 8px;
        font-family: 'Comic Sans MS', 'Brush Script MT', cursive; /* Tebeşir yazısı fontu */
        min-height: 500px; /* Yüksekliği kısa kenarından uzun */
        box-shadow: 5px 5px 20px rgba(0,0,0,0.6);
        margin-bottom: 20px;
        white-space: pre-wrap; /* Satır başlarını koru */
    }
    
    /* Öğretmen Konuşma Balonu */
    .teacher-bubble {
        background: white;
        color: black;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        position: relative;
        font-family: sans-serif;
        margin-top: 20px;
    }
    .teacher-bubble::after {
        content: ''; position: absolute; top: 20px; left: -10px;
        border-width: 10px 10px 0; border-style: solid; border-color: white transparent;
    }
    
    /* Sohbet Giriş Kutusu Stili */
    .stChatInput {
        position: fixed;
        bottom: 20px;
        width: 50%; /* Tahtanın altında ortala */
        left: 25%;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. GİRİŞ EKRANI ---
data = load_data()
if "user" not in st.session_state:
    st.title("🏫 Yapay Zeka Sınıfı")
    st.write("Lütfen sıranıza geçin...")
    u_list = list(data["users"].keys())
    sel_user = st.selectbox("Öğrenci:", u_list)
    if st.button("Derse Başla 🔔"):
        st.session_state.user = sel_user
        st.rerun()
    st.stop()

# --- 5. ANA ARAYÜZ ---
u_name = st.session_state.user
u_data = data["users"][u_name]
curr_lvl = u_data["lvl"]
curr_idx = u_data["unit_idx"]
topics = CURRICULUM[curr_lvl]
current_topic = topics[curr_idx] if curr_idx < len(topics) else "Tebrikler! Seviye Bitti."

# --- SOL SÜTUN (Müfredat) ---
with st.sidebar:
    st.title(f"👤 {u_name}")
    st.header(f"📊 Seviye: {curr_lvl}")
    st.divider()
    st.write("### 📚 Konu Takibi")
    for i, topic in enumerate(topics):
        if i == curr_idx:
            st.markdown(f"👉 **{topic}** (Şu anki konu)")
        elif i < curr_idx:
            st.markdown(f"✅ ~{topic}~")
        else:
            st.markdown(f"🔒 {topic}")
    
    st.divider()
    if st.button("Sonraki Konuya Geç ➡️"):
        if curr_idx < len(topics) - 1:
            data["users"][u_name]["unit_idx"] += 1
            # Yeni konuya geçince geçmişi temizle ki yeni ders başlasın
            data["users"][u_name]["history"] = [] 
            save_data(data)
            st.rerun()
        else:
            st.success("Bu seviyenin son konusundasınız!")

    if st.button("🚪 Çıkış Yap"):
        del st.session_state.user
        st.rerun()

# --- ORTA VE SAĞ SÜTUN (Sınıf Ortamı) ---
# Düzen: Orta (Tahta) - Sağ (Öğretmen)
col_board, col_teacher = st.columns([3, 1.5])

# Sohbet Geçmişini Yönet
if "history" not in u_data: u_data["history"] = []

# İlk açılışta dersi başlat
if not u_data["history"]:
    initial_prompt = f"Sen bir İngilizce öğretmenisin. Öğrenci: {u_name}. Seviye: {curr_lvl}. Konu: {current_topic}. Bu konuyu anlatmaya başla. Çıktıyı ikiye ayır: TEACHER: [Öğrenciyle samimi konuşman] BOARD: [Tahtaya tebeşirle yazılacak özet notlar, maddeler halinde]."
    
    if model:
        try:
            res = model.generate_content(initial_prompt)
            u_data["history"].append({"role": "model", "parts": [res.text]})
            save_data(data)
        except Exception as e: st.error(f"AI Hatası: {e}")

# KULLANICI SORU SORARSA
prompt = st.chat_input("Hocaya bir soru sor veya cevap ver...")
if prompt:
    # Kullanıcı mesajını ekle
    u_data["history"].append({"role": "user", "parts": [prompt]})
    
    # AI'ya bağlamı hatırlat ve cevap iste
    context_prompt = f"Öğrenci ({u_name}, {curr_lvl} seviyesi, Konu: {current_topic}) sana şunu yazdı: '{prompt}'. Buna bir öğretmen olarak cevap ver. Yine TEACHER: [Konuşman] ve BOARD: [Varsa tahtaya eklenecekler, yoksa boş bırak] formatını kullan."
    
    if model:
        try:
            res = model.generate_content(context_prompt)
            u_data["history"].append({"role": "model", "parts": [res.text]})
            save_data(data)
            st.rerun() # Ekranı yenile
        except Exception as e: st.error(f"AI Cevap Veremedi: {e}")

# EN SON GELEN AI CEVABINI AYIKLA VE GÖSTER
last_ai_response = next((msg["parts"][0] for msg in reversed(u_data["history"]) if msg["role"] == "model"), "")

teacher_says = ""
board_writes = ""

if "TEACHER:" in last_ai_response and "BOARD:" in last_ai_response:
    parts = last_ai_response.split("BOARD:")
    teacher_says = parts[0].replace("TEACHER:", "").strip()
    board_writes = parts[1].strip()
elif "TEACHER:" in last_ai_response:
    teacher_says = last_ai_response.replace("TEACHER:", "").strip()
elif last_ai_response:
    teacher_says = last_ai_response # Format uymazsa direkt konuşma kabul et

# --- EKRANA YERLEŞTİRME ---

with col_board:
    # Ortada Kara Tahta
    st.markdown(f"""
    <div class="chalkboard">
        {board_writes if board_writes else "..."}
    </div>
    """, unsafe_allow_html=True)

with col_teacher:
    # Sağda Öğretmen ve Balonu
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg", width=200)
    st.write("👩‍🏫 **Miss Sarah**")
    
    if teacher_says:
        st.markdown(f'<div class="teacher-bubble">{teacher_says}</div>', unsafe_allow_html=True)
        # Seslendirme Butonu
        if st.button("🔊 Dinle", key=f"tts_{len(u_data['history'])}"):
            tts = gTTS(text=teacher_says, lang='en' if 'How are you' in teacher_says else 'tr')
            fp = BytesIO(); tts.write_to_fp(fp)
            st.audio(fp)
