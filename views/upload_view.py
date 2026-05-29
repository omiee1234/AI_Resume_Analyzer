"""
views/upload_view.py
────────────────────
Streamlit rendering for the upload panel and company-specific input form.
Returns data to app.py; no AI calls here.
"""

import streamlit as st


def render_upload_section():
    """
    Render the file-uploader widget.

    Returns
    -------
    UploadedFile | None
    """
    st.subheader("Upload Your Resume")
    st.markdown(
        "Upload a PDF or DOCX file and let the analyzer extract key resume details for ATS scoring."
    )
    return st.file_uploader(
        "Choose a resume file",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX",
    )


def render_analysis_type_selector() -> str:
    """
    Render the analysis-type radio and return the selected value.

    Returns
    -------
    str  "General" or "HR Chatbot"
    """
    st.subheader("Choose Analysis Type")

    return st.radio(
        "Select Analysis",
        ["General", "HR Chatbot"],
        label_visibility="collapsed",
        horizontal=True,
    )


def render_hr_chatbot_input():
    """
    Render HR chatbot query input for candidate suitability checks.

    Returns
    -------
    tuple[str, bool]
        (hr_question, ok_clicked)
    """
    st.subheader("HR Chat - Ask About Candidate Suitability")
    st.markdown("Use quick questions or type a custom HR suitability query below.")

    quick_questions = [
        "Is this candidate suitable for a senior role?",
        "What are their strongest technical skills?",
        "What salary range is appropriate?",
        "What gaps should we probe in an interview?",
        "Culture fit for a startup?",
    ]

    # ── Init session state ────────────────────────────────────────────────────
    if "hr_question_input" not in st.session_state:
        st.session_state.hr_question_input = ""
    if "hr_quick_clicked" not in st.session_state:
        st.session_state.hr_quick_clicked = False

    # ── Quick question buttons ────────────────────────────────────────────────
    cols = st.columns(len(quick_questions))
    for idx, question in enumerate(quick_questions):
        if cols[idx].button(question, key=f"quick_hr_q_{idx}", use_container_width=True):
            st.session_state.hr_question_input = question
            st.session_state.hr_quick_clicked = True
            st.rerun()

    # ── Text area — value always driven from session state ────────────────────
    # Do NOT pass `key=` here so Streamlit doesn't fight with `value=`
    typed = st.text_area(
        "Or ask a custom question:",
        value=st.session_state.hr_question_input,
        placeholder="e.g., Is this candidate suitable for a data science role?",
        height=120,
    )

    # If user typed manually, sync back to session state
    if typed != st.session_state.hr_question_input:
        st.session_state.hr_question_input = typed

    # ── OK button ─────────────────────────────────────────────────────────────
    col_btn, col_clear = st.columns([1, 6])
    ok_clicked = col_btn.button("✅ OK", type="primary", key="hr_ok_btn")
    if col_clear.button("🗑️ Clear", key="hr_clear_btn"):
        st.session_state.hr_question_input = ""
        st.session_state.hr_quick_clicked = False
        if "hr_analysis" in st.session_state:
            del st.session_state["hr_analysis"]
        st.rerun()

    # Use session state value (not typed) so quick-click always works
    final_question = st.session_state.hr_question_input

    return final_question, ok_clicked