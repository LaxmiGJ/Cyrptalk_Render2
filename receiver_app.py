import streamlit as st
import requests

st.title("📥 CrypTalk Receiver")

API_KEY = "PASTE_YOUR_API_KEY"
BIN_ID = "69d68478856a6821891093db"

url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"

headers = {
    "X-Master-Key": $2a$10$Sfp9KhzSzJBDPcKJJZYSNeDKxmiuw8xc.Jn7/xMJbKLmFmaGikJVe
}

if st.button("Receive Message"):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        message = data["record"]["message"]

        st.success("Message Received ✅")
        st.code(message)
    else:
        st.error("Failed ❌")