import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json
import os
import time

# --- 1. API AYARLARI ---
# BURAYA ÇALIŞAN API ANAHTARINI YAPIŞTIR
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk"
genai.configure(api_key=API_KEY)

# Modeli Bulma (Hata Önleyici)
@st.cache_resource
def get_model():
    models = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            model.generate_content("Hi")
            return model
        except: continue
    return None

model = get_model()

# --- 2. MÜFREDAT ---
TOPICS = [
    "Unit 1: Tanışma (Greetings & Introduction)",
    "Unit 2: Sayılar ve Renkler (Numbers & Colors)",
    "Unit 3: Ailem (My Family)",
    "Unit 4: Okul Eşyaları (School Objects)",
    "Unit 5: Vücudumuz (My Body)",
    "Unit 6: Yiyecekler (Food & Drinks)",
    "Unit 7: Günlük Rutinler (Daily Routines)",
    "Unit 8: Kıyafetler (Clothes)",
    "Unit 9: Duygular (Feelings)",
    "Unit 10: Hava Durumu (Weather)"
]

# --- 3. VERİTABANI VE TASARIM ---
if "user_data" not in st.session_state:
    st.session_state.user_data = {"name": "", "score": 0, "current_unit": 0}
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "lesson" # lesson veya quiz
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "lesson_content" not in st.session_state:
    st.session_state.lesson_content = {}

# CSS Tasarımı (Animasyonlu Arka Plan & Tahta)
st.markdown("""
<style>
    @keyframes slowColors {
        0% { background-color: #e3f2fd; }
        25% { background-color: #fffde7; }
        50% { background-color: #fbe9e7; }
        75% { background-color: #e8f5e9; }
        100% { background-color: #e3f2fd; }
    }
    .stApp { animation: slowColors 60s infinite alternate; }
    
    .chalkboard {
        background-color: #1a3a32; color: white; border: 15px solid #5d4037;
        padding: 25px; border-radius: 8px; font-family: 'Comic Sans MS', cursive;
        min-height: 400px; box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        font-size: 18px; line-height: 1.6;
    }
    .chalkboard strong { color: #FFD700; } /* Önemli kelimeler sarı */
    
    .teacher-bubble {
        background: #fff; padding: 15px; border-radius: 20px;
        border: 2px solid #2196F3; position: relative; color: #333;
        font-family: sans-serif; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .teacher-bubble::after {
        content: ''; position: absolute; top: 20px; left: -10px;
        border-width: 10px 10px 0; border-style: solid; border-color: #fff transparent;
    }
    .active-unit { color: #1565C0; font-weight: bold; border-left: 4px solid #1565C0; padding-left: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.user_data["name"]:
    st.title("🎓 İngilizce Sınıfı")
    st.write("Sınıfa girmek için lütfen profilini seç:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Hatice Kübra"):
            st.session_state.user_data["name"] = "Hatice Kübra"
            st.rerun()
    with c2:
        if st.button("Mehmet Akif"):
            st.session_state.user_data["name"] = "Mehmet Akif"
            st.rerun()
    st.stop()

# --- 5. İÇERİK ÜRETİCİLER (AI) ---
def generate_lesson(topic):
    prompt = f"""
    Sen harika bir İngilizce öğretmenisin. Öğrenci: {st.session_state.user_data['name']}. Konu: {topic}.
    
    1. **TEACHER:** Öğrenciye Türkçe samimi bir giriş yap. Konuyu anlat. İngilizce cümle kurduğunda hemen yanına Türkçe anlamını ekle. 
       Örnek: "I am a teacher (Ben bir öğretmenim)."
    
    2. **BOARD:** Kara tahta için ders notları hazırla. 
       KURAL: İngilizce kelimelerin yanına mutlaka parantez içinde TÜRKÇE OKUNUŞUNU ve anlamını yaz.
       Format: `Word (Okunuşu) : Anlamı`
       Örnek: `Apple (Epıl) : Elma`
       
    Çıktı formatı şöyle olsun:
    TEACHER: [Konuşman]
    BOARD: [Tahta Notları]
    """
    try:
        res = model.generate_content(prompt)
        return res.text
    except: return "TEACHER: Bağlantı hatası.\nBOARD: Lütfen sayfayı yenile."

def generate_quiz(topic):
    prompt = f"""
    Konu: {topic}. Seviye: A1 (Başlangıç).
    Bu konuyla ilgili tam 15 tane çoktan seçmeli soru hazırla.
    Format JSON listesi olsun:
    [
      {{"q": "Soru metni", "options": ["A) ...", "B) ...", "C) ..."], "answer": "A) ..."}},
      ...
    ]
    Sadece JSON döndür.
    """
    try:
        res = model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except: return []

# --- 6. SAYFA DÜZENİ ---
u_name = st.session_state.user_data["name"]
u_unit = st.session_state.user_data["current_unit"]
current_topic = TOPICS[u_unit]

# Sidebar
with st.sidebar:
    st.header(f"👤 {u_name}")
    st.metric("Puan", st.session_state.user_data["score"])
    st.divider()
    st.subheader("📚 Konular")
    for i, t in enumerate(TOPICS):
        if i == u_unit: st.markdown(f'<div class="active-unit">👉 {t}</div>', unsafe_allow_html=True)
        elif i < u_unit: st.markdown(f"✅ ~~{t}~~")
        else: st.markdown(f"🔒 {t}")
    
    if st.button("Çıkış Yap"):
        st.session_state.user_data["name"] = ""
        st.rerun()

# Ana Ekran
if st.session_state.app_mode == "lesson":
    # DERS MODU
    col_board, col_teacher = st.columns([3, 1.5])
    
    # İçerik yoksa veya konu değiştiyse oluştur
    if current_topic not in st.session_state.lesson_content:
        with st.spinner("Öğretmen derse hazırlanıyor..."):
            st.session_state.lesson_content[current_topic] = generate_lesson(current_topic)
    
    content = st.session_state.lesson_content[current_topic]
    
    # İçeriği ayrıştır
    try:
        teacher_text = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
        board_text = content.split("BOARD:")[1].strip()
    except:
        teacher_text = "Hoş geldin! Derse başlayalım."
        board_text = "Notes..."

    with col_board:
        st.markdown(f'<div class="chalkboard">{board_text}</div>', unsafe_allow_html=True)
        
        # Sohbet Çubuğu (Öğrenci Soru Sorarsa)
        user_msg = st.chat_input("Öğretmene bir soru sor...")
        if user_msg:
            with st.spinner("Öğretmen cevap veriyor..."):
                reply = model.generate_content(f"Öğrenci sorusu: {user_msg}. Sen öğretmensin, kısa ve net açıkla.").text
                st.info(f"🗣️ **Sen:** {user_msg}")
                st.success(f"👩‍🏫 **Öğretmen:** {reply}")

    with col_teacher:
        st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg", width=200)
        st.write("👩‍🏫 **Miss Sarah**")
        st.markdown(f'<div class="teacher-bubble">{teacher_text}</div>', unsafe_allow_html=True)
        
        if st.button("🔊 Dersi Dinle"):
            tts = gTTS(teacher_text, lang='tr')
            audio = BytesIO()
            tts.write_to_fp(audio)
            st.audio(audio)
        
        st.divider()
        if st.button("📝 SINAVI BAŞLAT (15 Soru)"):
            st.session_state.app_mode = "quiz"
            st.session_state.quiz_data = [] # Sıfırla
            st.rerun()

elif st.session_state.app_mode == "quiz":
    # SINAV MODU
    st.title(f"📝 {current_topic} - Sınavı")
    
    if not st.session_state.quiz_data:
        with st.spinner("Sorular hazırlanıyor (Bu biraz sürebilir)..."):
            st.session_state.quiz_data = generate_quiz(current_topic)
    
    if not st.session_state.quiz_data:
        st.error("Sorular yüklenemedi. Tekrar dene.")
        if st.button("Geri Dön"): st.session_state.app_mode = "lesson"; st.rerun()
    else:
        # Soruları Göster
        score_temp = 0
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.write(f"**{i+1}. {q['q']}**")
                choice = st.radio(f"Cevap {i+1}", q['options'], key=f"q{i}")
                if choice == q['answer']:
                    score_temp += 1
            
            submitted = st.form_submit_button("Sınavı Bitir")
            if submitted:
                st.success(f"Sonuç: 15 soruda {score_temp} doğru yaptın!")
                if score_temp >= 8: # Geçme notu
                    st.balloons()
                    st.session_state.user_data["score"] += (score_temp * 10)
                    if st.session_state.user_data["current_unit"] < len(TOPICS) - 1:
                        st.session_state.user_data["current_unit"] += 1
                        st.session_state.app_mode = "lesson"
                        st.info("Tebrikler! Bir sonraki üniteye geçtin. 5 saniye içinde yönlendiriliyorsun...")
                        time.sleep(5)
                        st.rerun()
                else:
                    st.error("Yeterli doğru yapamadın. Konuyu tekrar çalışmalısın.")
                    if st.button("Tekrar Dene"):
                        st.session_state.app_mode = "lesson"
                        st.rerun()
