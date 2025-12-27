import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json

# --- 1. API VE AKILLI MODEL SEÇİCİ ---
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk" 
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_best_model():
    # Sistemde çalışan en uygun modeli otomatik bulur
    possible_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    for m_name in possible_models:
        try:
            m = genai.GenerativeModel(m_name)
            # Test amaçlı küçük bir istek
            m.generate_content("test")
            return m
        except:
            continue
    return None

model = get_best_model()

# --- 2. A1-C2 DEV MÜFREDAT ---
CURRICULUM = {
    "A1 (Başlangıç)": ["Greetings (Tanışma)", "Numbers & Colors", "Present Simple (Geniş Zaman)", "Be Fiili (Am-Is-Are)", "Daily Routines"],
    "A2 (Temel)": ["Past Simple (Geçmiş Zaman)", "Future Tense (Will/Going to)", "Adjectives (Sıfatlar)", "Modal Verbs (Can/Must)", "Questions"],
    "B1 (Orta Öncesi)": ["Present Perfect", "Passive Voice (Edilgen)", "Relative Clauses", "Conditionals Type 1", "Conjunctions"],
    "B2 (Orta Üstü)": ["Past Perfect", "Reported Speech", "Gerund & Infinitive", "Conditionals Type 2 & 3", "Phrasal Verbs"],
    "C1-C2 (İleri Seviye)": ["Inversion (Devrik Cümleler)", "Advanced Vocabulary", "Causatives", "Idioms", "Academic Writing"]
}

# --- 3. TASARIM (YATAY TAHTA VE RENKLİ ARKA PLAN) ---
st.set_page_config(layout="wide", page_title="Robot Akademi")

st.markdown("""
<style>
    /* 60 saniyede bir yavaşça renk değiştiren arka plan */
    @keyframes slowRainbow {
        0% { background-color: #eef2f3; }
        33% { background-color: #fffde7; }
        66% { background-color: #fce4ec; }
        100% { background-color: #eef2f3; }
    }
    .stApp { animation: slowRainbow 60s infinite ease-in-out; }
    
    /* YATAY DİKDÖRTGEN KARA TAHTA */
    .blackboard {
        background-color: #1a3a32; color: #fdfdfd; border: 12px solid #5d4037;
        padding: 30px; border-radius: 8px; font-family: 'Comic Sans MS', cursive;
        width: 100%; min-height: 350px; box-shadow: 8px 8px 25px rgba(0,0,0,0.5);
        font-size: 21px; line-height: 1.5; margin-bottom: 20px;
    }
    
    .teacher-bubble {
        background: white; padding: 20px; border-radius: 20px;
        border: 3px solid #FFD700; color: #333; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. KULLANICI SEÇİMİ ---
if "user" not in st.session_state:
    st.title("🎓 İngilizce Akademisi")
    col1, col2 = st.columns(2)
    if col1.button("👩‍🎓 Hatice Kübra"): st.session_state.user = "Hatice Kübra"; st.rerun()
    if col2.button("👨‍🎓 Mehmet Akif"): st.session_state.user = "Mehmet Akif"; st.rerun()
    st.stop()

# --- 5. SOL MENÜ (SEVİYE VE ÜNİTE) ---
if "level" not in st.session_state: st.session_state.level = "A1 (Başlangıç)"
if "unit_idx" not in st.session_state: st.session_state.unit_idx = 0

with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    new_lvl = st.selectbox("Seviye:", list(CURRICULUM.keys()), index=list(CURRICULUM.keys()).index(st.session_state.level))
    if new_lvl != st.session_state.level:
        st.session_state.level = new_lvl
        st.session_state.unit_idx = 0
        st.rerun()
    
    st.divider()
    units = CURRICULUM[st.session_state.level]
    for i, u in enumerate(units):
        if i == st.session_state.unit_idx: st.markdown(f"👉 **{u}**")
        else: st.write(f"🔹 {u}")
    
    if st.button("Sonraki Ünite ➡️"):
        if st.session_state.unit_idx < len(units)-1:
            st.session_state.unit_idx += 1
            st.rerun()
    
    if st.button("🚪 Çıkış"): st.session_state.user = None; st.rerun()

# --- 6. DERS İÇERİĞİ ---
current_unit = units[st.session_state.unit_idx]

def load_lesson():
    if not model: return "TEACHER: Bağlantı kurulamadı. BOARD: Lütfen API anahtarını kontrol et."
    
    prompt = f"""
    Sen harika bir İngilizce öğretmenisin. Konu: {current_unit}, Seviye: {st.session_state.level}.
    1. TEACHER: Bölümünde öğrenciye dersi TÜRKÇE anlat. İngilizce örneklerin yanına hemen Türkçesini yaz.
    2. BOARD: Bölümünde tahtaya tebeşirle yazılacak özeti çıkar. İngilizce kelimelerin yanına parantez içinde OKUNUŞUNU yaz.
       Örn: Teacher (Tiıçır) : Öğretmen.
    """
    try:
        res = model.generate_content(prompt)
        return res.text
    except:
        return "TEACHER: Bir hata oluştu. BOARD: Lütfen sayfayı yenile."

content = load_lesson()

# --- 7. EKRAN YERLEŞİMİ ---
col_main, col_teacher = st.columns([3, 1])

with col_main:
    # YATAY KARA TAHTA
    board_text = content.split("BOARD:")[1] if "BOARD:" in content else content
    st.markdown(f'<div class="blackboard">{board_text}</div>', unsafe_allow_html=True)
    
    # MESAJLAŞMA ÇUBUĞU (TAHTANIN ALTINDA)
    user_q = st.chat_input("Öğretmenim, bir sorum var...")
    if user_q:
        st.info(f"Sen: {user_q}")
        if model:
            with st.spinner("Hoca cevap veriyor..."):
                reply = model.generate_content(f"Sen öğretmensin. Soru: {user_q}. Türkçe cevap ver.").text
                st.success(f"Miss Sarah: {reply}")

with col_teacher:
    # ÖĞRETMEN VE BALON
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    teacher_text = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
    st.markdown(f'<div class="teacher-bubble">{teacher_text}</div>', unsafe_allow_html=True)
    
    if st.button("🔊 Sesli Dinle"):
        tts = gTTS(teacher_text, lang='tr')
        fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp)
        
    st.divider()
    if st.button("📝 15 Soruluk Test"):
        st.warning("Bu özellik yapım aşamasında!")
