import streamlit as st
import requests
import qrcode
import time
from web3 import Web3
from io import BytesIO
from PIL import Image
import threading

# === CONFIG ===
ETH_WALLET = "0x5036dbcEEfae0a7429e64467222e1E259819c7C7"
BUYMECOFFEE_URL = "https://coff.ee/xenotech"
TELEGRAM_TOKEN = "8089393098:AAGwE6cnV8DGOmKxU2TnhyoZOHIPm3kEDUU"
CHAT_ID = "7139092166"
INFURA_RPC = "https://mainnet.infura.io/v3/20a32c9c56174317ba15f92214fecff4"
w3 = Web3(Web3.HTTPProvider(INFURA_RPC))

st.set_page_config(page_title="XenoDrop Strike Final", layout="centered")

# === UTILS ===
def get_eth_balance():
    try:
        balance_wei = w3.eth.get_balance(ETH_WALLET)
        return w3.from_wei(balance_wei, 'ether')
    except Exception as e:
        return f"Error: {str(e)}"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram Error:", e)

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return Image.open(buf)

# === STREAMLIT UI ===
st.title("☄️ XenoDrop Live Earnings")
st.markdown("Monitoring wallet + tipping status in real-time.")

eth = get_eth_balance()
st.metric("🪙 ETH Balance", f"{eth} ETH")

st.subheader("💸 Tip XenoTech")
col1, col2 = st.columns(2)
with col1:
    st.image(make_qr("ethereum:" + ETH_WALLET), caption="Tip in ETH")
    st.write(ETH_WALLET)
with col2:
    st.image(make_qr(BUYMECOFFEE_URL), caption="Buy Me a Coffee")
    st.write(BUYMECOFFEE_URL)

st.markdown("---")
st.markdown("🔁 Auto-broadcasting updates every hour...")

# === AUTO LOOP ===
def hourly_broadcast():
    last_sent = ""
    while True:
        now = time.strftime('%H:%M:%S')
        eth = get_eth_balance()
        message = f"""🚀 XenoDrop Live!
Wallet: {ETH_WALLET}
💰 Balance: {eth} ETH
🌐 Stream: https://telegramm.streamlit.app/
☕ Tip: {BUYMECOFFEE_URL}
🛰️ {now}"""
        if message != last_sent:
            send_telegram(message)
            last_sent = message
        time.sleep(3600)

threading.Thread(target=hourly_broadcast, daemon=True).start()
