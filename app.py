import streamlit as st
import google.generativeai as genai

# --- 1. API YAPILANDIRMASI ---
# Yeni aldığın anahtarı buraya ekledim
API_KEY = "AIzaSyCOv-TPknOk_bNgbfhWoG9Ce_QlW1T8vBw" 

try:
    genai.configure(api_key=API_KEY)
    # Yeni anahtarınla artık en hızlı model olan 1.5 Flash'ı kullanabiliriz
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Başlatma Hatası: {e}")

st.set_page_config(page_title="Mehmet Akif & Hatice Kübra İngilizce", page_icon="🇬🇧", layout="wide")

# --- 2. PROFİL SİSTEMİ ---
if "current_user" not in st.session_state:
    st.title("👋 Aile Boyu İngilizce Kursu")
    st.subheader("Lütfen öğrenci profilinizi seçin:")
    
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
    # AI Öğretmen Avatarı
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    st.markdown("---")
    
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

# Geçmişi Göster
for message in st.session_state.messages:
    avatar = "https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Giriş ve Yanıt
if prompt := st.chat_input("Cevabınızı buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg"):
        system_instruction = f"""
        Sen bir İngilizce öğretmenisin. Öğrenci: {current_user}. Seviye: {st.session_state.user_data['level']}, Ünite: {st.session_state.user_data['unit']}.
        - Önce Türkçe selamla ve konuyu anlat.
        - Kelime okunuşlarını 🔊 formatında yaz.
        - Önemli kelimeler için resim ekle: ![image](https://loremflickr.com/600/400/<keyword>)
        - Her cevabın sonunda mutlaka bir soru sor.
        """
        
        try:
            # Hafıza yönetimi için mesajları listeye çeviriyoruz
            messages_for_ai = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
            # Mesajların başına sistem talimatını ekliyoruz
            response = model.generate_content([system_instruction] + [m["content"] for m in st.session_state.messages])
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            if "correct" in response.text.lower() or "doğru" in response.text.lower():
                st.session_state.user_data["score"] += 10
                st.toast("🎉 Puan Kazandın!")
        except Exception as e:
            st.error(f"Bir sorun oluştu: {e}")
