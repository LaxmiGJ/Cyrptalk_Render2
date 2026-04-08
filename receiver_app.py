import streamlit as st
import requests
from deep_translator import GoogleTranslator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zlib

st.set_page_config(page_title="CrypTalk Receiver", page_icon="📥", layout="centered")
st.title("📥 CrypTalk Receiver")
st.caption("Fetch, decrypt, and translate the secure message")

API_KEY = "$2a$10$Sfp9KhzSzJBDPcKJJZYSNeDKxmiuw8xc.Jn7/xMJbKLmFmaGikJVe"
BIN_ID = "69d68478856a6821891093db"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
HEADERS = {
    "X-Master-Key": API_KEY
}

LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml"
}

def decrypt_data(encrypted_hex, key_hex, nonce_hex):
    encrypted = bytes.fromhex(encrypted_hex)
    key = bytes.fromhex(key_hex)
    nonce = bytes.fromhex(nonce_hex)
    aes = AESGCM(key)
    return aes.decrypt(nonce, encrypted, None)


def decompress_data(data_bytes):
    return zlib.decompress(data_bytes).decode()


def parse_tagged_text(tagged_text):
    if tagged_text.startswith("[") and "] " in tagged_text:
        tag_part, message_part = tagged_text.split("] ", 1)
        return f"{tag_part}]", message_part
    return "", tagged_text


if st.button("Receive Message"):
    with st.spinner("Fetching secure message..."):
        response = requests.get(URL, headers=HEADERS)

        if response.status_code != 200:
            st.error("❌ Failed to fetch message from cloud storage")
            st.write(response.text)
        else:
            data = response.json()
            record = data.get("record", {})

            if not record:
                st.error("❌ No stored message found")
            else:
                try:
                    decrypted_bytes = decrypt_data(
                        record["encrypted"], record["key"], record["nonce"]
                    )
                    plaintext = decompress_data(decrypted_bytes)
                except Exception as exc:
                    st.error("❌ Failed to decrypt or decompress message")
                    st.write(exc)
                else:
                    tag, english_message = parse_tagged_text(plaintext)
                    receiver_lang = record.get("receiver_lang", "English")
                    translated_message = english_message

                    if receiver_lang != "English":
                        try:
                            translated_message = GoogleTranslator(
                                source="en",
                                target=LANG_CODES.get(receiver_lang, "en"),
                            ).translate(english_message)
                        except Exception:
                            translated_message = english_message

                    st.success("✅ Secure message received")
                    st.write("**Sender:**", record.get("sender", "Unknown"))
                    st.write("**Receiver:**", record.get("receiver", "Unknown"))
                    st.write("**Emotion:**", record.get("emotion", "Unknown"))
                    st.write("**Original language:**", record.get("sender_lang", "English"))
                    st.write("**Receiver language:**", receiver_lang)
                    st.write("**Decrypted message:**")
                    st.code(plaintext)

                    if receiver_lang != "English":
                        st.write("**Translated message:**")
                        st.code(f"{tag} {translated_message}" if tag else translated_message)
