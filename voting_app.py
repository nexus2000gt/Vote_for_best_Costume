import streamlit
import pandas
import sqlite3
import secrets
import hmac
from datetime import datetime, timezone

from streamlit_cookies_controller import CookieController


st = streamlit
pd = pandas

st.set_page_config(
    page_title="Halloween Costume Voting",
    page_icon="🎃",
    layout="wide",
)

DB_PATH = "halloween_votes.db"
COOKIE_NAME = "costume_vote_submitted"
LOCAL_TESTING_ONLY = False

MALE_CANDIDATES = [
    "Leonidas/Spartan",
    "Calzetin con rombos-man",
    "Dinosaur",
    "Mario & Yoshi",
    "Wrestler man",
    "Model",
    "Male Scarecrow",
    "Star Lord",
    "Edward Cullen",
    "Wolverine",
    "Snail",
    "Google Teams",
    "Chef (Ratatouille)",
]

FEMALE_CANDIDATES = [
    "Black swan",
    "Mavka (Ukranian magical creature)",
    "Alien",
    "Nagini",
    "Peach",
    "Harley Quinn's daughter",
    "Wrestler girl",
    "Female Scarecrow",
    "Gamora",
    "Mushroom",
    "She ware-wolf",
    "Britney Spears",
    "Remi (Ratatouille)",
]

OTHER_OPTION = "Other"

st.markdown(
    """
    <style>
    .stApp {
        color: #f8eefc;
        background:
            radial-gradient(circle at top, #3b1555 0%, #190c26 42%, #07040b 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12081c 0%, #281137 100%);
    }

    h1, h2, h3 {
        color: #ff8a1c !important;
        text-shadow: 0 0 8px rgba(184, 78, 255, 0.8);
    }

    .spooky-card {
        padding: 1rem 1.2rem;
        margin: 0.75rem 0 1.25rem 0;
        border: 1px solid #9146d8;
        border-radius: 14px;
        background: rgba(22, 9, 33, 0.88);
        box-shadow: 0 0 18px rgba(145, 70, 216, 0.28);
    }

    .small-note {
        color: #dccce5;
        font-size: 0.9rem;
    }

    div.stButton > button {
        border: 1px solid #ff8a1c;
        border-radius: 10px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def open_connection():
    connection = sqlite3.connect(DB_PATH, timeout=5.0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database():
    connection = open_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS ballots(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                male_choice TEXT NOT NULL,
                female_choice TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_ballots_male_choice
            ON ballots(male_choice);

            CREATE INDEX IF NOT EXISTS idx_ballots_female_choice
            ON ballots(female_choice);
            """
        )
    finally:
        connection.close()


def submit_vote(male_choice, female_choice):
    connection = open_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        connection.execute(
            """
            INSERT INTO ballots(
                male_choice,
                female_choice,
                submitted_at
            )
            VALUES (?, ?, ?)
            """,
            (
                male_choice,
                female_choice,
                utc_timestamp(),
            ),
        )

        connection.commit()
        return "success"

    except sqlite3.Error:
        connection.rollback()
        return "database_error"

    finally:
        connection.close()


def load_results():
    connection = open_connection()

    try:
        turnout_row = connection.execute(
            "SELECT COUNT(*) AS total FROM ballots"
        ).fetchone()

        turnout = int(turnout_row["total"])

        male_results = pd.read_sql_query(
            """
            SELECT male_choice AS candidate, COUNT(*) AS votes
            FROM ballots
            GROUP BY male_choice
            ORDER BY votes DESC, candidate COLLATE NOCASE
            """,
            connection,
        )

        female_results = pd.read_sql_query(
            """
            SELECT female_choice AS candidate, COUNT(*) AS votes
            FROM ballots
            GROUP BY female_choice
            ORDER BY votes DESC, candidate COLLATE NOCASE
            """,
            connection,
        )

        return turnout, male_results, female_results

    finally:
        connection.close()


def reset_votes():
    connection = open_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM ballots")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name = 'ballots'"
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_admin_password():
    try:
        password = str(st.secrets["admin_password"])

        if password:
            return password

    except Exception:
        pass

    if LOCAL_TESTING_ONLY:
        return "Costume2026"

    return None


def resolve_choice(selected_choice, other_text, category_label):
    if selected_choice != OTHER_OPTION:
        return selected_choice, None

    custom_choice = other_text.strip()

    if not custom_choice:
        return None, f"Enter the Other contestant for {category_label}."

    if len(custom_choice) > 80:
        return None, f"The Other contestant for {category_label} is too long."

    return custom_choice, None


def render_vote_page(cookie_controller):
    st.title("🎃 Halloween Costume Voting")

    st.markdown(
        """
        <div class="spooky-card">
            Vote for one contestant in each category.
            <div class="small-note">
                One submission is allowed per person.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    browser_marker = cookie_controller.get(COOKIE_NAME)

    session_marker = st.session_state.get(
        "vote_submitted_this_session",
        False,
    )

    if browser_marker or session_marker:
        st.warning(
            "This browser has already submitted a vote. If you believe this "
            "is incorrect, please ask the host for help."
        )
        return

    with st.form("costume_vote_form", clear_on_submit=False):
        st.subheader("🕺 Best Male Costume")

        male_selected = st.selectbox(
            "Choose the men's costume",
            MALE_CANDIDATES + [OTHER_OPTION],
            index=None,
            placeholder="Choose a contestant",
        )

        male_other = st.text_input(
            "Other men's contestant, only if Other is selected",
            max_chars=80,
        )

        st.subheader("💃 Best Female Costume")

        female_selected = st.selectbox(
            "Choose the women's costume",
            FEMALE_CANDIDATES + [OTHER_OPTION],
            index=None,
            placeholder="Choose a contestant",
        )

        female_other = st.text_input(
            "Other women's contestant, only if Other is selected",
            max_chars=80,
        )

        submitted = st.form_submit_button(
            "🕷️ Submit ballot",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if cookie_controller.get(COOKIE_NAME):
        st.warning(
            "This browser already has a vote reminder. No ballot was saved."
        )
        return

    if male_selected is None or female_selected is None:
        st.error("Choose one contestant in each category.")
        return

    male_choice, male_error = resolve_choice(
        male_selected,
        male_other,
        "the men's category",
    )

    female_choice, female_error = resolve_choice(
        female_selected,
        female_other,
        "the women's category",
    )

    if male_error:
        st.error(male_error)
        return

    if female_error:
        st.error(female_error)
        return

    result = submit_vote(male_choice, female_choice)

    if result == "success":
        cookie_controller.set(
            COOKIE_NAME,
            secrets.token_urlsafe(32),
        )

        st.session_state.vote_submitted_this_session = True

        st.success("Your ballot was recorded. Happy Halloween! 🎉")
        st.balloons()

    else:
        st.error(
            "The vote could not be saved. No ballot was recorded."
        )


def render_chart(title, result_frame):
    st.subheader(title)

    if result_frame.empty:
        st.info("No votes have been recorded in this category.")
        return

    chart_frame = result_frame.set_index("candidate")[["votes"]]

    st.bar_chart(chart_frame)

    st.dataframe(
        result_frame,
        hide_index=True,
        use_container_width=True,
    )


def render_admin_page(cookie_controller):
    st.title("🔐 Admin Results")

    admin_password = get_admin_password()

    if admin_password is None:
        st.error(
            "Admin access is disabled because st.secrets['admin_password'] "
            "is not configured."
        )
        return

    if LOCAL_TESTING_ONLY:
        st.warning(
            "LOCAL TESTING ONLY is enabled. Disable it before deployment."
        )

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        entered_password = st.text_input(
            "Admin password",
            type="password",
        )

        if st.button("Log in", type="primary"):
            if hmac.compare_digest(entered_password, admin_password):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect admin password.")

        return

    header_left, header_right = st.columns([4, 1])

    with header_left:
        st.success("Admin access granted.")

    with header_right:
        if st.button("Log out", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    turnout, male_results, female_results = load_results()

    st.metric("Total ballots submitted", turnout)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        render_chart("🧛 Men's results", male_results)

    with chart_col2:
        render_chart("🧙‍♀️ Women's results", female_results)

    st.divider()
    st.subheader("⚠️ Reset all voting data")

    st.warning(
        "This permanently deletes every ballot. It does not remove cookies "
        "from other guests' browsers."
    )

    reset_confirmed = st.checkbox(
        "I understand that this permanently deletes all voting results."
    )

    if st.button(
        "🗑️ Reset all votes",
        disabled=not reset_confirmed,
    ):
        try:
            reset_votes()

            # Clears the cookie for the browser currently used by the host.
            cookie_controller.remove(COOKIE_NAME)

            st.session_state.pop(
                "vote_submitted_this_session",
                None,
            )

            st.success("All voting records were deleted.")
            st.rerun()

        except sqlite3.Error:
            st.error(
                "The reset failed. The database transaction was rolled back."
            )


initialize_database()

cookie_controller = CookieController()

page = st.sidebar.radio(
    "Navigation",
    ["🎃 Vote", "🔐 Admin results"],
)

st.sidebar.caption(
    "One casual vote per browser cookie."
)

if page == "🎃 Vote":
    render_vote_page(cookie_controller)
else:
    render_admin_page(cookie_controller)
