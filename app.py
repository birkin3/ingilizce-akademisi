import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import json

# --- 1. API YAPILANDIRMASI ---
# BURAYA ANAHTARINI KOY. EĞER ÇALIŞMAZSA GOOGLE AI STUDIO'DAN "CREATE API KEY" DİYEREK YENİSİNİ AL.
API_KEY = "AIzaSyBBfIH_3C1uXozGu3gU2FA00JTjCVX8Zjk" 
genai.configure(api_key=API_KEY)

def ask_ai(prompt):
    try:
        # En stabil model ismini deniyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 2. A1-C2 DEV MÜFREDAT LİSTESİ ---
CURRICULUM = {
    "A1 (Başlangıç)": ["Tanışma & Am-Is-Are", "Sayılar & Renkler", "Geniş Zaman (Present Simple)", "Şimdiki Zaman (Present Continuous)", "Temel Fiiller"],
    "A2 (Temel)": ["Geçmiş Zaman (Past Simple)", "Gelecek Zaman (Will/Going to)", "Sıfatlar & Karşılaştırmalar", "Can-Must-Should", "İyelik Yapıları"],
    "B1 (Orta Öncesi)": ["Present Perfect (Have Done)", "Past Continuous", "Relative Clauses (Who/Which)", "Passive Voice (Edilgen)", "Conditionals Type 1"],
    "B2 (Orta Üstü)": ["Past Perfect", "Reported Speech (Aktarma)", "Gerund & Infinitive", "Conditionals Type 2 & 3", "Modals in the Past"],
    "C1-C2 (İleri)": ["Advanced Inversion (Devrik Cümle)", "Causatives (Have/Get)", "Academic Vocabulary", "Idioms & Phrasal Verbs", "Complex Structures"]
}

# --- 3. TASARIM VE CSS (YATAY TAHTA & RENKLİ ARKA PLAN) ---
st.set_page_config(layout="wide", page_title="İngilizce Akademisi")

st.markdown("""
<style>
    @keyframes bgAnimation {
        0% { background-color: #e3f2fd; } 33% { background-color: #fff9c4; }
        66% { background-color: #ffccbc; } 100% { background-color: #e3f2fd; }
    }
    .stApp { animation: bgAnimation 50s infinite alternate linear; }
    
    /* YATAY DİKDÖRTGEN KARA TAHTA */
    .blackboard {
        background-color: #0d2b21; color: #f0f0f0; border: 14px solid #5d4037;
        padding: 40px; border-radius: 10px; font-family: 'Comic Sans MS', cursive;
        width: 100%; min-height: 320px; box-shadow: 15px 15px 35px rgba(0,0,0,0.6);
        font-size: 22px; line-height: 1.6; margin-bottom: 25px;
        background-image: radial-gradient(circle, #1a3a32 0%, #0d2b21 100%);
    }
    .teacher-bubble {
        background: white; padding: 20px; border-radius: 25px;
        border: 3px solid #FFD700; position: relative; color: #333; font-weight: bold;
    }
    .active-unit { border-left: 6px solid #d32f2f; padding-left: 10px; color: #d32f2f; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. DURUM YÖNETİMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "level" not in st.session_state: st.session_state.level = "A1 (Başlangıç)"
if "unit" not in st.session_state: st.session_state.unit = 0
if "mode" not in st.session_state: st.session_state.mode = "lesson"

# --- 5. GİRİŞ EKRANI ---
if not st.session_state.user:
    st.title("🏫 İngilizce Akademisi - Sınıfa Giriş")
    cols = st.columns(2)
    if cols[0].button("👩‍🎓 Hatice Kübra"): st.session_state.user = "Hatice Kübra"; st.rerun()
    if cols[1].button("👨‍🎓 Mehmet Akif"): st.session_state.user = "Mehmet Akif"; st.rerun()
    st.stop()

# --- 6. SOL PANEL (MÜFREDAT SÜTUNU) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user}")
    st.write(f"📊 Mevcut Seviye: **{st.session_state.level}**")
    st.divider()
    
    # Seviye Seçimi
    selected_lvl = st.selectbox("Seviye Değiştir:", list(CURRICULUM.keys()))
    if selected_lvl != st.session_state.level:
        st.session_state.level = selected_lvl
        st.session_state.unit = 0
        st.rerun()
    
    st.subheader("📚 Üniteler")
    units = CURRICULUM[st.session_state.level]
    for i, u in enumerate(units):
        if i == st.session_state.unit: st.markdown(f'<div class="active-unit">➡️ {u}</div>', unsafe_allow_html=True)
        else: st.write(f"🔹 {u}")
    
    st.divider()
    if st.button("Sonraki Ünite ➡️"):
        if st.session_state.unit < len(units) - 1:
            st.session_state.unit += 1
            st.session_state.mode = "lesson"
            st.rerun()
    
    if st.button("🚪 Çıkış"): st.session_state.user = None; st.rerun()

# --- 7. DERS VE SINAV MANTIĞI ---
current_unit_name = units[st.session_state.unit]

def get_content():
    if st.session_state.mode == "lesson":
        prompt = f"""
        Sen bir İngilizce öğretmenisin. Seviye: {st.session_state.level}, Konu: {current_unit_name}.
        1. TEACHER: Kısmında öğrenciye Türkçe olarak konuyu anlat. İngilizce cümle kurduğunda hemen yanına Türkçesini yaz. 
           Örn: I am a teacher (Ben bir öğretmenim).
        2. BOARD: Kısmında tahtaya tebeşirle yazılacak özeti çıkar. 
           ÖNEMLİ: Her kelimenin yanına parantez içinde OKUNUŞUNU yaz.
           Örn: School (S'kuul) : Okul
        """
    else:
        prompt = f"Seviye: {st.session_state.level}, Konu: {current_unit_name}. Bu konuyla ilgili 15 adet çoktan seçmeli İngilizce test sorusu ve şıklarını hazırla. En sonda cevap anahtarını ver."
    
    res = ask_ai(prompt)
    return res

content = get_content()

# --- 8. EKRAN YERLEŞİMİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    # YATAY KARA TAHTA
    board_part = content.split("BOARD:")[1] if "BOARD:" in content else content
    st.markdown(f'<div class="blackboard">{board_part}</div>', unsafe_allow_html=True)
    
    # MESAJLAŞMA ÇUBUĞU
    user_input = st.chat_input("Hocaya bu konuyla ilgili bir soru sor...")
    if user_input:
        st.chat_message("user").write(user_input)
        with st.spinner("Hoca cevaplıyor..."):
            answer = ask_ai(f"Sen öğretmensin. Konu {current_unit_name}. Öğrenci şunu sordu: {user_input}. Türkçe cevap ver.")
            st.chat_message("assistant").write(answer)

with col_side:
    # ÖĞRETMEN GÖRSELİ VE BALON
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    st.write("👩‍🏫 **Miss Sarah**")
    
    teacher_part = content.split("BOARD:")[0].replace("TEACHER:", "").strip()
    st.markdown(f'<div class="teacher-bubble">{teacher_part}</div>', unsafe_allow_html=True)
    
    if st.button("🔊 Sesli Dinle"):
        tts = gTTS(teacher_part, lang='tr')
        fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    
    st.divider()
    if st.button("📝 Ünite Sınavını Başlat (15 Soru)"):
        st.session_state.mode = "quiz"
        st.rerun()
    if st.button("📖 Derse Geri Dön"):
        st.session_state.mode = "lesson"
        st.rerun()
