import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Honeypot Live Monitor", layout="wide")

st.title("🛡️ AI Honeypot: Live Attack Monitor")

placeholder = st.empty()

def load_data():
    try:
        df = pd.read_csv("attacks.csv", names=["Timestamp", "Attacker IP", "Command", "Response Type"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Attacker IP", "Command", "Response Type"])
    
while True:
    df = load_data()
    
    with placeholder.container():
        # KPI Metrics at the top
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Metric 1: Total Attacks
        kpi1.metric(label="Total Commands Captured", value=len(df))
        
        # Metric 2: Unique Attackers
        unique_ips = df["Attacker IP"].nunique() if not df.empty else 0
        kpi2.metric(label="Unique Attackers", value=unique_ips)
        
        # Metric 3: Critical Threats (Simple keyword search)
        threats = df[df['Command'].str.contains('wget|curl|rm -rf|sudo', case=False, na=False)]
        kpi3.metric(label="Critical Threats Detected", value=len(threats), delta_color="inverse")

        # The Data Table
        st.subheader("🔴 Live Attack Log")
        
        # Show dangerous commands in RED
        if not df.empty:
            # We sort by newest first
            df = df.sort_index(ascending=False)
            st.dataframe(df, use_container_width=True)

    # Wait 1 second before refreshing
    time.sleep(1)