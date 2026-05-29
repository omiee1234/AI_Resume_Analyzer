# views/__init__.py  ← rename this file to __init__.py inside views/ folder
from .upload_view import render_upload_section, render_analysis_type_selector, render_hr_chatbot_input
from .analysis_view import render_analysis, render_hr_section

__all__ = [
    "render_upload_section",
    "render_analysis_type_selector",
    "render_hr_chatbot_input",
    "render_analysis",
    "render_hr_section",
]