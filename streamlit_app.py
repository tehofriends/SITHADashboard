import os
import streamlit as st
import pandas as pd

# ───── Theme and Styling ─────
st.set_page_config(page_title="Partner & Service Dashboard", page_icon="📊", layout="wide")
st.markdown("""
<style>
.stApp {background:#0e1b2a; color:#e0e0e0;}
h1,h2 {color:#ffffff;}
.metric-card {background:#172a45; padding:1.1rem; border-radius:12px;
              box-shadow:0 0 8px rgba(0,0,0,0.40); text-align:center; height:100%;}
.metric-value {font-size:1.7rem; color:#ffcf4d; font-weight:700;}
.metric-label {font-size:0.95rem; color:#b0bec5;}
</style>
""", unsafe_allow_html=True)

def card(label: str, value: int | float | str):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

# ───── Load Data ─────
ATT_SRV = "/mnt/data/services.csv"
ATT_PRV = "/mnt/data/provider.csv"

st.sidebar.header("📂 Data source")
use_attached = st.sidebar.checkbox("Use attached CSVs", value=True)

if use_attached and os.path.exists(ATT_SRV) and os.path.exists(ATT_PRV):
    srv_df = pd.read_csv(ATT_SRV)
    prv_df = pd.read_csv(ATT_PRV)
else:
    srv_u = st.sidebar.file_uploader("services.csv",  type="csv")
    prv_u = st.sidebar.file_uploader("provider.csv", type="csv")
    srv_df = pd.read_csv(srv_u) if srv_u else None
    prv_df = pd.read_csv(prv_u) if prv_u else None

if srv_df is None or prv_df is None:
    st.info("Upload both CSVs or tick the checkbox.")
    st.stop()

srv_df.columns = srv_df.columns.str.strip().str.lower()
prv_df.columns = prv_df.columns.str.strip().str.lower()

# ───── Metrics ─────
active_prv = prv_df[prv_df["status"].str.upper() == "ACTIVE"]
aadhaar_ok = active_prv[active_prv.get("is_aadhaar_verified", 0) == 1]
aadhaar_missing = active_prv[active_prv.get("is_aadhaar_verified", 0) != 1]

indiv_cnt = active_prv[active_prv["company_type"].str.lower() == "individual"].shape[0] \
            if "company_type" in active_prv else 0
org_cnt = active_prv[active_prv["company_type"].str.lower() == "organization"].shape[0] \
          if "company_type" in active_prv else 0

active_srv = srv_df[srv_df["status"].str.upper() == "ACTIVE"]
services = active_srv[active_srv["is_multi_city"] == 0]
products = active_srv[active_srv["is_multi_city"] == 1]
total_listings = len(active_srv)

online = services[services["is_remote"] == 1]
offline = services[services["is_remote"] == 0]

cust_place = offline[offline["is_at_door_step"] == 1] if "is_at_door_step" in offline else pd.DataFrame()
part_store = offline[offline["is_at_store"] == 1] if "is_at_store" in offline else pd.DataFrame()

prv_no_srv = prv_df[~prv_df["provider_id"].isin(srv_df["provider_id"])]

# ───── UI Layout ─────
st.title("📊 Partner & Service Dashboard")

# 🧑‍💼 Providers Summary
st.subheader("🧑‍💼 Providers Summary")
c1, c2, c3 = st.columns(3)
with c1: card("Active Providers", len(active_prv))
with c2: card("Aadhaar Verified", len(aadhaar_ok))
with c3: card("Providers w/out Aadhaar", len(aadhaar_missing))

# 🏢 Partner Type
st.subheader("🏢 Partner Type")
pt1, pt2, pt3 = st.columns(3)
with pt1: card("Individual", indiv_cnt)
with pt2: card("Organization", org_cnt)
pt3.markdown("")

# 🚀 Actions
st.subheader("🚀 Actions")
a1, a2, _ = st.columns(3)
with a1:
    card("🔍 Show Providers w/out Listings", len(prv_no_srv))
    with st.expander("Details"):
        st.dataframe(prv_no_srv.reset_index(drop=True))
with a2:
    card("🔍 Show Providers w/out Aadhaar", len(aadhaar_missing))
    with st.expander("Details"):
        st.dataframe(aadhaar_missing.reset_index(drop=True))

# 📦 Services & Products
st.subheader("📦 Services & Products")
s1, s2, s3 = st.columns(3)
with s1: card("Total Listings", total_listings)
with s2: card("Services", len(services))
with s3: card("Products", len(products))

# 🔍 Service Type
st.subheader("🔍 Service Type")
t1, t2, t3 = st.columns(3)
with t1: card("Online Services", len(online))
with t2: card("Offline Services", len(offline))
t3.markdown("")

# 🏠 On-site Services Split
st.subheader("🏠 On-site Services Split")
os1, os2, os3 = st.columns(3)
with os1: card("Customer-place", len(cust_place))
with os2: card("Partner-store", len(part_store))
os3.markdown("")

st.markdown("---")
st.caption("Click a 🔍 card to view details. Updates on upload or toggle.")
