import streamlit as st
import pandas as pd
import extra_streamlit_components as stx

# 1. Page Configuration
st.set_page_config(
    page_title="Spooky Costume Contest",
    page_icon="🎃",
    layout="centered"
)

# 2. Cookie Manager Initialization (No caching decorator needed)
cookie_manager = stx.CookieManager()

# 3. Spooky Halloween Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 12, 41, 0.88), rgba(48, 43, 99, 0.88)), 
                    url("https://images.unsplash.com/photo-1508739773434-c26b3d09e071?q=80&w=1200&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f1f1f1;
    }

    h1 {
        color: #ff5500 !important;
        text-shadow: 0 0 10px #ff0000, 0 0 20px #ff5500, 2px 2px 5px #000;
        font-family: 'Trebuchet MS', 'Arial', sans-serif;
        text-align: center;
    }

    p, label {
        color: #e0e0e0 !important;
        font-weight: bold;
    }

    .stForm, div[data-testid="stExpander"] {
        background-color: rgba(20, 10, 30, 0.82) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 2px solid #8a2be2 !important;
        box-shadow: 0 0 20px rgba(138, 43, 226, 0.6);
    }

    .stButton > button {
        background: linear-gradient(45deg, #ff5500, #8a2be2) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border-radius: 30px !important;
        border: 2px solid #ffaa00 !important;
        padding: 12px 28px !important;
        width: 100%;
        box-shadow: 0 0 15px #ff5500;
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        transform: scale(1.04);
        box-shadow: 0 0 25px #8a2be2;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Data Initialization (Separated by Category)
if "men_votes" not in st.session_state:
    st.session_state["men_votes"] = {
        "Nexus - Spartan": 0,
        "Diego - Policeman": 0
    }

if "women_votes" not in st.session_state:
    st.session_state["women_votes"] = {
        "Margarita - Princess": 0,
        "Julia S - Pocahontas": 0,
        "Tina - Barbie": 0
    }

MEN_CONTESTANTS = list(st.session_state["men_votes"].keys())
WOMEN_CONTESTANTS = list(st.session_state["women_votes"].keys())

# Header Banner
st.markdown("<h1 style='font-size: 40px;'>🎃 Spooky Costume Contest 👻</h1>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/3815/3815316.png" width="80" style="margin: 0 10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3815/3815321.png" width="80" style="margin: 0 10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3815/3815332.png" width="80" style="margin: 0 10px;">
    </div>
""", unsafe_allow_html=True)

# Check Cookie status
has_voted_cookie = cookie_manager.get(cookie="halloween_costume_voted_2cat")

# 5. Main Voting Area
if has_voted_cookie:
    st.warning("🔒 **You have already cast your votes from this device!** Multi-voting is blocked.")
    st.info("👻 Enjoy the party! The host will reveal the winners soon.")
else:
    with st.form("spooky_vote_form", clear_on_submit=True):
        st.subheader("🕸️ Cast Your Secret Votes")
        
        # Category 1: Best Male Costume
        chosen_man = st.selectbox(
            "🕺 Best Male Costume:", 
            ["-- Select male contestant --"] + MEN_CONTESTANTS
        )
        
        st.write("---")
        
        # Category 2: Best Female Costume
        chosen_woman = st.selectbox(
            "💃 Best Female Costume:", 
            ["-- Select female contestant --"] + WOMEN_CONTESTANTS
        )
        
        submitted = st.form_submit_button("🕷️ Submit Secret Votes!")

    if submitted:
        if chosen_man == "-- Select male contestant --" or chosen_woman == "-- Select female contestant --":
            st.error("Please pick a candidate for BOTH categories before submitting!")
        else:
            # 1. Update Vote Tallies
            st.session_state["men_votes"][chosen_man] += 1
            st.session_state["women_votes"][chosen_woman] += 1

            # 2. Set Cookie on the user's browser (expires in 1 day)
            cookie_manager.set("halloween_costume_voted_2cat", "true", key="voted_cookie_set_2cat")

            st.balloons()
            st.success("🎉 **Votes Submitted Successfully!** Your phone is recorded so your votes stay secret and single-use.")
            st.rerun()

# 6. Host Admin Panel (Password Protected)
st.divider()
with st.expander("🔐 Host / Admin Results Panel"):
    password = st.text_input("Enter Host Password:", type="password")

    if password == "Costume2026":
        st.success("Access Granted, Host!")
        
        # Category 1 Results
        st.subheader("🕺 Best Male Costume Results")
        df_men = pd.DataFrame(list(st.session_state["men_votes"].items()), columns=["Contestant", "Votes"])
        df_men = df_men.sort_values(by="Votes", ascending=False)
        st.dataframe(df_men, use_container_width=True)
        st.bar_chart(df_men.set_index("Contestant"))

        st.write("---")

        # Category 2 Results
        st.subheader("💃 Best Female Costume Results")
        df_women = pd.DataFrame(list(st.session_state["women_votes"].items()), columns=["Contestant", "Votes"])
        df_women = df_women.sort_values(by="Votes", ascending=False)
        st.dataframe(df_women, use_container_width=True)
        st.bar_chart(df_women.set_index("Contestant"))

        if st.button("🔄 Reset All Tally Votes"):
            for key in st.session_state["men_votes"]:
                st.session_state["men_votes"][key] = 0
            for key in st.session_state["women_votes"]:
                st.session_state["women_votes"][key] = 0
            st.rerun()
    elif password:
        st.error("Incorrect password.")
