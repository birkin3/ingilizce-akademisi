import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- 1. API YAPILANDIRMASI ---
API_KEY = "AIzaSyCOv-TPknOk_bNgbfhWoG9Ce_QlW1T8vBw"
genai.configure(api_key=API_KEY)

# Hata almamak için sistemdeki uygun modeli otomatik bulan fonksiyon
@st.cache_resource
def get_working_model():
    try:
        # Google'a "Benim anahtarım hangi modelleri açıyor?" diye soruyoruz
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Öncelik sıramız: 1.5 Flash, 1.5 Pro, en son Gemini Pro
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        
        for target in target_models:
            if target in available_models:
                return genai.GenerativeModel(target)
        
        # Eğer hiçbiri yoksa listedeki ilk çalışan modeli al
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"Modellere ulaşılamadı: {e}")
    return None

model = get_working_model()

def metni_sese_cevir(text):
    try:
        sound_file = BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(sound_file)
        return sound_file
    except: return None

st.set_page_config(page_title="İngilizce Akademisi", layout="wide")

# --- 2. PROFİL SİSTEMİ ---
if "current_user" not in st.session_state:
    st.title("👋 Hoş Geldiniz")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👦 Mehmet Akif", use_container_width=True):
            st.session_state.current_user = "Mehmet Akif"
            st.session_state.user_data = {"level": "A1", "score": 0}
            st.rerun()
    with col2:
        if st.button("👧 Hatice Kübra", use_container_width=True):
            st.session_state.current_user = "Hatice Kübra"
            st.session_state.user_data = {"level": "A1", "score": 0}
            st.rerun()
    st.stop()

# --- 3. SOHBET ---
st.sidebar.title(f"👤 {st.session_state.current_user}")
st.sidebar.metric("⭐ Puan", st.session_state.user_data['score'])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model is None:
            st.error("Üzgünüm, Google API şu an anahtarınızı kabul etmiyor. Lütfen AI Studio'dan anahtarın 'Active' olduğunu kontrol edin.")
        else:
            try:
                system_instr = f"Sen öğretmensin. Öğrenci: {st.session_state.current_user}. Seviye: A1. Türkçe açıkla, İngilizce öğret. Sonunda soru sor."
                response = model.generate_content(system_instr + "\n" + prompt)
                
                cevap = response.text
                st.markdown(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
                
                audio = metni_sese_cevir(cevap)
                if audio: st.audio(audio)
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
