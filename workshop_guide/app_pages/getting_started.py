import streamlit as st

st.title("Getting Started")
st.markdown("Set up your Snowflake environment for the workshop")

st.space("small")

st.markdown("#### Step 1: Gather your credentials")

with st.container(border=True):
    st.markdown("""
Before the workshop, you received an **email from the facilitator** containing your pre-provisioned Snowflake account details:

- **Account URL** — the link to your Snowflake environment
- **Username**: LABUSERXX
- **Password**: CHANGE_ME_2026!

Locate this email and keep the credentials handy.

:material/info: Check your spam folder if you don't see the email. If you can't find it, contact the workshop facilitator.
""")

st.space("small")

st.markdown("#### Step 2: Log in to the account")

with st.container(border=True):
    st.markdown("""
Open the **account URL** from the email in your browser and log in with the provided **username** and **password**.

Ensure that the role **OPENFLOW_ADMIN** is selected in the role picker (bottom left Snowsight menu).

Once logged in to Snowsight, open **CoCo** by clicking on the blue button with a star in the bottom right of your Snowsight window — this is the AI coding assistant where you will paste all prompts from this workshop.
""")
