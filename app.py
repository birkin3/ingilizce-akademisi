import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- 1. API YAPILANDIRMASI ---
# NOT: Eğer hala hata alırsan Google AI Studio'dan "Yeni Bir API Key" almayı dene.
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk" 
genai.configure(api_key=API_KEY)

# En garantici model çağırma fonksiyonu
def get_ai_content(prompt):
    try:
        # v1beta hatasını önlemek için doğrudan güncel ismi kullanıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 2. A1-C2 DEV MÜFREDAT ---
CURRICULUM = {
    "A1 (Beginner)": ["Tanışma (Greetings)", "Sayılar & Renkler", "Geniş Zaman (Present Simple)", "Am/Is/Are", "Daily Routines"],
    "A2 (Elementary)": ["Geçmiş Zaman (Past Simple)", "Gelecek Zaman (Will)", "Can/Could", "Adjectives", "Simple Questions"],
    "B1 (Intermediate)": ["Present Perfect", "Relative Clauses", "Passive Voice", "Conditionals Type 1", "Modals"],
    "B2 (Upper-Int)": ["Past Perfect", "Reported Speech", "Gerund & Infinitive", "Conditionals Type 2", "Phrasal Verbs"],
    "C1-C2 (Advanced)": ["Inversion", "Causatives", "Advanced Idioms", "Formal Writing", "Complex Grammar"]
}

# --- 3. TASARIM (YATAY TAHTA VE RENKLİ ARKA PLAN) ---
st.set_page_config(layout="wide", page_title="İngilizce Robot Akademi")

st.markdown("""
<style>
    /* Renk değiştiren arka plan */
    @keyframes bgFlow {
        0% { background-color: #e3f2fd; }
        33% { background-color: #fffde7; }
        66% { background-color: #fce4ec; }
        100% { background-color: #e3f2fd; }
    }
    .stApp { animation: bgFlow 60s infinite ease-in-out; }
    
    /* YATAY DİKDÖRTGEN KARA TAHTA */
    .blackboard {
        background-color: #0d2b21; 
        color: #fdfdfd; 
        border: 15px solid #5d4037;
        padding: 40px; 
        border-radius: 10px; 
        font-family: 'Comic Sans MS', cursive;
        width: 100%; 
        min-height: 300px; /* Yatay görünüm için yükseklik sınırlı tutuldu */
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
        font-size: 22px; 
        line-height: 1.6;
        margin-top: 10px;
    }
    
    .teacher-bubble {
        background: white; padding: 20px; border-radius: 20px;
        border: 4px solid #FFD700; color: #333; font-weight: bold;
        position: relative; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. OTURUM YÖNETİMİ ---
if "user" not in st.session_state:
    st.title("🎓 İngilizce Akademisi")
    c1, c2 = st.columns(2)
    if c1.button("👩‍🎓 Hatice Kübra"): st.session_state.user = "Hatice Kübra"; st.rerun()
    if c2.button("👨‍🎓 Mehmet Akif"): st.session_state.user = "Mehmet Akif"; st.rerun()
    st.stop()

if "level" not in st.session_state: st.session_state.level = "A1 (Beginner)"
if "unit_idx" not in st.session_state: st.session_state.unit_idx = 0

# --- 5. SOL PANEL (NAVİGASYON) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    lvl = st.selectbox("Seviye:", list(CURRICULUM.keys()), index=list(CURRICULUM.keys()).index(st.session_state.level))
    if lvl != st.session_state.level:
        st.session_state.level = lvl
        st.session_state.unit_idx = 0
        st.rerun()
    
    st.write("---")
    units = CURRICULUM[st.session_state.level]
    for i, u in enumerate(units):
        if i == st.session_state.unit_idx: st.info(f"👉 {u}")
        else: st.write(f"🔹 {u}")
    
    if st.button("Sonraki Ünite ➡️"):
        if st.session_state.unit_idx < len(units)-1:
            st.session_state.unit_idx += 1
            st.rerun()
    
    if st.button("🚪 Çıkış"): st.session_state.user = None; st.rerun()

# --- 6. DERS İÇERİĞİ ---
current_topic = units[st.session_state.unit_idx]

@st.cache_data(show_spinner=False)
def load_lesson_data(level, topic):
    prompt = f"""
    Sen harika bir İngilizce öğretmenisin. Seviye: {level}, Konu: {topic}.
    1. TEACHER: Bölümünde öğrenciye dersi TÜRKÇE anlat. İngilizce cümle kurduğunda yanına Türkçesini yaz.
    2. BOARD: Bölümünde yatay kara tahtaya yazılacak özet notları çıkar. 
       KURAL: İngilizce her kelimenin/cümlenin yanına parantez içinde OKUNUŞUNU yaz.
       Örn: Hello (Heloo) : Merhaba.
    """
    return get_ai_content(prompt)

content = load_lesson_data(st.session_state.level, current_topic)

# --- 7. ANA EKRAN DÜZENİ ---
if "ERROR" in content:
    st.error(f"⚠️ Bağlantı Sorunu: {content}")
    if st.button("Tekrar Dene"): st.rerun()
else:
    col_main, col_teacher = st.columns([3, 1])

    with col_main:
        # TAHTA VE MESAJLAŞMA
        try:
            t_part = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
            b_part = content.split("BOARD:")[1].strip()
        except:
            t_part = "Hoş geldin! Derse hazır mısın?"; b_part = content

        st.markdown(f'<div class="blackboard">{b_part}</div>', unsafe_allow_html=True)
        
        # MESAJLAŞMA ÇUBUĞU (TAHTANIN HEMEN ALTINDA)
        user_q = st.chat_input("Öğretmenim, burayı anlamadım...")
        if user_q:
            with st.spinner("Öğretmen cevap veriyor..."):
                ans = get_ai_content(f"Sen öğretmensin. Konu: {current_topic}. Soru: {user_input}. Türkçe cevap ver.")
                st.chat_message("user").write(user_q)
                st.chat_message("assistant").write(ans)

    with col_teacher:
        # ÖĞRETMEN VE SESLENDİRME
        st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
        st.markdown(f'<div class="teacher-bubble">{t_part}</div>', unsafe_allow_html=True)
        
        if st.button("🔊 Sesi Aç"):
            tts = gTTS(t_part, lang='tr')
            fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp)
        
        st.divider()
        st.button("📝 15 Soruluk Test (Yakında)")
