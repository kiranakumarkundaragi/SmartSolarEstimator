import streamlit as st
import pandas as pd
import numpy as np

# ------------------------
# Constants / Assumptions
# ------------------------
DEFAULT_TARIFF = 8.0  # Rs/unit
KWH_PER_KW_PER_MONTH = 120.0  # Approx monthly generation per 1 kW system
SOLAR_HOURS_PER_DAY = 5.0
COST_PER_KW_NO_BATT = 40000
COST_PER_KW_WITH_BATT = 60000
AGR_COST_PER_KW_NO_BATT = 35000
AGR_COST_PER_KW_WITH_BATT = 55000

MATERIALS = [
    {"category": "Panel", "name": "Monocrystalline 450W", "watt": 450, "price": 12000},
    {"category": "Panel", "name": "Polycrystalline 350W", "watt": 350, "price": 8000},
    {"category": "Inverter", "name": "Hybrid Inverter 5kW", "spec": "5kW", "price": 55000},
    {"category": "Battery", "name": "Li-ion 5kWh", "spec": "5kWh", "price": 70000},
    {"category": "Structure", "name": "Roof Mounting Kit", "spec": "per kW", "price": 4000},
    {"category": "Protection", "name": "ACDB/MCB/Protection", "spec": "per system", "price": 8000},
    {"category": "Cables", "name": "PV Cables & Accessories", "spec": "per kW", "price": 2000},
]

# ------------------------
# Helper functions
# ------------------------
def currency(x):
    return f"₹{int(round(x)):,}"

def calc_residential_from_bill(bill, tariff, battery):
    monthly_units = bill / tariff
    system_kw = max(0.5, round(monthly_units / KWH_PER_KW_PER_MONTH * 2)/2)
    cost_per_kw = COST_PER_KW_WITH_BATT if battery else COST_PER_KW_NO_BATT
    total_cost = system_kw * cost_per_kw
    monthly_generation = system_kw * KWH_PER_KW_PER_MONTH
    monthly_savings = monthly_generation * tariff
    payback_years = total_cost / (monthly_savings*12 + 1e-6)
    return {
        "monthly_units": monthly_units,
        "system_kw": system_kw,
        "monthly_generation": monthly_generation,
        "total_cost": total_cost,
        "monthly_savings": monthly_savings,
        "payback_years": round(payback_years, 1)
    }

def calc_agriculture_from_pump(pump_hp, hours_per_day, battery):
    pump_kw = pump_hp * 0.746
    daily_energy = pump_kw * hours_per_day
    system_kw = max(0.5, round(daily_energy / SOLAR_HOURS_PER_DAY * 2)/2)
    cost_per_kw = AGR_COST_PER_KW_WITH_BATT if battery else AGR_COST_PER_KW_NO_BATT
    total_cost = system_kw * cost_per_kw
    monthly_generation = system_kw * KWH_PER_KW_PER_MONTH
    return {
        "pump_kw": pump_kw,
        "hours_per_day": hours_per_day,
        "system_kw": system_kw,
        "monthly_generation": monthly_generation,
        "total_cost": total_cost,
        "daily_energy": daily_energy
    }

def materials_for_system(system_kw):
    panel = MATERIALS[0]
    panel_count = int(np.ceil(system_kw / (panel['watt']/1000)))
    inverter = MATERIALS[2]
    battery = MATERIALS[3]
    structure = MATERIALS[4]
    protection = MATERIALS[5]
    cables = MATERIALS[6]
    mats = [
        {"item": panel['name'], "qty": panel_count, "unit_price": panel['price'], "total": panel_count*panel['price']},
        {"item": inverter['name'], "qty": 1, "unit_price": inverter['price'], "total": inverter['price']},
        {"item": battery['name'], "qty": max(1,int(system_kw/3)), "unit_price": battery['price'], "total": max(1,int(system_kw/3))*battery['price']},
        {"item": structure['name'], "qty": system_kw, "unit_price": structure['price'], "total": system_kw*structure['price']},
        {"item": protection['name'], "qty": 1, "unit_price": protection['price'], "total": protection['price']},
        {"item": cables['name'], "qty": system_kw, "unit_price": cables['price'], "total": system_kw*cables['price']},
    ]
    return mats

# -------------------------------
# Streamlit App Config
# -------------------------------
st.set_page_config(
    page_title="Smart Solar Estimator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# Session state to track login
# -------------------------------
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

# ------------------------
# Top Navigation (no sidebar)
# ------------------------
page = st.selectbox("Choose Page", ["Home", "Estimator", "Materials", "About", "More"])

# ------------------------
# Background function
# ------------------------
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('{image_url}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            background: rgba(255,255,255,0.85);
            border-radius: 12px;
            padding: 4vw 2vw;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------
# Pages
# ------------------------
if page == "Home":
    set_background("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80")
    st.header("🌞 Welcome to Smart Solar Estimator ⚡")
    st.write("🔋 Estimate system size, costs, and materials for Residential or Agriculture solar systems.")
    st.write("🌱 Go green, save money, and power your future with solar energy!")
    st.write("🏠 ☀️ 🚜")

elif page == "Estimator":
    set_background("https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=1200&q=80")
    st.header("🧮 Solar Estimator 📊")
    mode = st.selectbox("Mode", ["Residential", "Agriculture"])
    battery = st.checkbox("Include Battery?")
    
    if mode == "Residential":
        bill = st.number_input("Monthly Electricity Bill (₹)", value=2000.0)
        if st.button("Estimate Residential System"):
            res = calc_residential_from_bill(bill, DEFAULT_TARIFF, battery)
            st.subheader("📋 Results")
            st.metric("Monthly Consumption (kWh)", round(res['monthly_units'],1))
            st.metric("Recommended System Size (kW)", res['system_kw'])
            st.metric("Estimated Monthly Generation (kWh)", int(res['monthly_generation']))
            st.metric("Monthly Savings (₹)", currency(res['monthly_savings']))
            st.metric("Estimated Project Cost", currency(res['total_cost']))
            st.metric("Payback (years)", res['payback_years'])
            
            st.subheader("🛠️ Materials List")
            mats = materials_for_system(res['system_kw'])
            df = pd.DataFrame(mats)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Materials CSV", csv, file_name="residential_materials.csv")
    
    else:
        pump_hp = st.number_input("Pump Size (HP)", value=2.0)
        hours = st.number_input("Pump Run Hours/Day", value=5.0)
        if st.button("Estimate Pump System"):
            res = calc_agriculture_from_pump(pump_hp, hours, battery)
            st.subheader("📋 Results")
            st.metric("Pump Power (kW)", round(res['pump_kw'],2))
            st.metric("Daily Pump Energy (kWh)", round(res['daily_energy'],1))
            st.metric("Recommended System Size (kW)", res['system_kw'])
            st.metric("Estimated Monthly Generation (kWh)", int(res['monthly_generation']))
            st.metric("Estimated Project Cost", currency(res['total_cost']))
            
            st.subheader("🛠️ Materials List")
            mats = materials_for_system(res['system_kw'])
            df = pd.DataFrame(mats)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Materials CSV", csv, file_name="agriculture_materials.csv")
    st.write("🔋 ⚡ 🏡 🚜")

elif page == "Materials":
    set_background("https://images.unsplash.com/photo-1448387473223-5c37445527e7?auto=format&fit=crop&w=1200&q=80")
    st.header("📦 Materials Catalogue 🧰")
    df = pd.DataFrame(MATERIALS)
    st.dataframe(df)
    st.write("🔩 🪛 🧱")

elif page == "About":
    set_background("https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1200&q=80")
    st.header("ℹ️ About Smart Solar Estimator 💡")
    st.write("This app estimates solar system size, cost, and materials for Residential and Agriculture applications.")
    st.write("🌍 Powered by clean energy and smart technology!")
    st.write("👨‍💻 👩‍🔬 ☀️")

elif page == "More":
    set_background("https://images.unsplash.com/photo-1465101178521-c1a9136a3c8b?auto=format&fit=crop&w=1200&q=80")
    st.header("🔑 More & Login 🛡️")
    if not st.session_state.login:
        st.subheader("🔒 Login")
        role = st.radio("Select Role", ["User", "Admin"])
        if role == "Admin":
            username = st.text_input("Admin Username")
            password = st.text_input("Admin Password", type="password")
            if st.button("Login as Admin"):
                if username == "admin" and password == "admin123":
                    st.session_state.login = True
                    st.session_state.role = "Admin"
                    st.success("Logged in as Admin")
                    st.experimental_rerun()
                else:
                    st.error("Invalid Admin credentials!")
        else:
            if st.button("Login as User"):
                st.session_state.login = True
                st.session_state.role = "User"
                st.success("Logged in as User")
                st.experimental_rerun()
    else:
        st.write(f"Logged in as: {st.session_state.role}")
        if st.button("Logout"):
            st.session_state.update({"login": False, "role": None})
            st.experimental_rerun()
    st.write("🔑 👤 🛡️")

st.caption("Disclaimer: Estimates are approximate. Consult a licensed solar installer for exact sizing.")
st.write("The mini project is done by Thimmeshi, Kiran, Praveen, and Venkatesh.")
st.write("Guided by: Dr. Chailesh Chandra")