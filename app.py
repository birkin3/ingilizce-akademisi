import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json

# --- 1. API VE MODEL ---
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk"
genai.configure(api_key=API_KEY)

def get_ai_response(prompt):
    models = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            return model.generate_content(prompt).text
        except: continue
    return "ERROR"

# --- 2. DEV MÜFREDAT (A1 - C2) ---
CURRICULUM = {
    "A1 (Başlangıç)": [
        "Greetings & Verb To Be (Am/Is/Are)",
        "Numbers, Colors & Family",
        "Present Simple (Geniş Zaman - I work)",
        "Present Continuous (Şimdiki Zaman - I am working)",
        "Basic Verbs & Daily Routines"
    ],
    "A2 (Temel)": [
        "Past Simple (Geçmiş Zaman - I worked)",
        "Future Simple (Gelecek Zaman - Will/Going to)",
        "Comparative & Superlative (Sıfat Karşılaştırma)",
        "Modal Verbs (Can, Must, Should)",
        "Countable & Uncountable Nouns"
    ],
    "B1 (Orta Öncesi)": [
        "Present Perfect (Belirsiz Geçmiş Zaman - I have worked)",
        "Past Continuous (Geçmişte Süreklilik)",
        "Relative Clauses (Who, Which, That)",
        "Passive Voice (Edilgen Yapı)",
        "First Conditional (Koşul Cümleleri - Type 1)"
    ],
    "B2 (Orta Üstü)": [
        "Past Perfect (Öncesi Geçmiş Zaman)",
        "Modal Verbs in the Past",
        "Reported Speech (Dolaylı Anlatım)",
        "Gerunds & Infinitives",
        "Second & Third Conditionals"
    ],
    "C1-C2 (İleri)": [
        "Advanced Inversion (Devrik Cümleler)",
        "Subjunctive Mood & Formal English",
        "Academic Writing & Idioms",
        "Complex Sentence Structures",
        "Advanced Phrasal Verbs"
    ]
}

# --- 3. TASARIM VE DURUM YÖNETİMİ ---
st.set_page_config(layout="wide")

if "user" not in st.session_state: st.session_state.user = None
if "level" not in st.session_state: st.session_state.level = "A1 (Başlangıç)"
if "topic_idx" not in st.session_state: st.session_state.topic_idx = 0
if "cache" not in st.session_state: st.session_state.cache = {}

st.markdown("""
<style>
    @keyframes slowRainbow {
        0% { background-color: #f0f4f8; }
        50% { background-color: #fff9db; }
        100% { background-color: #f0f4f8; }
    }
    .stApp { animation: slowRainbow 40s ease infinite; }
    .blackboard {
        background-color: #0d2b21; color: #fdfdfd; border: 12px solid #5d4037;
        padding: 25px; border-radius: 5px; font-family: 'Courier New', monospace;
        min-height: 480px; box-shadow: 10px 10px 30px rgba(0,0,0,0.5); font-size: 19px;
    }
    .teacher-bubble {
        background: white; padding: 18px; border-radius: 20px;
        border: 3px solid #4A90E2; color: #333; font-weight: bold; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.user:
    st.title("👨‍🏫 İngilizce Akademisi'ne Hoş Geldin!")
    st.subheader("Lütfen öğrenci profilini seç:")
    cols = st.columns(2)
    if cols[0].button("👩‍🎓 Hatice Kübra"): st.session_state.user = "Hatice Kübra"; st.rerun()
    if cols[1].button("👨‍🎓 Mehmet Akif"): st.session_state.user = "Mehmet Akif"; st.rerun()
    st.stop()

# --- 5. YAN MENÜ (NAVİGASYON) ---
with st.sidebar:
    st.title(f"🎓 {st.session_state.user}")
    # Seviye Seçimi
    new_level = st.selectbox("Seviye Seç:", list(CURRICULUM.keys()), index=list(CURRICULUM.keys()).index(st.session_state.level))
    if new_level != st.session_state.level:
        st.session_state.level = new_level
        st.session_state.topic_idx = 0
        st.rerun()
    
    st.divider()
    topics = CURRICULUM[st.session_state.level]
    for i, t in enumerate(topics):
        if i == st.session_state.topic_idx: st.success(f"📖 {t}")
        else: st.write(f"🔹 {t}")

    st.divider()
    if st.button("Sonraki Konu ➡️"):
        if st.session_state.topic_idx < len(topics) - 1:
            st.session_state.topic_idx += 1
            st.rerun()

    if st.button("🚪 Çıkış"): st.session_state.user = None; st.rerun()

# --- 6. DERS İÇERİĞİ ---
current_topic = topics[st.session_state.topic_idx]
cache_key = f"{st.session_state.level}_{current_topic}"

if cache_key not in st.session_state.cache:
    with st.spinner("Öğretmen tahtayı hazırlıyor..."):
        prompt = f"""
        Sen bir İngilizce öğretmenisin. Seviye: {st.session_state.level}, Konu: {current_topic}.
        Dersi TÜRKÇE anlat. İngilizce örnekler ver. 
        MUTLAKA: İngilizce her kelimenin/cümlenin yanına parantez içinde OKUNUŞUNU yaz.
        Örnek: I go to school (Ay go tu s'kuul) : Okula giderim.
        
        Format:
        TEACHER: [Öğrenciye samimi, Türkçe giriş]
        BOARD: [Tahtaya tebeşirle yazılacak konu özeti, kurallar ve okunuşlu örnekler]
        """
        res = get_ai_response(prompt)
        if res != "ERROR": st.session_state.cache[cache_key] = res
        else: st.error("Bağlantı sorunu! Lütfen tekrar deneyin.")

# --- 7. EKRAN TASARIMI ---
content = st.session_state.cache.get(cache_key, "TEACHER: Merhaba! BOARD: Hazırlanıyor...")
t_text = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
b_text = content.split("BOARD:")[1].strip() if "BOARD:" in content else "Ders yükleniyor..."

col_b, col_t = st.columns([3, 1])

with col_b:
    st.markdown(f'<div class="blackboard">{b_text}</div>', unsafe_allow_html=True)
    # Soru sorma alanı
    u_q = st.chat_input("Hocaya bu konu hakkında bir şey sor...")
    if u_q:
        with st.spinner("Hoca düşünüyor..."):
            ans = get_ai_response(f"Konu {current_topic}. Soru: {u_q}. Türkçe ve kısa cevap ver.")
            st.chat_message("user").write(u_q)
            st.chat_message("assistant").write(ans)

with col_t:
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    st.markdown(f'<div class="teacher-bubble">{t_text}</div>', unsafe_allow_html=True)
    if st.button("🔊 Dinle"):
        tts = gTTS(t_text, lang='tr')
        fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    
    st.divider()
    if st.button("📝 15 Soruluk Testi Başlat"):
        st.info("Bu özellik bir sonraki güncellemede eklenecek!")
