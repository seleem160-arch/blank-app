import streamlit as st
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

# --- إعدادات الخزنة ---
DB = 'fortress.json'
COMPANIES = {'2222.SR': 'أرامكو', '7010.SR': 'stc', '1120.SR': 'الراجحي', '2082.SR': 'أكوا باور'}

def load_data():
    if os.path.exists(DB):
        with open(DB, 'r') as f: return json.load(f)
    return []

def save_data(data):
    with open(DB, 'w') as f: json.dump(data, f, indent=4)

# --- الواجهة ---
st.set_page_config(page_title="حصن المليون", layout="wide")
st.markdown("<h1 style='text-align: center;'>🦅 حصن المليون</h1>", unsafe_allow_html=True)

data = load_data()

# جلب الأسعار
@st.cache_data(ttl=60)
def get_prices():
    try:
        df = yf.download(list(COMPANIES.keys()), period="1d")['Close']
        return df.iloc[-1].to_dict()
    except: return {k: 0 for k in COMPANIES}

prices = get_prices()

# --- حسابات المليون ---
current_val = sum(i['qty'] * prices.get(i['ticker'], 0) for i in data)
total_cost = sum(i['qty'] * i['price'] for i in data)
profit = current_val - total_cost
distance = 1000000 - current_val

# --- لوحة التحكم ---
c1, c2, c3 = st.columns(3)
c1.metric("المحفظة الآن", f"{current_val:,.2f} ريال")
c2.metric("الربح/الخسارة", f"{profit:,.2f} ريال")
c3.metric("المسافة للمليون", f"{distance:,.2f} ريال")
st.progress(min(current_val / 1000000, 1.0))

# --- إضافة وحذف ---
st.write("---")
with st.expander("➕ تسجيل صيدة جديدة"):
    with st.form("add"):
        t = st.selectbox("الشركة", list(COMPANIES.keys()), format_func=lambda x: COMPANIES[x])
        q = st.number_input("الأسهم", min_value=1)
        p = st.number_input("السعر", min_value=0.1)
        if st.form_submit_button("تثبيت"):
            data.append({'id': str(datetime.now()), 'ticker': t, 'name': COMPANIES[t], 'qty': q, 'price': p})
            save_data(data)
            st.rerun()

st.header("📜 السجل التفصيلي (الأرشيف الصامت)")
for i, item in enumerate(reversed(data)):
    col_a, col_b, col_c = st.columns([3, 1, 1])
    col_a.write(f"**{item['name']}**: {item['qty']} سهم بسعر {item['price']}")
    if col_c.button("حذف 🗑️", key=item['id']):
        data.remove(item)
        save_data(data)
        st.rerun()
