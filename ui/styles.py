import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --ifin-ink: #172033;
            --ifin-muted: #667085;
            --ifin-line: #e6eaf0;
            --ifin-panel: #f7f9fc;
            --ifin-blue: #1f6feb;
            --ifin-green: #15917a;
            --ifin-soft-blue: #eef5ff;
            --ifin-soft-green: #edf8f5;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        h1, h2, h3 {
            color: var(--ifin-ink);
            letter-spacing: 0;
        }

        .ifin-hero-v2 {
            padding: 3rem 0 1.1rem;
            border-bottom: 1px solid var(--ifin-line);
            margin-bottom: 1.2rem;
        }

        .ifin-hero-v2 h1 {
            font-size: 2.2rem;
            line-height: 1.2;
            margin: 0 0 0.55rem;
        }

        .ifin-hero-subtitle {
            color: var(--ifin-ink);
            font-size: 1.08rem;
            margin-bottom: 0.35rem;
        }

        .ifin-hero-note {
            color: var(--ifin-muted);
            font-size: 0.95rem;
        }

        .ifin-section-title {
            font-size: 1.08rem;
            font-weight: 760;
            color: var(--ifin-ink);
            margin: 1.2rem 0 0.75rem;
        }

        .ifin-card, .ifin-note, .ifin-kv, .ifin-work-card, .ifin-list-row, .ifin-stat-card {
            background: #ffffff;
            border: 1px solid var(--ifin-line);
            border-radius: 8px;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
        }

        .ifin-card, .ifin-note, .ifin-kv {
            padding: 1rem;
        }

        .ifin-work-card {
            min-height: 220px;
            padding: 1.25rem;
        }

        .ifin-work-card-blue {
            background: linear-gradient(180deg, #ffffff 0%, var(--ifin-soft-blue) 100%);
            border-color: #d5e6ff;
        }

        .ifin-work-card-green {
            background: linear-gradient(180deg, #ffffff 0%, var(--ifin-soft-green) 100%);
            border-color: #cfeee4;
        }

        .ifin-work-title {
            color: var(--ifin-ink);
            font-size: 1.18rem;
            font-weight: 780;
            margin-bottom: 0.65rem;
        }

        .ifin-work-body {
            color: var(--ifin-muted);
            line-height: 1.65;
            min-height: 82px;
        }

        .ifin-list-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.65rem;
        }

        .ifin-row-title {
            color: var(--ifin-ink);
            font-weight: 650;
        }

        .ifin-row-meta {
            color: var(--ifin-muted);
            font-size: 0.82rem;
            margin-top: 0.18rem;
        }

        .ifin-mini-badge {
            display: inline-block;
            color: #24525f;
            background: #edf7f8;
            border: 1px solid #cfe9ec;
            border-radius: 999px;
            padding: 0.18rem 0.5rem;
            margin-right: 0.35rem;
            margin-bottom: 0.25rem;
            font-size: 0.76rem;
            font-weight: 650;
        }

        .ifin-blue-badge {
            color: #174ea6;
            background: var(--ifin-soft-blue);
            border-color: #d5e6ff;
        }

        .ifin-green-badge {
            color: #116b5c;
            background: var(--ifin-soft-green);
            border-color: #cfeee4;
        }

        .ifin-tag-row {
            margin-top: 0.75rem;
        }

        .ifin-watch-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }

        .ifin-watch-tag {
            color: var(--ifin-ink);
            background: #f8fafc;
            border: 1px solid var(--ifin-line);
            border-radius: 999px;
            padding: 0.42rem 0.72rem;
            font-size: 0.88rem;
            font-weight: 650;
        }

        .ifin-stat-card {
            padding: 1rem;
            min-height: 108px;
        }

        .ifin-stat-label {
            color: var(--ifin-muted);
            font-size: 0.82rem;
            margin-bottom: 0.42rem;
        }

        .ifin-stat-value {
            color: var(--ifin-ink);
            font-weight: 800;
            font-size: 1.35rem;
            line-height: 1.25;
        }

        .ifin-event-input {
            background: linear-gradient(180deg, #ffffff 0%, var(--ifin-soft-blue) 100%);
            border: 1px solid #d5e6ff;
            border-radius: 8px;
            padding: 1.15rem;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
            margin-bottom: 1rem;
        }

        .ifin-status-card, .ifin-number-card, .ifin-history-card, .ifin-risk-card, .ifin-view-card {
            background: #ffffff;
            border: 1px solid var(--ifin-line);
            border-radius: 8px;
            padding: 1rem;
            min-height: 142px;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
        }

        .ifin-status-state, .ifin-number-value {
            color: var(--ifin-blue);
            font-weight: 800;
            font-size: 1.18rem;
            margin: 0.35rem 0;
        }

        .ifin-position-track {
            position: relative;
            height: 8px;
            border-radius: 999px;
            background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 48%, #1f6feb 100%);
            margin: 0.65rem 0 0.35rem;
        }

        .ifin-position-dot {
            position: absolute;
            top: 50%;
            width: 14px;
            height: 14px;
            border-radius: 999px;
            background: #172033;
            border: 2px solid #ffffff;
            transform: translate(-50%, -50%);
            box-shadow: 0 2px 8px rgba(23, 32, 51, 0.18);
        }

        .ifin-position-labels {
            display: flex;
            justify-content: space-between;
            color: var(--ifin-muted);
            font-size: 0.76rem;
            margin-bottom: 0.55rem;
        }

        .ifin-trend {
            display: inline-block;
            color: #174ea6;
            background: var(--ifin-soft-blue);
            border: 1px solid #d5e6ff;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .ifin-impact-chain {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.65rem;
            align-items: stretch;
            margin-bottom: 0.75rem;
        }

        .ifin-impact-step {
            background: var(--ifin-soft-blue);
            border: 1px solid #d5e6ff;
            border-radius: 8px;
            padding: 1rem;
            min-height: 118px;
            color: var(--ifin-ink);
            font-weight: 720;
            display: flex;
            align-items: center;
        }

        .ifin-impact-arrow {
            color: var(--ifin-blue);
            font-weight: 900;
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }

        .ifin-reasoning-wrap {
            position: relative;
            border-left: 2px solid #d5e6ff;
            margin: 0.5rem 0 1rem 0.85rem;
            padding-left: 1.25rem;
        }

        .ifin-reasoning-card {
            position: relative;
            background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
            border: 1px solid #d5e6ff;
            border-radius: 8px;
            padding: 1rem 1rem 1rem 1.15rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 10px 24px rgba(31, 111, 235, 0.06);
        }

        .ifin-reasoning-card::before {
            content: "";
            position: absolute;
            left: -1.78rem;
            top: 1.05rem;
            width: 0.86rem;
            height: 0.86rem;
            border-radius: 999px;
            background: var(--ifin-blue);
            border: 3px solid #ffffff;
            box-shadow: 0 0 0 2px #d5e6ff;
        }

        .ifin-step-badge {
            display: inline-block;
            color: #174ea6;
            background: var(--ifin-soft-blue);
            border: 1px solid #d5e6ff;
            border-radius: 999px;
            padding: 0.16rem 0.55rem;
            font-size: 0.76rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .ifin-reasoning-title {
            color: var(--ifin-ink);
            font-weight: 800;
            margin-bottom: 0.28rem;
        }

        .ifin-reasoning-content {
            color: var(--ifin-blue);
            font-weight: 800;
            font-size: 1.05rem;
            margin-bottom: 0.4rem;
        }

        .ifin-section-subtitle {
            color: var(--ifin-muted);
            font-size: 0.92rem;
            margin: -0.25rem 0 0.8rem;
        }

        .ifin-risk-level {
            display: inline-block;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 760;
            margin-bottom: 0.45rem;
        }

        .ifin-risk-high {
            color: #9f2f16;
            background: #fff1ec;
            border: 1px solid #ffd2c2;
        }

        .ifin-risk-mid {
            color: #8a5200;
            background: #fff8e8;
            border: 1px solid #f5dda3;
        }

        .ifin-view-source {
            color: var(--ifin-muted);
            font-size: 0.82rem;
            margin-top: 0.7rem;
            border-top: 1px solid var(--ifin-line);
            padding-top: 0.55rem;
        }

        .ifin-risk-history {
            margin-top: 0.75rem;
            padding-top: 0.65rem;
            border-top: 1px solid var(--ifin-line);
            color: var(--ifin-muted);
            font-size: 0.86rem;
            line-height: 1.55;
        }

        .ifin-insight-card {
            background: linear-gradient(135deg, #eef5ff 0%, #ffffff 58%, #edf8f5 100%);
            border: 1px solid #cfe0ff;
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 12px 30px rgba(31, 111, 235, 0.09);
            margin: 0.85rem 0 0.4rem;
        }

        .ifin-insight-label {
            color: var(--ifin-blue);
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .ifin-insight-text {
            color: var(--ifin-ink);
            font-size: 1.12rem;
            font-weight: 760;
            line-height: 1.6;
        }

        .ifin-user-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
            border: 1px solid #d5e6ff;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
            margin-bottom: 1rem;
        }

        .ifin-user-main {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .ifin-avatar {
            width: 54px;
            height: 54px;
            border-radius: 999px;
            background: linear-gradient(135deg, #1f6feb 0%, #15917a 100%);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.05rem;
        }

        .ifin-user-name {
            color: var(--ifin-ink);
            font-size: 1.05rem;
            font-weight: 800;
        }

        .ifin-user-handle, .ifin-user-desc {
            color: var(--ifin-muted);
            font-size: 0.84rem;
        }

        .ifin-user-meta {
            display: grid;
            grid-template-columns: repeat(3, minmax(82px, 1fr));
            gap: 0.65rem;
        }

        .ifin-user-meta-item {
            background: rgba(255,255,255,0.74);
            border: 1px solid var(--ifin-line);
            border-radius: 8px;
            padding: 0.65rem;
        }

        .ifin-note-card {
            background: #ffffff;
            border: 1px solid var(--ifin-line);
            border-radius: 8px;
            padding: 0.9rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
        }

        .ifin-note-date {
            color: var(--ifin-blue);
            font-weight: 800;
            font-size: 0.82rem;
            margin-bottom: 0.32rem;
        }

        .ifin-note-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
        }

        .ifin-coming-soon {
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            padding: 1rem;
            color: var(--ifin-muted);
        }

        .ifin-report-input {
            background: linear-gradient(180deg, #ffffff 0%, var(--ifin-soft-green) 100%);
            border: 1px solid #cfeee4;
            border-radius: 8px;
            padding: 1.15rem;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
            margin-bottom: 1rem;
        }

        .ifin-report-card {
            background: #ffffff;
            border: 1px solid var(--ifin-line);
            border-radius: 8px;
            padding: 1rem;
            min-height: 150px;
            box-shadow: 0 8px 22px rgba(23, 32, 51, 0.05);
        }

        .ifin-change-direction {
            display: inline-block;
            color: #116b5c;
            background: var(--ifin-soft-green);
            border: 1px solid #cfeee4;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 760;
            margin-bottom: 0.45rem;
        }

        .ifin-fulfillment {
            display: inline-block;
            color: #174ea6;
            background: var(--ifin-soft-blue);
            border: 1px solid #d5e6ff;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 760;
            margin-bottom: 0.45rem;
        }

        .ifin-card {
            min-height: 140px;
        }

        .ifin-card-title {
            color: var(--ifin-ink);
            font-weight: 700;
            margin-bottom: 0.4rem;
        }

        .ifin-card-meta {
            color: var(--ifin-muted);
            font-size: 0.8rem;
            margin-bottom: 0.48rem;
        }

        .ifin-card-body {
            color: var(--ifin-muted);
            line-height: 1.55;
            font-size: 0.94rem;
        }

        .ifin-source-view {
            border-left: 3px solid var(--ifin-blue);
            background: var(--ifin-panel);
            padding: 0.82rem 0.95rem;
            margin-bottom: 0.75rem;
            border-radius: 0 8px 8px 0;
            color: var(--ifin-ink);
        }

        .ifin-source {
            color: var(--ifin-muted);
            font-size: 0.82rem;
            margin-top: 0.45rem;
        }

        .ifin-callout {
            background: #f4fbf8;
            border: 1px solid #cfeee4;
            border-radius: 8px;
            padding: 1rem;
            color: #15584d;
            margin-bottom: 0.75rem;
        }

        .ifin-kv-label {
            color: var(--ifin-muted);
            font-size: 0.78rem;
            margin-bottom: 0.35rem;
        }

        .ifin-kv-value {
            color: var(--ifin-ink);
            font-weight: 700;
            font-size: 0.95rem;
        }

        .ifin-note {
            margin-bottom: 0.75rem;
        }

        section[data-testid="stSidebar"] {
            background: #f6f8fb;
        }

        div[data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
