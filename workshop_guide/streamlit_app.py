from pathlib import Path

import streamlit as st

from components import is_session_complete

_DIR = Path(__file__).parent


def _title(session_num: int, label: str) -> str:
    check = " :green[:material/check_circle:]" if is_session_complete(session_num) else ""
    return f"{session_num}. {label}{check}"


st.set_page_config(
    page_title="{{WORKSHOP_TITLE}}",
    page_icon="{{PAGE_ICON}}",
    layout="wide",
)

st.logo(
    str(_DIR / "static" / "snowflake_full_logo.png"),
    icon_image=str(_DIR / "static" / "snowflake_logo.png"),
)

page = st.navigation(
    {
        "": [
            st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
            st.Page("app_pages/getting_started.py", title="Getting Started", icon=":material/rocket_launch:"),
            st.Page("app_pages/agenda.py", title="Agenda", icon=":material/calendar_today:"),
        ],
        "Block 1: Ingestion": [
            st.Page("app_pages/session_01.py", title=_title(1, "Environment Setup"), icon=":material/settings:"),
            st.Page("app_pages/session_02.py", title=_title(2, "Enterprise Ingestion"), icon=":material/cloud_download:"),
        ],
        "Block 2: EDW & Optimization": [
            st.Page("app_pages/session_03.py", title=_title(3, "EDW Pipeline (dbt)"), icon=":material/build_circle:"),
            st.Page("app_pages/session_04.py", title=_title(4, "Code Review"), icon=":material/rate_review:"),
            st.Page("app_pages/session_05.py", title=_title(5, "DE Skill (Stretch)"), icon=":material/psychology:"),
        ],
    },
    position="sidebar",
)

page.run()
