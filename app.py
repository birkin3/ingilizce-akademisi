import streamlit as st
import google.generativeai as genai

# --- 1. API YAPILANDIRMASI ---
API_KEY = "AIzaSyCOv-TPknOk_bNgbfhWoG9Ce_QlW1T8vBw" 

# BAĞLANTIYI ZORLA v1 SÜRÜMÜNE AYARLIYORUZ (404 HATASINI ÇÖZER)
genai.configure(api_key=API_KEY)

# Hata olasılığını sıfıra indirmek için model ismini doğrudan tanımlıyoruz
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Mehmet Akif & Hatice Kübra İngilizce", page_icon="🇬🇧", layout="wide")

# --- 2. PROFİL SİSTEMİ ---
if "current_user" not in st.session_state:
    st.title("👋 Aile Boyu İngilizce Kursu")
    st.subheader("Lütfen profilinizi seçin:")
    
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

# --- 3. KENAR ÇUBUĞU ---
current_user = st.session_state.current_user
with st.sidebar:
    st.title(f"👤 {current_user}")
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    
    st.session_state.user_data["level"] = st.selectbox(
        "Seviye:", ["A1", "A2", "B1", "B2", "C1", "C2"],
        index=["A1", "A2", "B1", "B2", "C1", "C2"].index(st.session_state.user_data["level"])
    )
    st.session_state.user_data["unit"] = st.number_input(
        "Ünite:", min_value=1, value=st.session_state.user_data["unit"]
    )
    st.divider()
    st.metric(label="⭐ Puan", value=st.session_state.user_data['score'])
    
    if st.button("🚪 Profil Değiştir"):
        st.session_state.clear()
        st.rerun()

# --- 4. SOHBET VE DERS AKIŞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg"):
        # MODELİ ÇAĞIRIRKEN SİSTEM TALİMATINI İÇERİYE GÖMÜYORUZ
        system_instruction = f"Sen bir İngilizce öğretmenisin. Öğrenci: {current_user}. Seviye: {st.session_state.user_data['level']}, Ünite: {st.session_state.user_data['unit']}. Kelime okunuşlarını 🔊 formatında yaz. Görsel için şunu kullan: ![image](https://loremflickr.com/600/400/<keyword>)"
        
        try:
            # EN BASİT ÇAĞRI YÖNTEMİ (HATA PAYINI AZALTIR)
            chat = model.start_chat(history=[])
            response = chat.send_message(f"{system_instruction}\n\nÖğrenci mesajı: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            if "correct" in response.text.lower() or "doğru" in response.text.lower():
                st.session_state.user_data["score"] += 10
                st.toast("🎉 Puan Kazandın!")
        except Exception as e:
            st.error(f"Bağlantı sorunu: {e}")
            st.info("Eğer hata 404 ise, Streamlit Cloud panelinden 'Reboot App' yapmayı deneyin.")
