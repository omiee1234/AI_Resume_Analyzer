"""
views/analysis_view.py
──────────────────────
Clean card-based UI — no raw JSON shown ever.
"""

import streamlit as st

from utils import try_parse_json
from models import create_docx, create_pdf
from controllers import generate_improved_resume


# ── Shared CSS ────────────────────────────────────────────────────────────────

_CARD_CSS = """
<style>
.av-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.av-banner-title { color:#94a3b8; font-size:0.85rem; text-transform:uppercase; letter-spacing:.08em; margin:0; }
.av-banner-score { color:#ffffff; font-size:3.5rem; font-weight:800; margin:4px 0; line-height:1; }
.av-banner-sub   { color:#64748b; font-size:0.9rem; margin:0; }

.av-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 18px;
}
.av-card-title {
    color: #f1f5f9;
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.av-bullet { color:#cbd5e1; margin: 6px 0; padding-left: 0; list-style:none; }
.av-bullet li::before { content:"• "; color:#3b82f6; font-weight:700; }
.av-bullet li { margin-bottom: 7px; line-height:1.5; }
.av-text { color:#cbd5e1; line-height:1.7; margin:0; }

.av-snapshot-row { display:flex; justify-content:space-between; padding: 7px 0; border-bottom:1px solid #1e293b; }
.av-snapshot-row:last-child { border-bottom: none; }
.av-snapshot-label { color:#64748b; font-size:0.85rem; }
.av-snapshot-value { color:#e2e8f0; font-size:0.85rem; font-weight:600; text-align:right; max-width:60%; }

.av-tag {
    display:inline-block;
    background:#1e293b;
    color:#93c5fd;
    padding:3px 10px;
    border-radius:20px;
    font-size:0.8rem;
    margin:3px 3px 3px 0;
}
.av-verdict {
    display:inline-block;
    padding: 6px 18px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 12px;
}
</style>
"""


def _inject_css():
    st.markdown(_CARD_CSS, unsafe_allow_html=True)


# ── Banner ────────────────────────────────────────────────────────────────────

def _render_banner(parsed: dict) -> None:
    score = parsed.get("ats_score") or parsed.get("ats_match_percentage")
    if score is None:
        return
    # pick colour by score
    if score >= 85:
        color = "#22c55e"
    elif score >= 70:
        color = "#3b82f6"
    elif score >= 55:
        color = "#f59e0b"
    else:
        color = "#ef4444"

    st.markdown(
        f"""
        <div class='av-banner'>
            <p class='av-banner-title'>ATS Score</p>
            <div class='av-banner-score' style='color:{color};'>{score}%</div>
            <p class='av-banner-sub'>Detailed ATS insights with strengths, weaknesses, missing skills, and keyword gaps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Quick Snapshot sidebar card ───────────────────────────────────────────────

def _render_snapshot_card(parsed: dict) -> None:
    snap = parsed.get("quick_resume_snapshot") or {}
    score = parsed.get("ats_score") or parsed.get("ats_match_percentage")

    rows = []
    if score is not None:
        rows.append(("ATS Score", f"{score}%"))
    if snap.get("candidate_name"):
        rows.append(("Name", snap["candidate_name"]))
    if snap.get("current_role"):
        rows.append(("Role", snap["current_role"]))
    if snap.get("total_experience"):
        rows.append(("Experience", snap["total_experience"]))
    if snap.get("education"):
        rows.append(("Education", snap["education"]))
    if snap.get("resume_strength"):
        rows.append(("Verdict", snap["resume_strength"]))

    if not rows:
        return

    html = ["<div class='av-card'><p class='av-card-title'>📋 Quick Resume Snapshot</p>"]
    for label, value in rows:
        html.append(
            f"<div class='av-snapshot-row'>"
            f"<span class='av-snapshot-label'>{label}</span>"
            f"<span class='av-snapshot-value'>{value}</span>"
            f"</div>"
        )

    # top tech skills as tags
    skills = snap.get("top_tech_skills", [])
    if skills:
        html.append("<div style='margin-top:12px;'>")
        for s in skills:
            html.append(f"<span class='av-tag'>{s}</span>")
        html.append("</div>")

    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ── Generic list card ─────────────────────────────────────────────────────────

def _list_card(icon: str, title: str, items: list) -> None:
    if not items:
        return
    html = [f"<div class='av-card'><p class='av-card-title'>{icon} {title}</p><ul class='av-bullet'>"]
    for item in items:
        if isinstance(item, dict):
            text = " — ".join(str(v) for v in item.values())
        else:
            text = str(item)
        html.append(f"<li>{text}</li>")
    html.append("</ul></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _text_card(icon: str, title: str, text: str) -> None:
    if not text:
        return
    st.markdown(
        f"<div class='av-card'><p class='av-card-title'>{icon} {title}</p>"
        f"<p class='av-text'>{text}</p></div>",
        unsafe_allow_html=True,
    )


# ── Main analysis cards ───────────────────────────────────────────────────────

def _render_analysis_cards(parsed: dict) -> None:
    _list_card("💪", "Top Strengths",
               parsed.get("top_strengths") or parsed.get("optimized_skills_section") or [])

    _list_card("⚠️", "Weaknesses",
               parsed.get("weaknesses") or parsed.get("resume_weaknesses") or [])

    _list_card("🔧", "Missing Skills",
               parsed.get("missing_skills") or [])

    _list_card("🔑", "Keywords Missing",
               parsed.get("important_ats_keywords_missing") or parsed.get("missing_keywords") or [])

    _list_card("💡", "Improvement Suggestions",
               parsed.get("improvement_suggestions") or parsed.get("important_improvements") or [])

    _text_card("✍️", "Improved Professional Summary",
               parsed.get("improved_professional_summary") or parsed.get("optimized_resume_summary") or "")

    _render_ai_enablement_card(parsed)


# ── AI Enablement card ────────────────────────────────────────────────────────

def _render_ai_enablement_card(parsed: dict) -> None:
    ai = parsed.get("ai_enablement")
    if not ai:
        return

    status = ai.get("ai_enablement_status", "")
    score  = ai.get("ai_enablement_score", 0)
    status_colors = {
        "HIGHLY AI-ENABLED": "#22c55e",
        "AI-ENABLED":        "#3b82f6",
        "MODERATELY AI-ENABLED": "#f59e0b",
        "LIMITED AI-SKILLS": "#f97316",
        "NO AI-EXPERIENCE":  "#ef4444",
    }
    color = status_colors.get(status.upper(), "#94a3b8")

    html = [
        "<div class='av-card'>",
        "<p class='av-card-title'>🤖 AI Enablement</p>",
        f"<span class='av-verdict' style='background:{color}22; color:{color}; border:1px solid {color}55;'>{status} — {score}%</span>",
    ]

    # skills tags
    skills = ai.get("ai_related_skills", [])
    if skills:
        html.append("<p style='color:#64748b; font-size:0.8rem; margin:12px 0 6px;'>AI / ML Skills</p>")
        for s in skills:
            html.append(f"<span class='av-tag'>{s}</span>")

    # tools
    tools = ai.get("ai_tools_and_frameworks", [])
    if tools:
        html.append("<p style='color:#64748b; font-size:0.8rem; margin:12px 0 6px;'>Tools & Frameworks</p>")
        for t in tools:
            html.append(f"<span class='av-tag' style='color:#86efac;'>{t}</span>")

    # projects
    projects = ai.get("ai_related_projects", [])
    if projects:
        html.append("<p style='color:#64748b; font-size:0.8rem; margin:12px 0 6px;'>AI Projects</p>")
        html.append("<ul class='av-bullet'>")
        for p in projects:
            name = p.get("project_name", "Project")
            desc = p.get("description", "")
            outcome = p.get("outcome", "")
            line = f"<strong>{name}</strong> — {desc}"
            if outcome:
                line += f" <em>({outcome})</em>"
            html.append(f"<li>{line}</li>")
        html.append("</ul>")

    exp = ai.get("ai_experience_summary", "")
    if exp:
        html.append(f"<p class='av-text' style='margin-top:12px;'>{exp}</p>")

    ready = ai.get("ai_readiness", "")
    if ready:
        html.append(f"<p style='color:#93c5fd; margin-top:10px; font-size:0.9rem;'>🎯 {ready}</p>")

    roles = ai.get("recommended_ai_roles", [])
    if roles:
        html.append("<p style='color:#64748b; font-size:0.8rem; margin:12px 0 6px;'>Recommended Roles</p>")
        for r in roles:
            html.append(f"<span class='av-tag' style='color:#c4b5fd;'>{r}</span>")

    gaps = ai.get("gaps_for_ai_roles", [])
    if gaps:
        html.append("<p style='color:#64748b; font-size:0.8rem; margin:12px 0 6px;'>Skill Gaps</p>")
        html.append("<ul class='av-bullet'>")
        for g in gaps:
            html.append(f"<li>{g}</li>")
        html.append("</ul>")

    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ── Final improved resume renderer ───────────────────────────────────────────

def _render_resume_section(label: str, value) -> None:
    if not value:
        return
    st.markdown(f"### {label}")
    if isinstance(value, str):
        st.markdown(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, list):
                st.markdown(f"**{key.replace('_',' ').title()}:**")
                for entry in item:
                    st.markdown(f"- {entry}")
            else:
                st.markdown(f"**{key.replace('_',' ').title()}:** {item}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                title = item.get("title") or item.get("role") or item.get("name") or item.get("degree")
                if title:
                    st.markdown(f"**{title}**")
                for field, detail in item.items():
                    if field in ("title", "role", "name", "degree"):
                        continue
                    if isinstance(detail, list):
                        for line in detail:
                            st.markdown(f"- {line}")
                    else:
                        st.markdown(f"- **{field.replace('_',' ').title()}:** {detail}")
            else:
                st.markdown(f"- {item}")


def _render_final_resume(improved_text: str) -> None:
    parsed = try_parse_json(improved_text)
    if not parsed:
        st.error("Could not parse the improved resume.")
        st.code(improved_text)
        return

    resume = parsed.get("final_resume") or parsed.get("final_ats_optimized_resume")
    if not resume and all(k in parsed for k in ["name", "title"]):
        resume = parsed
    if not resume:
        st.error("Improved resume JSON does not contain a valid resume object.")
        st.code(improved_text)
        return

    name    = resume.get("name")
    title   = resume.get("title") or resume.get("objective")
    contact = resume.get("contact") or resume.get("contact_info")

    if name:
        st.markdown(f"# {name}")
    if title and title != name:
        st.markdown(f"**{title}**")
    if contact:
        if isinstance(contact, dict):
            parts = [v for v in contact.values() if v and v != "Not provided"]
            st.markdown(" | ".join(parts))
        elif isinstance(contact, list):
            st.markdown(" | ".join(contact))
        else:
            st.markdown(contact)

    _render_resume_section("Objective",        resume.get("objective"))
    _render_resume_section("Education",        resume.get("education"))
    _render_resume_section("Technical Skills", resume.get("technical_skills"))
    _render_resume_section("Tools & Platforms",resume.get("tools_and_platforms"))
    _render_resume_section("Projects",         resume.get("projects"))
    _render_resume_section("Experience",       resume.get("experience"))
    _render_resume_section("Certifications",   resume.get("certifications"))
    _render_resume_section("Achievements",     resume.get("achievements"))


# ── Apply Changes + Download ──────────────────────────────────────────────────

def _render_apply_changes(resume_text: str, analysis_text: str) -> None:
    if st.button("⚡ Apply Changes & Generate Resume"):
        with st.spinner("Generating ATS Optimized Resume…"):
            st.session_state.improved_resume = generate_improved_resume(
                resume_text, analysis_text
            )

    if "improved_resume" not in st.session_state:
        return

    st.subheader("🔥 Final ATS Optimized Resume")
    _render_final_resume(st.session_state.improved_resume)

    export_format = st.selectbox("Choose download format", ["DOCX", "PDF"], key="export_format")
    improved = st.session_state.improved_resume

    if export_format == "DOCX":
        st.download_button(
            label="⬇ Download Improved Resume (.docx)",
            data=create_docx(improved),
            file_name="ATS_Optimized_Resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        st.download_button(
            label="⬇ Download Improved Resume (.pdf)",
            data=create_pdf(improved),
            file_name="ATS_Optimized_Resume.pdf",
            mime="application/pdf",
        )


# ── PUBLIC: General Analysis ──────────────────────────────────────────────────

def render_analysis(analysis_text: str, resume_text: str) -> None:
    _inject_css()
    st.subheader("📊 Resume Analysis")

    parsed = try_parse_json(analysis_text)

    if not parsed:
        st.error("Unable to parse the resume analysis. Please try again.")
        return   # NO raw JSON shown

    _render_banner(parsed)

    col_left, col_right = st.columns([2, 1], gap="large")
    with col_left:
        _render_analysis_cards(parsed)
    with col_right:
        _render_snapshot_card(parsed)

    st.markdown("---")
    _render_apply_changes(resume_text, analysis_text)


# ── PUBLIC: HR Section ────────────────────────────────────────────────────────

def render_hr_section(hr_analysis_text: str) -> None:
    _inject_css()
    st.markdown("---")

    parsed = try_parse_json(hr_analysis_text)

    if not parsed:
        st.error("Could not parse HR response. Please try again.")
        return   # NO raw JSON shown

    hr_answer    = parsed.get("hr_answer", {})
    hr_suitability = parsed.get("hr_suitability", {})

    # ── Verdict badge ─────────────────────────────────────────────────────────
    verdict = hr_answer.get("suitability_verdict", "")
    verdict_colors = {
        "HIGHLY SUITABLE":    ("#22c55e", "#14532d"),
        "SUITABLE":           ("#3b82f6", "#1e3a5f"),
        "MODERATELY SUITABLE":("#f59e0b", "#451a03"),
        "NOT SUITABLE":       ("#ef4444", "#450a0a"),
    }
    if verdict:
        fg, bg = verdict_colors.get(verdict.upper(), ("#94a3b8", "#1e293b"))
        st.markdown(
            f"<div style='background:{bg}; border:1px solid {fg}44; border-radius:12px; "
            f"padding:16px 24px; margin-bottom:20px;'>"
            f"<span style='color:{fg}; font-size:1.3rem; font-weight:800;'>⚖️ {verdict}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Question & Answer ─────────────────────────────────────────────────────
    question = hr_answer.get("question", "")
    answer   = hr_answer.get("answer", "")
    if question:
        st.markdown(f"**❓ Question:** _{question}_")
    if answer:
        st.info(answer)

    # ── Key Points & Concerns ────────────────────────────────────────────────
    key_pts  = hr_answer.get("key_points", [])
    concerns = hr_answer.get("concerns", [])
    col1, col2 = st.columns(2)
    with col1:
        _list_card("✅", "Key Hiring Points", key_pts)
    with col2:
        _list_card("⚠️", "Concerns", concerns)

    # ── Recommendation ────────────────────────────────────────────────────────
    rec = hr_answer.get("recommendation", "")
    if rec:
        st.success(f"📋 **Recommendation:** {rec}")

    # ── Candidate Profile ─────────────────────────────────────────────────────
    fit_sum   = hr_suitability.get("candidate_fit_summary", "")
    hire_pts  = hr_suitability.get("key_hiring_points", [])
    hire_cons = hr_suitability.get("hiring_concerns", [])

    if fit_sum:
        _text_card("🧠", "Candidate Profile (HR View)", fit_sum)

    col3, col4 = st.columns(2)
    with col3:
        _list_card("💼", "Hiring Strengths", hire_pts)
    with col4:
        _list_card("🔍", "Due Diligence", hire_cons)

    # ── AI Enablement ─────────────────────────────────────────────────────────
    _render_ai_enablement_card(parsed)