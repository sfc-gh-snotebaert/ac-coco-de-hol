import streamlit as st

st.title("Getting Started")
st.markdown("Set up your Snowflake environment for the workshop")

st.space("small")

st.markdown("#### Step 1: Sign up for a free trial")

with st.container(border=True):
    st.markdown("""
Go to **[signup.snowflake.com]({{SIGNUP_LINK}})** and fill out the registration form with your name, email, and company.

On the **Choose your Snowflake edition** screen, select:

| Setting | Recommended value |
|---------|-------------------|
| **Cloud provider** | Amazon Web Services (AWS) |
| **Edition** | Enterprise |
| **Region** | {{RECOMMENDED_REGION}} |

Enterprise edition is recommended because it includes all the features we use in this workshop.
""")

st.space("small")

st.markdown("#### Step 2: Activate your account")

with st.container(border=True):
    st.markdown("""
After submitting the form, Snowflake sends an **activation link** to the email address you provided. Click the link to set your password and log in.

:material/info: The activation email typically arrives within a few minutes. Check your spam folder if you don't see it.
""")

st.space("small")

st.markdown("#### Step 3: Open Cortex Code")

with st.container(border=True):
    st.markdown("""
Once logged in to Snowsight, open **Cortex Code** from the left navigation panel. This is the AI coding assistant where you will paste all prompts from this workshop.

Confirm you are using the **ACCOUNTADMIN** role — you can check and switch roles in the bottom-left of the Snowsight UI.
""")

st.space("small")

st.markdown("#### Step 4: Verify Openflow is enabled")

with st.container(border=True):
    st.markdown("""
This workshop uses **Openflow** for data ingestion from external databases. Your account has been pre-provisioned with Openflow enabled.

Verify it is available by running this SQL in a worksheet:

```sql
SHOW OPENFLOW RUNTIMES;
```

If you see an empty result set (no error), Openflow is enabled. If you get an error, notify the workshop facilitator.

:material/info: Openflow requires SPCS (Snowpark Container Services) which is pre-enabled on your trial account for this workshop.
""")

st.space("small")

st.markdown("#### Free trial details")

col1, col2, col3 = st.columns(3)
col1.metric("Duration", "30 days", help="Free trial duration from activation")
col2.metric("Credits", "$400", help="Complimentary Snowflake credits included")
col3.metric("Credit card", "Not required", help="No payment method needed to start")

st.caption("The free trial provides more than enough credits to complete the entire workshop")
