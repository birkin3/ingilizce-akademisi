import streamlit as st
import google.generativeai as genai

# --- 1. AYARLAR VE API ---
API_KEY = "AIzaSyCghofUePWU_WYB1R044BacmkH5n2Vm5a8" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Sayfa ayarları
st.set_page_config(page_title="Mehmet Akif & Hatice Kübra İngilizce", page_icon="🇬🇧", layout="wide")

# --- 2. PROFİL VE GİRİŞ SİSTEMİ (İSİMLER GÜNCELLENDİ) ---
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

# --- 3. KENAR ÇUBUĞU (SIDEBAR) ---
current_user = st.session_state.current_user
with st.sidebar:
    st.title(f"👤 {current_user}")
    st.image("https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg")
    st.markdown("---")
    
    st.session_state.user_data["level"] = st.selectbox(
        "Seviye:", 
        ["A1", "A2", "B1", "B2", "C1", "C2"],
        index=["A1", "A2", "B1", "B2", "C1", "C2"].index(st.session_state.user_data["level"])
    )
    st.session_state.user_data["unit"] = st.number_input(
        "Ünite:", 
        min_value=1, 
        value=st.session_state.user_data["unit"]
    )
    
    st.divider()
    st.metric(label="⭐ Başarı Puanı", value=st.session_state.user_data['score'])
    
    if st.button("🚪 Profil Değiştir"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 4. ANA DERS EKRANI ---
st.title(f"🎓 Merhaba {current_user}, Bugün Ne Öğreniyoruz?")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hi {current_user}! I am your English teacher. Are you ready for Unit {st.session_state.user_data['unit']}? (Hazırsan 'Yes' yazarak başlayalım!)"}
    ]

# Sohbet Geçmişi
for message in st.session_state.messages:
    avatar = "https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg"):
        system_instruction = f"""
        Sen samimi bir İngilizce öğretmenisin. Öğrencinin tam adı: {current_user}. 
        Seviye: {st.session_state.user_data['level']}, Ünite: {st.session_state.user_data['unit']}.
        
        KURALLAR:
        1. {current_user} ismini kullanarak ona hitap et.
        2. Konuyu anlat, soru sor ve yanlışlarını düzelt.
        3. Okunuşları '🔊 Pronunciation: Word -> [Okunuş]' formatında ekle.
        4. Nesneler için görsel ekle: ![image](https://source.unsplash.com/600x400/?<keyword>)
        5. Doğru cevaplarda 'Correct! +10 points' yaz.
        """
        
        chat_context = "\n".join([m["content"] for m in st.session_state.messages])
        response = model.generate_content(system_instruction + "\n\n" + chat_context)
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        if "correct" in response.text.lower() or "doğru" in response.text.lower():
            st.session_state.user_data["score"] += 10
            st.toast("🎉 Puan Kazandın!")
