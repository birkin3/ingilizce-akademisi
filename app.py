import streamlit as st
import google.generativeai as genai
import json
import os

# --- AYARLAR VE API ---
API_KEY = "AIzaSyCghofUePWU_WYB1R044BacmkH5n2Vm5a8" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- KULLANICI YÖNETİMİ ---
def progress_yukle(user_name):
    file_path = f"ilerleme_{user_name.lower()}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"level": "A1", "unit": 1, "score": 0}

def progress_kaydet(user_name, data):
    file_path = f"ilerleme_{user_name.lower()}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- GİRİŞ EKRANI ---
st.set_page_config(page_title="Aile Boyu İngilizce", layout="wide")

if "current_user" not in st.session_state:
    st.title("👋 Hoş Geldiniz!")
    user = st.selectbox("Lütfen profilinizi seçin:", ["Seçiniz", "Ben", "Ablam"])
    if user != "Seçiniz":
        st.session_state.current_user = user
        st.session_state.user_data = progress_yukle(user)
        st.rerun()
    st.stop() # Kullanıcı seçilene kadar uygulamanın geri kalanını çalıştırma

current_user = st.session_state.current_user

# --- KENAR ÇUBUĞU ---
with st.sidebar:
    st.title(f"👤 Profil: {current_user}")
    avatar_url = "https://img.freepik.com/free-psd/3d-illustration-female-teacher-with-glasses-holding-books_23-2149436197.jpg"
    st.image(avatar_url)
    
    level = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2", "C1", "C2"], 
                         index=["A1", "A2", "B1", "B2", "C1", "C2"].index(st.session_state.user_data["level"]))
    unit = st.number_input("Ünite:", min_value=1, value=st.session_state.user_data["unit"])
    st.metric(label="Puan", value=st.session_state.user_data['score'])

    if st.button("Çıkış Yap / Kullanıcı Değiştir"):
        del st.session_state.current_user
        st.rerun()

# --- EĞİTİM MOTORU ---
# (Önceki görsel ve ders anlatım mantığı burada devam ediyor...)
system_instruction = f"Sen {current_user} adlı öğrenciye ders veren bir öğretmensin. Seviye: {level}, Ünite: {unit}..."

# Not: Diğer sohbet ve resim kodları burada aynı şekilde çalışacak.
st.write(f"### Merhaba {current_user}, derse hazır mısın?")

if prompt := st.chat_input("Mesajınızı yazın..."):
    # ... (Buradaki işlemler önceki kodla aynı kalacak)
    st.session_state.user_data["score"] += 10 # Örnek puan artışı
    progress_kaydet(current_user, st.session_state.user_data)