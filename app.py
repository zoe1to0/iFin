import streamlit as st

from modules.mock_data import PROFILE_DATA
from ui.event_page import render_event_analysis
from ui.guide_page import render_guide
from ui.home_page import render_home
from ui.profile_page import render_profile
from ui.report_page import render_financial_analysis
from ui.settings_page import render_settings
from ui.styles import inject_styles


st.set_page_config(
    page_title="iFin",
    page_icon="IF",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_state():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("saved_notes", PROFILE_DATA["notes"].copy())
    st.session_state.setdefault("watchlist", PROFILE_DATA["watchlist"].copy())
    st.session_state.setdefault("saved_insights", [])


def go_to(page):
    st.session_state.page = page


def render_sidebar():
    with st.sidebar:
        st.title("iFin")
        st.caption("Market insight assistant")
        nav_items = {
            "Home": "Home",
            "Events": "Event Analysis",
            "Reports": "Financial Analysis",
            "Profile": "Profile",
            "Guide": "Guide",
            "Settings": "Settings",
        }
        for label, page in nav_items.items():
            if st.button(label, width="stretch"):
                go_to(page)
                st.rerun()


inject_styles()
init_state()
render_sidebar()

page = st.session_state.page
if page == "Home":
    render_home()
elif page == "Event Analysis":
    render_event_analysis()
elif page == "Financial Analysis":
    render_financial_analysis()
elif page == "Profile":
    render_profile()
elif page == "Guide":
    render_guide()
else:
    render_settings()
