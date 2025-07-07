import streamlit as st
import requests, time, threading, webbrowser, qrcode
from web3 import Web3
from io import BytesIO
from PIL import Image

# === CONFIG ===
ETH_WALLET = "0x5036dbcEEfae0a7429e64467222e1E259819c7C7"
BUYMECOFFEE = "https://coff.ee/xenotech"
RPC_URL = "https://ethereum.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# === TELEGRAM BOT ===
TELEGRAM_TOKEN = "8089393098:AAGwE6cnV8DGOmKxU2TnhyoZOHIPm3kEDUU"
CHAT_ID = "7139092166"

# === STREAMLIT ===
st.set_page_config(page_title="☄️ XenoDrop Super Live", layout="centered")
st.title("☄️ XenoDrop Live Earnings")
st.markdown("Monitoring wallet + tipping status in real-time.")

# === QR GENERATOR ===
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return Image.open(buf)

# === ETH BALANCE ===
def get_balance():
    try:
        wei = w3.eth.get_balance(ETH_WALLET)
        return round(w3.from_wei(wei, 'ether'), 5)
    except Exception as e:
        return f"Error: {e}"

# === TELEGRAM SEND ===
def telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    except: pass

# === DONATION TRACKER ===
seen_tx = set()
def watch_wallet():
    while True:
        try:
            txs = w3.eth.get_block("latest", full_transactions=True).transactions
            for tx in txs:
                if tx.to and tx.to.lower() == ETH_WALLET.lower():
                    if tx.hash.hex() not in seen_tx:
                        amt = w3.from_wei(tx.value, 'ether')
                        sender = tx['from']
                        msg = f"💸 New Tip!\nFrom: {sender}\nAmount: {amt:.4f} ETH"
                        telegram(msg)
                        seen_tx.add(tx.hash.hex())
        except: pass
        time.sleep(15)

# === FARCASTER + LENS POSTING (ZERO-AUTH) ===
def launch_broadcast_tabs():
    post = f"""🚀 Support XenoTech — Builder of AI Crypto Tools

☄️ Live Dashboard: https://xenodrop.streamlit.app/
💸 ETH: {ETH_WALLET}
☕ Coffee: {BUYMECOFFEE}
📡 Telegram: @xenodrop_bot
"""
    lens = "https://hey.xyz/post?text=" + requests.utils.quote(post)
    farcaster = "https://warpcast.com/~/compose?text=" + requests.utils.quote(post)
    webbrowser.open_new_tab(lens)
    webbrowser.open_new_tab(farcaster)

# === HOURLY TELEGRAM PING ===
def hourly_ping():
    while True:
        balance = get_balance()
        message = f"""🚨 XenoDrop Ping
🪙 Balance: {balance} ETH
📟 Live: https://xenodrop.streamlit.app/
📮 Tip: {BUYMECOFFEE}"""
        telegram(message)
        launch_broadcast_tabs()
        time.sleep(3600)

# === VISUALS ===
balance = get_balance()
st.metric("🪙 ETH Balance", f"{balance} ETH")

col1, col2 = st.columns(2)
with col1:
    st.image(make_qr("ethereum:" + ETH_WALLET), caption="Tip ETH")
    st.code(ETH_WALLET)
with col2:
    st.image(make_qr(BUYMECOFFEE), caption="Buy Me A Coffee")
    st.write(BUYMECOFFEE)

st.info("🔁 Auto-posts every hour to Telegram, Farcaster, Lens\n📡 Monitoring live tips every 15s")

# === THREADS START ===
threading.Thread(target=watch_wallet, daemon=True).start()
threading.Thread(target=hourly_ping, daemon=True).start()

# === AUTO REFRESH ===
time.sleep(30)
st.experimental_rerun()
