import streamlit as st
import requests

st.title("📤 CrypTalk Sender")

API_KEY = "$2a$10$Sfp9KhzSzJBDPcKJJZYSNeDKxmiuw8xc.Jn7/xMJbKLmFmaGikJVe"
BIN_ID = "69d68478856a6821891093db"

url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

message = st.text_area("Enter message")

if st.button("Send"):
    data = {"message": message}

    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 200:
        st.success("Message Sent Successfully ✅")
    else:
        st.error("Failed ❌")