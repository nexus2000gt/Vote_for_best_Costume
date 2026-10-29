import streamlit
import pandas
import sqlite3
import hashlib
import secrets
import hmac
from datetime import datetime, timezone

from streamlit_cookies_controller import CookieController


st = streamlit
pd = pandas

st.set_page_config(
    page_title="Halloween Costume Voting",
    page_icon="ðŸŽƒ",
    layout="wide",
)

DB_PATH = "halloween_votes.db"
COOKIE_NAME = "costume_vote_submitted"
LOCAL_TESTING_ONLY = False

ELIGIBLE_VOTERS = [
    'Angel',
    'Nexus',
    'Margarita',
    'Tina',
    'Diego Ruiz',
    'Julia Stefanini',
    'Alex Rivas',
    'Dariana',
    'Yherman Alejandro',
    'Yisbeth',
    'Karolina Anderson',
    'Frida',
    'Carlos Sanchez (Jarochito)',
    'Natalia de Jarocho',
    'Ivan Santana',
    'Olaya',
    'Luis Daniel',
    'Marta',
    'Marco',
    'Mateusz',
    'Wera-duża',
    'Wera-mała',
    'Sonya',
    'Kateryna',
    'Zair',
    'Larisa',
    'Kamil',
    'Nastia',
    'Kasia D',
    'Adrian',
    'Adriana Ayala',
    'Witek',
    'Miguel',
    'Eliza',
    'Ruslan',
    'Vasya',
    'Edson',
    'Vanshi',
    'Klaudia M.',
    'Luka',
]

# Only SHA-256 hashes are stored here. Plaintext voter PINs are kept solely in
# the separate organizer-only mapping file.
PIN_HASHES = {
    'Angel': '03f65a290e11d78647e557030042d74d268521768c4a1648264a1b38047a4b37',
    'Nexus': 'ae600959378c54c51d1b867e77cef34eba55658bf2abcec187cfe901526d0a80',
    'Margarita': 'a7d2a606c6ce4168f1f88c3b11afb70472841708b221f666323e68a95c91c173',
    'Tina': '07a0708ed8472c991e0545aaf3433da3b61de39001f6dc3706516c13f3d49e52',
    'Diego Ruiz': 'f85dd1cb11c453b93c052d8dcf30b925aa4082f1e992c5ad51b762cb97bdf153',
    'Julia Stefanini': 'e85a870aeb6eed9e560269c22f3f3d0823a5a1aa6536bb1bf8d90621b9e70fd1',
    'Alex Rivas': '64f363361a0acc78ce6d9e6240ca840dfc9a338bab1a2fcb7c6270baf81b1f86',
    'Dariana': '8e5fabc4550b9c8521b119ede0270237fd4891a697330a2ef5fdea4dde53bf13',
    'Yherman Alejandro': 'f36e412aea00d7c622f3d331c5ceec42eaf18bda2d0374971a09fc79d7d9f293',
    'Yisbeth': '560b29022e637e13a843d6e32927a666e6a00edf0dbef9b6c29495b34512a103',
    'Karolina Anderson': 'ee932b02fc14995ab1085f9c686b916d3dd5d21361ca4c20923965257334991d',
    'Frida': '3f14a60b7590cb27fad945421e73a7f76c1125f3fd982e96a110ad1c9929b9da',
    'Carlos Sanchez (Jarochito)': 'f309ff5ddc25bf94b74483e860148a0b0d1069c45dfdbacbb6ceeecdda167487',
    'Natalia de Jarocho': 'cc4996f23b1298387d649919eaa4f4f1f1c26ef836af118ca1334a366efbf979',
    'Ivan Santana': 'e96e85632cd66c4c1d9184b1d85eeaa66b830386ccb69d1f9fed089c30b92c82',
    'Olaya': 'fd0d5cf8daff925c6e741eaf958ef32b31ebb0109bd575ad2a78af30860d8a08',
    'Luis Daniel': '5b7267c26cc279fdbe97b434c889c0ec3831f2294b19e4b8a9228de154551503',
    'Marta': 'e485f271f7db87ad8888f40c7b00412cc0c97c9bbf35790e7ba85e08ff602860',
    'Marco': '7b3b4e5fed79d4b93089785bd5654a021da6426cd154e1b98a630be06a50f281',
    'Mateusz': 'e7bb14f4c55efcc91e049546838499c176b2f0e01c2161bd9517c32cd1f3a37b',
    'Wera-duża': '9b5173ba93decd311f89513f060a62d652ec189f0dba97db15c2a07787add029',
    'Wera-mała': '152bf02d1a3d3094d00cbce4933d5e38a402fa94ebad8c225e03fd98a3483441',
    'Sonya': '0193d52e5b14627091d6163a8546c79f708bb374ba31f9d5b1173e028a96ca0f',
    'Kateryna': '92c23d77b6b8e8327128859040f3feddb2fbdc914a09f8d37e222f30b4f1a38c',
    'Zair': '77f16846583961d1e1e490d0cb58e1bd65898159b6327ef400bd5000eb2394bd',
    'Larisa': '33e335ace8e8fbf3dfeef681c26f238b9a79428447db482dda0a2656f1c12295',
    'Kamil': 'da37e500c65ac7c6de9d491e531836b3e866dd1b05a445b30714744469d07411',
    'Nastia': '1395d0b76b56509da2cd59c06ca9522cc2b7aff483dcd622b507c21e74613278',
    'Kasia D': '0c49468f854e20a591f566e2bd39700725de0d288a564ac7be82eba1b85b75b9',
    'Adrian': '478052290f5e77d85bbb7105568d4839d62081096a8685816c15e14604427f82',
    'Adriana Ayala': '4044d96743cebcaa244ac6c35d068d28dabe7c628f8f912ad6bc8330cd6647f3',
    'Witek': '808ba8c29edb1f89bc1a44969fddfb1fef9a8e4996a84bbc8c3502e2435652de',
    'Miguel': 'fb420d1701eecd8f951f3834671277144b3287908bf698f5c0ef2fdacd6eb655',
    'Eliza': '953abe48dfdfa8e256eca457f2987a119d7bf4fddc4964cde3b3b9bd12fb2d5c',
    'Ruslan': '5f7635b6a1c0307fd33f4270e2b1437795d6f63612f13f684648bd2e6ff119c1',
    'Vasya': 'a00c249b224dde8430dda29aad26db3b58af0706c048efa3258818a4e22b4386',
    'Edson': '3c7a32a431aaaf0fba3365e2b56a23aa859c578c15618b0da2938411ec3b49ba',
    'Vanshi': 'b8f935f6c4dc97d265b9ae01b575162cc132fb2ce3308af03c4363c398c950e7',
    'Klaudia M.': '0d326e09800891fbc9b35ae697a3889817b6dc094f4d68b7d99f9ada813b8f9a',
    'Luka': 'badc1520e836916367a6eeaf8953e9bea0c7ca2cb1832b1994dbf07b53866548',
}

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
    """Return one fresh SQLite connection for one short operation."""
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
            CREATE TABLE IF NOT EXISTS participation(
                voter_name TEXT PRIMARY KEY,
                voted_at TEXT NOT NULL
            );

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


def authenticate_voter(voter_name, entered_pin):
    """Authenticate the selected voter entirely on the server."""
    if voter_name not in PIN_HASHES:
        return False

    if len(entered_pin) != 4 or not entered_pin.isdigit():
        return False

    entered_hash = hashlib.sha256(entered_pin.encode("utf-8")).hexdigest()
    return hmac.compare_digest(entered_hash, PIN_HASHES[voter_name])


def submit_vote(voter_name, male_choice, female_choice):
    """
    Atomically reserve the voter name and write the anonymous ballot.

    The participation primary key is the authoritative one-vote control.
    The ballots table deliberately has no voter name or participation foreign
    key, so results cannot directly map a voter to their choices.
    """
    connection = open_connection()
    submitted_at = utc_timestamp()

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            INSERT INTO participation(voter_name, voted_at)
            VALUES (?, ?)
            """,
            (voter_name, submitted_at),
        )
        connection.execute(
            """
            INSERT INTO ballots(male_choice, female_choice, submitted_at)
            VALUES (?, ?, ?)
            """,
            (male_choice, female_choice, submitted_at),
        )
        connection.commit()
        return "success"
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        if "participation.voter_name" in str(exc):
            return "duplicate"
        return "integrity_error"
    except sqlite3.Error:
        connection.rollback()
        return "database_error"
    finally:
        connection.close()


def load_results():
    connection = open_connection()
    try:
        turnout_row = connection.execute(
            "SELECT COUNT(*) AS total FROM participation"
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
        connection.execute("DELETE FROM participation")
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
        password = str(st.secrets['admin_password'])
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
    st.title("ðŸŽƒ Halloween Costume Voting")
    st.markdown(
        """
        <div class="spooky-card">
            Select your own name, enter your assigned four-digit PIN, and vote
            for one contestant in each category.
            <div class="small-note">
                The browser cookie is an additional reminder only. The database
                primary key is the authoritative one-vote-per-name control.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    browser_marker = cookie_controller.get('costume_vote_submitted')
    session_marker = st.session_state.get("vote_submitted_this_session", False)

    if browser_marker or session_marker:
        st.warning(
            "This browser has a previous-vote reminder. Voting is blocked on "
            "this device as an additional deterrent only. Cookies can be "
            "cleared and are not the security boundary. If this reminder is "
            "incorrect and you have not voted, ask the host for help."
        )
        return

    with st.form("costume_vote_form", clear_on_submit=False):
        voter_name = st.selectbox(
            "Your name",
            ELIGIBLE_VOTERS,
            index=None,
            placeholder="Choose your own name",
        )
        voter_pin = st.text_input(
            "Your assigned 4-digit PIN",
            type="password",
            max_chars=4,
        )

        st.subheader("ðŸ§› Men's costume")
        male_selected = st.selectbox(
            "Choose the men's costume",
            MALE_CANDIDATES + [OTHER_OPTION],
            index=None,
            placeholder="Choose a contestant",
        )
        male_other = st.text_input(
            "Other men's contestant",
            max_chars=80,
            help="Used only when Other is selected.",
        )

        st.subheader("ðŸ§™â€â™€ï¸ Women's costume")
        female_selected = st.selectbox(
            "Choose the women's costume",
            FEMALE_CANDIDATES + [OTHER_OPTION],
            index=None,
            placeholder="Choose a contestant",
        )
        female_other = st.text_input(
            "Other women's contestant",
            max_chars=80,
            help="Used only when Other is selected.",
        )

        submitted = st.form_submit_button(
            "ðŸ•¯ï¸ Submit ballot",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    # Check the browser reminder again before any database write.
    if cookie_controller.get('costume_vote_submitted'):
        st.warning(
            "This browser already has a previous-vote reminder. No database "
            "submission was attempted. Ask the host for help if it is wrong."
        )
        return

    if not voter_name:
        st.error("Choose your own name.")
        return

    if not authenticate_voter(voter_name, voter_pin):
        st.error("The selected name and PIN do not match.")
        return

    if male_selected is None or female_selected is None:
        st.error("Choose one contestant in each category.")
        return

    male_choice, male_error = resolve_choice(
        male_selected, male_other, "the men's category"
    )
    female_choice, female_error = resolve_choice(
        female_selected, female_other, "the women's category"
    )

    if male_error:
        st.error(male_error)
        return
    if female_error:
        st.error(female_error)
        return

    result = submit_vote(voter_name, male_choice, female_choice)

    if result == "success":
        random_value = secrets.token_urlsafe(32)
        cookie_controller.set('costume_vote_submitted', random_value)
        st.session_state.vote_submitted_this_session = True
        st.success("Your ballot was recorded. Happy Halloween! ðŸŽ‰")
        st.balloons()
    elif result == "duplicate":
        st.error(
            "A vote has already been submitted for this name. No second "
            "ballot was recorded. Ask the host if you believe this is wrong."
        )
    else:
        st.error(
            "The vote could not be saved. The transaction was rolled back, "
            "so no partial ballot was recorded."
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


def render_admin_page():
    st.title("ðŸ” Admin Results")

    admin_password = get_admin_password()
    if admin_password is None:
        st.error(
            "Admin access is disabled because st.secrets['admin_password'] "
            "is not configured. Add it to .streamlit/secrets.toml. The "
            "Costume2026 fallback works only when LOCAL_TESTING_ONLY is "
            "deliberately changed to True."
        )
        return

    if LOCAL_TESTING_ONLY:
        st.warning(
            "LOCAL TESTING ONLY is enabled. Disable it and configure "
            "st.secrets['admin_password'] before deployment."
        )

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        entered_password = st.text_input("Admin password", type="password")
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

    col1, col2 = st.columns(2)
    col1.metric("Turnout", turnout)
    col2.metric("Eligible voters", len(ELIGIBLE_VOTERS))

    st.caption(
        "Only aggregate results and the turnout count are displayed. "
        "The admin panel does not show voter names or a voter-to-choice map."
    )

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    render_chart("🧛 Men's results", male_results)

with chart_col2:
    render_chart("🧙‍♀️ Women's results", female_results)

st.divider()
st.subheader("⚠️ Reset all voting data")
st.warning(
    "This permanently deletes participation and ballot records. It does "
    "not remove reminder cookies already stored in guests' browsers."
)

reset_confirmed = st.checkbox(
    "I understand that this permanently deletes all voting results."
)

if st.button(
        "Reset all votes",
        disabled=not reset_confirmed,
    ):
        try:
            reset_votes()
            st.success("All database voting records were deleted.")
            st.rerun()
        except sqlite3.Error:
            st.error(
                "The reset failed. The transaction was rolled back."
            )


initialize_database()

cookie_controller = CookieController()

page = st.sidebar.radio(
    "Navigation",
    ["🎃 Vote", "🔐 Admin results"],
)

st.sidebar.caption(
    "One atomic database submission per eligible voter name."
)

if page == "🎃 Vote":
    render_vote_page(cookie_controller)
else:
    render_admin_page()
