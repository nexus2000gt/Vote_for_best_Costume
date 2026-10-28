import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Spooky Costume Contest",
    page_icon="🎃",
    layout="centered"
)

# 2. Spooky Halloween Styling
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
        margin-bottom: 0px !important;
    }

    h3 {
        color: #bb86fc !important;
        text-shadow: 0 0 8px #8a2be2;
    }

    p, label {
        color: #e0e0e0 !important;
        font-weight: bold;
    }

    div[data-testid="stForm"], div[data-testid="stExpander"] {
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
        font-size: 18px !important;
        border-radius: 30px !important;
        border: 2px solid #ffaa00 !important;
        padding: 10px 24px !important;
        width: 100%;
        box-shadow: 0 0 15px #ff5500;
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 25px #8a2be2, 0 0 10px #ff5500;
        color: #ffeb3b !important;
    }

    /* Large Glowing Emojis Banner */
    .spooky-emoji-banner {
        text-align: center;
        font-size: 55px;
        margin: 15px 0;
        text-shadow: 0 0 15px #ff5500, 0 0 25px #8a2be2;
    }
    </style>
""", unsafe_allow_html=True)


# 3. GLOBAL SHARED DATA STORAGE
@st.cache_resource
def get_global_data():
    return {
        "voted_guests": set(),
        "men_votes": {
            "Leonidas/Spartan": 0,
            "Calzetin con rombos-man": 0,
            "Dinosaur": 0,
            "Mario & Yoshi": 0,
            "Wrestler man": 0,
            "Model": 0,
            "Male Scarecrow": 0,
            "Star Lord": 0,
            "Edward Cullen": 0,
            "Wolverine": 0,
            "Snail": 0,
            "Google Teams": 0,
            "Remi (Ratatouille)": 0,
        },
        "women_votes": {
            "Black swan": 0,
            "Mavka (Ukranian magical creature)": 0,
            "Alien": 0,
            "Nagini": 0,
            "Peach": 0,
            "Harley Quinn's daughter": 0,
            "Wrestler girl": 0,
            "Female Scarecrow": 0,
            "Gamora": 0,
            "Mushroom": 0,
            "She ware-wolf": 0,
            "Britney Spears": 0,
            "Chef (Ratatouille)": 0,
        }
    }

data = get_global_data()

# Guest list (List of all eligible voters)
GUESTS = [
    "Angel", "Nexus", "Margarita", "Tina", "Diego Ruiz", "Julia Stefanini",
    "Alex Rivas", "Dariana", "Yherman Alejandro", "Yisbeth", "Karolina Anderson",
    "Angel", "Frida", "Carlos Sanchez (Jarochito)", "Natalia de Jarocho", "Frida" "Ivan Santana",
    "Olaya", "Luis Daniel", "Marta", "Marco", "Mateusz", "Wera-duża",
    "Wera-mała", "Sonya", "Kateryna", "Zair", "Larisa",
    "Adriana Ayala", "Witek", "Miguel", "Eliza", "Ruslan", "Vasya", "Edson", "Vanshi", "Klaudia M.", "Luka"
]

# Header Banner
st.markdown("<h1 style='font-size: 40px;'>🎃 Spooky Costume Contest 👻</h1>", unsafe_allow_html=True)
st.markdown("<div class='spooky-emoji-banner'>🦇 🎃 💀 🕷️ 🕯️ 🕸️ 🧛</div>", unsafe_allow_html=True)

# 4. Main Voting Form (using normal widgets with a form container or state management)
# To allow instant UI updates when choosing "Other", we handle selects outside a strict st.form, 
# or use widget keys. Let's use standard widgets with a submit block.

st.subheader("🕸️ Select Your Name & Cast Votes")

# Voter Identity
voter_name = st.selectbox("👤 Who are you?", ["-- Select your name --"] + GUESTS)

st.write("---")

# Category 1: Best Male Costume
men_options = list(data["men_votes"].keys()) + ["Other (Type below)"]
chosen_man_selection = st.selectbox("🕺 Best Male Costume:", ["-- Select male contestant --"] + men_options)

custom_man = ""
if chosen_man_selection == "Other (Type below)":
    custom_man = st.text_input("✍️ Enter custom Male Costume name:")

st.write("---")

# Category 2: Best Female Costume
women_options = list(data["women_votes"].keys()) + ["Other (Type below)"]
chosen_woman_selection = st.selectbox("💃 Best Female Costume:", ["-- Select female contestant --"] + women_options)

custom_woman = ""
if chosen_woman_selection == "Other (Type below)":
    custom_woman = st.text_input("✍️ Enter custom Female Costume name:")

st.write("---")

# Submission Button
if st.button("🕷️ Submit Secret Votes!"):
    # Resolve final choices (handling "Other" inputs)
    final_man = custom_man.strip() if chosen_man_selection == "Other (Type below)" else chosen_man_selection
    final_woman = custom_woman.strip() if chosen_woman_selection == "Other (Type below)" else chosen_woman_selection

    if voter_name == "-- Select your name --":
        st.error("Please select your name from the guest list!")
    elif chosen_man_selection == "-- Select male contestant --" or chosen_woman_selection == "-- Select female contestant --":
        st.error("Please choose a contestant for BOTH categories!")
    elif chosen_man_selection == "Other (Type below)" and not custom_man.strip():
        st.error("Please write down the name of the custom Male costume!")
    elif chosen_woman_selection == "Other (Type below)" and not custom_woman.strip():
        st.error("Please write down the name of the custom Female costume!")
    elif voter_name in data["voted_guests"]:
        st.warning(f"⚠️ **{voter_name}**, a vote has already been submitted under your name!")
    else:
        # Dynamically add custom contestants to dictionaries if they don't exist yet
        if final_man not in data["men_votes"]:
            data["men_votes"][final_man] = 0
        if final_woman not in data["women_votes"]:
            data["women_votes"][final_woman] = 0

        # Record Secret Vote globally
        data["men_votes"][final_man] += 1
        data["women_votes"][final_woman] += 1
        data["voted_guests"].add(voter_name)

        st.balloons()
        st.success(f"🎉 **Thank you, {voter_name}!** Your secret votes have been registered globally!")

# 5. Host Admin Panel (Password Protected)
st.divider()
with st.expander("🔐 Host / Admin Results Panel"):
    st.write("Access the host dashboard:")
    
    admin_form = st.form("admin_login_form")
    password = admin_form.text_input("Enter Host Password:", type="password")
    admin_login = admin_form.form_submit_button("🔑 Enter Admin Panel")

    if admin_login:
        if password == "Costume2026":
            st.session_state["costume_admin_logged_in"] = True
        else:
            st.session_state["costume_admin_logged_in"] = False
            st.error("Incorrect password.")

    if st.session_state.get("costume_admin_logged_in", False):
        st.success("Access Granted, Nexus!")
        
        st.write(f"**Total Voters:** {len(data['voted_guests'])} / {len(GUESTS)}")
        st.write(f"**Guests Who Voted:** {', '.join(data['voted_guests']) if data['voted_guests'] else 'None yet'}")
        st.write("---")

        # Category 1 Results
        st.subheader("🕺 Best Male Costume Results")
        df_men = pd.DataFrame(list(data["men_votes"].items()), columns=["Contestant", "Votes"]).sort_values(by="Votes", ascending=False)
        st.dataframe(df_men, use_container_width=True)
        st.bar_chart(df_men.set_index("Contestant"))

        st.write("---")

        # Category 2 Results
        st.subheader("💃 Best Female Costume Results")
        df_women = pd.DataFrame(list(data["women_votes"].items()), columns=["Contestant", "Votes"]).sort_values(by="Votes", ascending=False)
        st.dataframe(df_women, use_container_width=True)
        st.bar_chart(df_women.set_index("Contestant"))

        if st.button("🔄 Reset All Tally Votes"):
            data["voted_guests"].clear()
            for key in list(data["men_votes"].keys()):
                data["men_votes"][key] = 0
            for key in list(data["women_votes"].keys()):
                data["women_votes"][key] = 0
            st.success("All votes have been reset!")
            st.rerun()
