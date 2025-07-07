# ☄️ XenoDrop Super V2 - Unified Script
# Live ETH/Token Monitor + Streamlit Dashboard + Telegram Alerts

import streamlit as st
import requests
import time
from web3 import Web3
from datetime import datetime

# === CONFIG ===
WALLET_ADDRESS = "0x5036dbcEEfae0a7429e64467222e1E259819c7C7"
RPC_URL = "https://ethereum.publicnode.com"  # No API key needed
TELEGRAM_TOKEN = "8089393098:AAGwE6cnV8DGOmKxU2TnhyoZOHIPm3kEDUU"
TELEGRAM_CHAT_ID = "7139092166"
BMAC_LINK = "https://coff.ee/xenotech"
X_HANDLE = "xtech87184"

# === INIT ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
prev_balance = 0

# === FUNCTIONS ===
def get_eth_balance():
    try:
        balance_wei = w3.eth.get_balance(WALLET_ADDRESS)
        return w3.from_wei(balance_wei, 'ether')
    except Exception as e:
        return f"Error: {e}"

def send_telegram_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except:
        pass

def generate_qr_link(wallet):
    return f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=ethereum:{wallet}"

# === DASHBOARD ===
st.set_page_config(page_title="☄️ XenoDrop Live", layout="centered")
st.title("☄️ XenoDrop Live Earnings")
st.caption("Monitoring wallet + tipping status in real-time.")

eth_col, tip_col = st.columns(2)

# ETH BALANCE
eth = get_eth_balance()
eth_col.metric("🪙 ETH Balance", f"{eth} ETH" if isinstance(eth, float) else str(eth))

# TIP + QR
qr = generate_qr_link(WALLET_ADDRESS)
tip_col.image(qr, caption="Scan to Tip")
tip_col.write("💸 **Tip XenoTech**")
tip_col.code(WALLET_ADDRESS)
tip_col.markdown(f"☕ [Buy Me a Coffee]({BMAC_LINK})")

# AUTO-ALERTING
if isinstance(eth, float) and eth > float(prev_balance):
    diff = eth - float(prev_balance)
    send_telegram_alert(f"🚀 New tip received! +{diff:.4f} ETH\nBalance: {eth:.4f} ETH")
    prev_balance = eth

# FOOTER
st.markdown("---")
st.markdown(f"📡 Broadcasting to [Telegram](https://t.me/xenodrop_bot), Farcaster, and Lens...")
st.markdown(f"🔁 Auto-refreshing every 60s | @{X_HANDLE} on X")

# === AUTO REFRESH ===
time.sleep(60)
st.rerun()
