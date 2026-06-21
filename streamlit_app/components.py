from pathlib import Path
import html as html_lib
from typing import Mapping, Sequence

import pandas as pd
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
    title = html_lib.escape(str(title))
    text = html_lib.escape(str(text))
    render_html(
        f'<div class="rf-card">'
        f'<div class="rf-card-title">{title}</div>'
        f'<div class="rf-card-text">{text}</div>'
        f'</div>'
    )


def proof_card(title: str, proof: str):
    title = html_lib.escape(str(title))
    proof = html_lib.escape(str(proof))
    render_html(
        f'<div class="rf-card">'
        f'<div class="rf-card-title">✅ {title}</div>'
        f'<div class="rf-card-text">{proof}</div>'
        f'</div>'
    )


def block_badges(blocks: Sequence[str]):
    """Display discreet academic block badges at the top of a page."""
    badges = "".join(
        f'<span class="rf-badge">{html_lib.escape(str(block))}</span>'
        for block in blocks
    )

    render_html(
        '<div style="margin: 0.5rem 0 1.2rem 0;">'
        '<span style="font-size: 0.85rem; opacity: 0.75; margin-right: 0.5rem;">Blocs :</span>'
        f'{badges}'
        '</div>'
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


def technical_evidence(evidence: Mapping[str, Sequence[str]], expanded: bool = False):
    """Render a standardized technical evidence expander."""
    with st.expander("Technical evidence", expanded=expanded):
        for title, items in evidence.items():
            st.markdown(f"**{title}**")
            for item in items:
                st.markdown(f"- {item}")


def academic_mapping(rows: Sequence[Mapping[str, str]], expanded: bool = False):
    """Render a standardized academic block mapping expander."""
    with st.expander("Academic block mapping", expanded=expanded):
        if rows:
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No academic mapping provided for this page.")


def tool_links(links: Sequence[Mapping[str, str]]):
    """Render a compact row of external tool links."""
    if not links:
        return

    cols = st.columns(len(links))

    for col, link in zip(cols, links):
        with col:
            st.link_button(
                link.get("label", "Open"),
                link.get("url", "#"),
                use_container_width=True,
            )


def footer_note():
    render_html(
        '<div class="rf-footer-note">'
        'RetailFlow Platform • Hugo Braun - Master 2 Data for Finance • '
        'End-to-end Retail Intelligence Platform'
        '</div>'
    )
