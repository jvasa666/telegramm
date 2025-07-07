# ☄️ XenoDrop Super Script v2 — Full Funnel Web3 Earnings

import streamlit as st
import requests, time, threading, webbrowser, qrcode
from web3 import Web3
from io import BytesIO
from PIL import Image

# === CONFIG ===
ETH_WALLET = "0x5036dbcEEfae0a7429e64467222e1E259819c7C7"
SOLANA_WALLET = "TODO"  # Placeholder for future Phantom/Solana integration
BUYMECOFFEE = "https://coff.ee/xenotech"
INFURA = "https://ethereum.publicnode.com"
TELEGRAM_TOKEN = "8089393098:AAGwE6cnV8DGOmKxU2TnhyoZOHIPm3kEDUU"
CHAT_ID = "7139092166"
w3 = Web3(Web3.HTTPProvider(INFURA))

# === INIT STORAGE ===
seen_tx = set()
leaderboard = {}

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="XenoDrop Super V2", layout="wide")
st.title("☄️ XenoDrop Live Earnings V2")
st.markdown("Real-time multi-chain earnings tracker and live broadcasting.")

# === QR CODE ===
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return Image.open(buf)

# === BALANCE ===
def get_eth_balance():
    try:
        return round(w3.from_wei(w3.eth.get_balance(ETH_WALLET), 'ether'), 5)
    except Exception as e:
        return f"Error: {e}"

# === TELEGRAM ===
def telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg})
    except: pass

# === ERC-20 TIP CHECK ===
def check_erc20_tips():
    try:
        latest = w3.eth.get_block('latest', full_transactions=True).transactions
        for tx in latest:
            if tx.to and tx.to.lower() == ETH_WALLET.lower():
                if tx.hash.hex() not in seen_tx:
                    eth_amt = w3.from_wei(tx.value, 'ether')
                    sender = tx['from']
                    seen_tx.add(tx.hash.hex())
                    leaderboard[sender] = leaderboard.get(sender, 0) + eth_amt
                    telegram(f"🤑 New ETH Tip\nFrom: {sender}\nAmount: {eth_amt:.4f} ETH")
    except: pass

# === NFT DROP STUB ===
def maybe_trigger_nft():
    # Placeholder - could trigger OpenSea mint or NFT storage
    pass

# === LENS + FARCASTER BLAST ===
def blast():
    msg = f"🚀 Tip XenoTech - ETH: {ETH_WALLET} / Coffee: {BUYMECOFFEE}"
    url_lens = f"https://hey.xyz/post?text={requests.utils.quote(msg)}"
    url_fc = f"https://warpcast.com/~/compose?text={requests.utils.quote(msg)}"
    webbrowser.open_new_tab(url_lens)
    webbrowser.open_new_tab(url_fc)

# === THREAD WORK ===
def monitor():
    while True:
        check_erc20_tips()
        maybe_trigger_nft()
        time.sleep(15)

def hourly():
    while True:
        bal = get_eth_balance()
        msg = f"📡 XenoDrop Hourly Broadcast\nETH: {bal} ETH\nStream: https://xenodrop.streamlit.app"
        telegram(msg)
        blast()
        time.sleep(3600)

# === START THREADS ===
threading.Thread(target=monitor, daemon=True).start()
threading.Thread(target=hourly, daemon=True).start()

# === DASHBOARD ===
bal = get_eth_balance()
st.metric("ETH Balance", f"{bal} ETH")
col1, col2 = st.columns(2)

with col1:
    st.image(make_qr("ethereum:" + ETH_WALLET), caption="ETH QR")
    st.code(ETH_WALLET)
with col2:
    st.image(make_qr(BUYMECOFFEE), caption="Buy Me Coffee")
    st.write(BUYMECOFFEE)

st.subheader("🏆 Top Contributors")
if leaderboard:
    for addr, val in sorted(leaderboard.items(), key=lambda x: x[1], reverse=True):
        st.write(f"{addr} — {val:.4f} ETH")
else:
    st.info("No tips received yet. Waiting...")

# === AUTO-REFRESH ===
time.sleep(30)
st.experimental_rerun()
