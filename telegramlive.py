# xenodrop_strike_final.py – Full AI Tip Tracker (Telegram + Streamlit)
import streamlit as st, requests, time
from web3 import Web3

# === CONFIG ===
ETH_ADDRESS = "0x5036dbcEEfae0a7429e64467222e1E259819c7C7"
RPC = "https://eth.llamarpc.com"  # No API key required
TELEGRAM_TOKEN = "8089393098:AAGwE6cnV8DGOmKxU2TnhyoZOHIPm3kEDUU"
TELEGRAM_CHAT_ID = "7139092166"
TOKENS = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA"
}
ERC20_ABI = '[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"}]'

web3 = Web3(Web3.HTTPProvider(RPC))

# === INIT STATE ===
if "log" not in st.session_state: st.session_state.log = []
if "prev_eth" not in st.session_state: st.session_state.prev_eth = 0.0
if "prev_tokens" not in st.session_state: st.session_state.prev_tokens = {}

# === HELPERS ===
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_eth_balance():
    return float(web3.from_wei(web3.eth.get_balance(ETH_ADDRESS), "ether"))

def get_token_balances():
    results = {}
    for name, addr in TOKENS.items():
        try:
            contract = web3.eth.contract(address=Web3.to_checksum_address(addr), abi=ERC20_ABI)
            bal = contract.functions.balanceOf(ETH_ADDRESS).call()
            dec = contract.functions.decimals().call()
            results[name] = bal / (10 ** dec)
        except:
            continue
    return results

# === CHECK + ALERT ===
def check_and_alert():
    new_eth = get_eth_balance()
    if new_eth > st.session_state.prev_eth:
        delta = round(new_eth - st.session_state.prev_eth, 6)
        msg = f"💸 ETH Tip: +{delta} ETH\n🎁 DROP: https://coff.ee/xenotech"
        send_telegram(msg)
        st.session_state.log.append(("ETH", delta))
        st.session_state.prev_eth = new_eth

    new_tokens = get_token_balances()
    for sym, amount in new_tokens.items():
        if sym not in st.session_state.prev_tokens:
            st.session_state.prev_tokens[sym] = 0
        if amount > st.session_state.prev_tokens[sym]:
            delta = round(amount - st.session_state.prev_tokens[sym], 4)
            msg = f"🪙 {sym} Tip: +{delta} {sym}\n🎁 DROP: https://coff.ee/xenotech"
            send_telegram(msg)
            st.session_state.log.append((sym, delta))
            st.session_state.prev_tokens[sym] = amount

# === STREAMLIT DASHBOARD ===
st.set_page_config(page_title="XenoDrop Tracker", layout="wide")
st.title("👁️ XenoDrop AI Tip Tracker")
st.markdown(f"**Watching:** `{ETH_ADDRESS}`")

check_and_alert()

col1, col2 = st.columns(2)
with col1:
    st.subheader("📬 Tip Log")
    st.table(st.session_state.log[-10:])
with col2:
    st.subheader("📊 Live Balances")
    st.metric("ETH", f"{get_eth_balance():.4f} ETH")
    st.json(get_token_balances())

# === AUTO REFRESH LOOP ===
st.markdown("⏱️ Auto-refresh every 30 seconds")
if st.button("⟳ Manual Refresh"):
    st.rerun()

time.sleep(30)
st.rerun()
