from pathlib import Path
import html as html_lib

import streamlit as st


CSS_PATH = Path(__file__).parent / "styles" / "custom.css"


def load_css():
    if CSS_PATH.exists():
        st.markdown(
            f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_html(content: str):
    st.markdown(content, unsafe_allow_html=True)


def hero():
    render_html(
        '<div class="rf-hero">'
        '<div class="rf-logo"><span class="rf-logo-icon"></span>RetailFlow</div>'
        '<h1>From customer events to business intelligence</h1>'
        '<p>RetailFlow is an end-to-end retail intelligence platform combining '
        'real-time data pipelines, customer analytics, machine learning and '
        'observability to support business decision-making.</p>'
        '<div class="rf-badge-row">'
        '<span class="rf-badge">Real-Time Pipelines</span>'
        '<span class="rf-badge">Customer Intelligence</span>'
        '<span class="rf-badge">Machine Learning</span>'
        '<span class="rf-badge">Data Governance</span>'
        '<span class="rf-badge">Data Quality</span>'
        '<span class="rf-badge">Observability</span>'
        '</div>'
        '</div>'
    )


def section_title(title: str):
    title = html_lib.escape(title)
    render_html(f'<div class="rf-section-title">{title}</div>')


def info_card(title: str, text: str):
    title = html_lib.escape(title)
    text = html_lib.escape(text)
    render_html(
        f'<div class="rf-card">'
        f'<div class="rf-card-title">{title}</div>'
        f'<div class="rf-card-text">{text}</div>'
        f'</div>'
    )


def architecture_overview():
    render_html(
        '<div class="rf-architecture">'
        '<div class="rf-node">Customer Events</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">Redpanda</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">Consumer</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">PostgreSQL</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">ML Models</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">FastAPI</div><div class="rf-arrow">→</div>'
        '<div class="rf-node">Streamlit</div>'
        '</div>'
    )


def footer_note():
    render_html(
        '<div class="rf-footer-note">'
        'RetailFlow Platform • Hugo Braun - Master 2 Data for Finance • '
        'End-to-end Retail Intelligence Platform'
        '</div>'
    )
