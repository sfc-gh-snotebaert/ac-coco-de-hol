import streamlit as st

SESSION_PROMPTS = {
    1: ["Prompt 1.1", "Prompt 1.2", "Prompt 1.3"],
    2: ["Prompt 2.1", "Prompt 2.2", "Prompt 2.3"],
    3: ["Prompt 3.1", "Prompt 3.2", "Prompt 3.3"],
    4: ["Prompt 4.1", "Prompt 4.2", "Prompt 4.3"],
    5: ["Prompt 5.1", "Prompt 5.2"],
}


def _done_store() -> dict:
    if "_done" not in st.session_state:
        st.session_state["_done"] = {}
    return st.session_state["_done"]


def _prompt_key(prompt_id: str) -> str:
    return prompt_id.replace(" ", "_").replace(".", "_")


def _on_toggle(prompt_id: str):
    key = _prompt_key(prompt_id)
    _done_store()[key] = st.session_state[f"_cb_{key}"]


def is_session_complete(session_num: int) -> bool:
    prompts = SESSION_PROMPTS.get(session_num, [])
    store = _done_store()
    return len(prompts) > 0 and all(
        store.get(_prompt_key(p), False) for p in prompts
    )


def render_prompt(prompt_id: str, title: str, prompt_text: str):
    key = _prompt_key(prompt_id)
    cb_key = f"_cb_{key}"
    store = _done_store()
    if cb_key not in st.session_state:
        st.session_state[cb_key] = store.get(key, False)
    with st.container(border=True):
        header_col, check_col = st.columns([5, 1])
        with header_col:
            st.markdown(f"#### :material/terminal: {prompt_id} - {title}")
        with check_col:
            st.checkbox(
                "Done",
                key=cb_key,
                on_change=_on_toggle,
                args=(prompt_id,),
            )
        st.caption("Copy this prompt and paste it into Cortex Code")
        st.code(prompt_text, language="text", wrap_lines=True)


def render_explanation(title: str, body: str):
    with st.expander(f":material/school: {title}", expanded=False):
        st.markdown(body)


def render_technology_card(name: str, description: str, icon: str = "widgets"):
    with st.container(border=True):
        st.markdown(f":material/{icon}: **{name}**")
        st.caption(description)


def render_technologies_used(technologies: list[dict]):
    st.markdown("##### :material/build: Technologies used in this session")
    cols = st.columns(min(len(technologies), 3))
    for i, tech in enumerate(technologies):
        with cols[i % len(cols)]:
            render_technology_card(
                tech["name"], tech["description"], tech.get("icon", "widgets")
            )


def render_session_header(
    session_num: int,
    title: str,
    time_range: str,
    duration: str,
    building: str,
):
    st.title(f"Session {session_num}: {title}")
    col1, col2 = st.columns(2)
    col1.markdown(f":material/schedule: **{time_range}** ({duration})")
    col2.markdown(f":material/construction: **Building**: {building}")
    st.space("small")


def render_key_concepts(concepts: list[dict]):
    st.markdown("##### :material/lightbulb: Key concepts")
    for concept in concepts:
        with st.expander(f"**{concept['term']}**"):
            st.markdown(concept["definition"])


def render_what_you_built(items: list[str]):
    st.markdown("##### :material/check_circle: What you built in this session")
    for item in items:
        st.markdown(f"- :green-badge[Done] {item}")
