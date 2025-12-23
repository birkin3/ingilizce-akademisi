import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- 1. API YAPILANDIRMASI ---
# Paylaştığın yeni anahtarı buraya ekledim
API_KEY = "AIzaSyCOv-TPknOk_bNgbfhWoG9Ce_QlW1T8vBw" 

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def metni_sese_cevir(text):
    try:
        sound_file = BytesIO()
        # gTTS kütüphanesi ile İngilizce seslendirme
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(sound_file)
        return sound_file
    except:
        return None

st.set_page_config(page_title="Mehmet Akif & Hatice Kübra İngilizce", layout="wide")

# --- 2. PROFİL SİSTEMİ ---
if "current_user" not in st.session_state:
    st.title("👋 İngilizce Akademisine Hoş Geldiniz")
    st.subheader("Öğrenci profilinizi seçerek başlayın:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👦 Mehmet Akif", use_container_width=True):
            st.session_state.current_user = "Mehmet Akif"
            st.session_state.user_data = {"level": "A1", "unit": 1, "score": 0}
            st.rerun()
    with col2:
        if st.button("👧 Hatice Kübra", use_container_width=True):
            st.session_state.current_user = "Hatice Kübra"
            st.session_state.user_data = {"level": "A1", "unit": 1, "score": 0}
            st.rerun()
    st.stop()

# --- 3. SOHBET EKRANI ---
current_user = st.session_state.current_user
st.sidebar.title(f"👤 {current_user}")
st.sidebar.write(f"**Seviye:** {st.session_state.user_data['level']}")
st.sidebar.write(f"**Ünite:** {st.session_state.user_data['unit']}")
st.sidebar.metric("⭐ Puan", st.session_state.user_data['score'])

if st.sidebar.button("🚪 Profil Değiştir"):
    st.session_state.clear()
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj Geçmişini Görüntüle
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Yapay zekaya öğretici talimatı gönderiyoruz
            system_prompt = f"Sen bir İngilizce öğretmenisin. Öğrencinin adı {current_user}. Seviyesi {st.session_state.user_data['level']}. Önce Türkçe kısa bir açıklama yap, sonra İngilizce öğret ve en sonunda bir soru sor."
            
            response = model.generate_content(system_prompt + "\n" + prompt)
            cevap = response.text
            
            st.markdown(cevap)
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            
            # Seslendirme butonu
            audio = metni_sese_cevir(cevap)
            if audio:
                st.audio(audio)
                
        except Exception as e:
            st.error(f"Bir sorun oluştu: {e}")
            st.info("Eğer hata devam ederse, lütfen 5 dakika bekleyip sayfayı yenileyin (API aktivasyon süresi).")
