"""Reusable Streamlit sections for the iFin MVP."""

import streamlit as st


def render_badge(label):
    st.markdown(f"<span class='ifin-badge'>{label}</span>", unsafe_allow_html=True)


def render_card(title, body, tags=None, meta=None):
    tags = tags or []
    meta_html = f"<div class='ifin-card-meta'>{meta}</div>" if meta else ""
    tag_html = "".join(f"<span class='ifin-mini-badge'>{tag}</span>" for tag in tags)
    st.markdown(
        f"""
        <div class="ifin-card">
            <div class="ifin-card-title">{title}</div>
            {meta_html}
            <div class="ifin-card-body">{body}</div>
            <div class="ifin-tag-row">{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(items):
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        with column:
            st.metric(item["label"], item["value"], item.get("trend"))


def render_source_view(view, source, tag=None):
    tag_html = f"<span class='ifin-mini-badge'>{tag}</span>" if tag else ""
    st.markdown(
        f"""
        <div class="ifin-source-view">
            <div>{view}</div>
            <div class="ifin-source">Source: {source}</div>
            <div class="ifin-tag-row">{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)


def render_bullets(items):
    for item in items:
        st.markdown(f"- {item}")


def render_key_value_grid(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items.items()):
        with column:
            st.markdown(
                f"""
                <div class="ifin-kv">
                    <div class="ifin-kv-label">{label}</div>
                    <div class="ifin-kv-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_note(note):
    st.markdown(
        f"""
        <div class="ifin-note">
            <div class="ifin-card-title">{note["target"]}</div>
            <div class="ifin-card-meta">{note["source_page"]} · {note["created_at"]}</div>
            <div class="ifin-tag-row"><span class="ifin-mini-badge">{note["attitude"]}</span></div>
            <div class="ifin-card-body">{note["content"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
