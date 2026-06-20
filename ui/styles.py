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

        .ifin-market-card {
            background: #ffffff;
            border: 1px solid #e6eaf2;
            border-radius: 14px;
            padding: 16px;
            min-height: 172px;
            box-shadow: 0 8px 18px rgba(23, 32, 51, 0.04);
            margin-bottom: 0.85rem;
        }

        .ifin-market-card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin-bottom: 0.35rem;
        }

        .ifin-market-card-title {
            color: var(--ifin-ink);
            font-size: 0.94rem;
            font-weight: 760;
            line-height: 1.35;
        }

        .ifin-market-card-value {
            color: #3b6ff5;
            font-size: 21px;
            line-height: 1.18;
            font-weight: 700;
            margin: 0.24rem 0 0.34rem;
        }

        .ifin-market-card-badge,
        .ifin-market-card-trend {
            display: inline-block;
            color: #174ea6;
            background: #eef5ff;
            border: 1px solid #d5e6ff;
            border-radius: 999px;
            padding: 0.13rem 0.46rem;
            font-size: 0.72rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .ifin-market-card-body {
            color: var(--ifin-muted);
            font-size: 0.84rem;
            line-height: 1.48;
            margin: 0.34rem 0 0.42rem;
        }

        .ifin-market-card-meta-wrap {
            margin-top: 0.42rem;
        }

        .ifin-market-card-meta {
            color: #6b7280;
            font-size: 12.5px;
            line-height: 1.56;
        }

        .ifin-market-track {
            position: relative;
            height: 8px;
            border-radius: 999px;
            background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 48%, #3b6ff5 100%);
            margin: 0.46rem 0 0.22rem;
        }

        .ifin-market-dot {
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

        .ifin-market-track-labels {
            display: flex;
            justify-content: space-between;
            color: #6b7280;
            font-size: 0.76rem;
            margin-bottom: 0.32rem;
        }

        .ifin-key-empty-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            min-height: 118px;
            box-shadow: 0 8px 18px rgba(23, 32, 51, 0.03);
            margin-bottom: 0.85rem;
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

        .ifin-prototype-search-label,
        .ifin-prototype-label {
            color: #667085;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.42rem;
        }

        div[data-testid="stTextInput"]:has(input[aria-label="Search"]) {
            position: sticky;
            top: 3.1rem;
            z-index: 30;
            padding: 0.35rem 0;
            background: rgba(255, 255, 255, 0.96);
        }

        .ifin-prototype-topic-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1.5rem;
            padding: 1rem 0 0.9rem;
            margin: 0.45rem 0 1rem;
            border-bottom: 1px solid #e6eaf0;
        }

        .ifin-prototype-topic {
            color: #172033;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.45rem;
        }

        .ifin-prototype-understanding {
            color: #667085;
            font-size: 0.86rem;
            line-height: 1.48;
            max-width: 720px;
        }

        .ifin-prototype-freshness {
            color: #667085;
            font-size: 0.78rem;
            white-space: nowrap;
            padding-top: 0.35rem;
        }

        .st-key-event_deck_desktop {
            position: relative;
            overflow: visible;
            min-height: 410px;
            margin-top: 3.8rem;
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"] {
            position: absolute;
            top: 66px;
            width: 152px;
            transition: transform 160ms ease, filter 160ms ease, opacity 160ms ease, z-index 0ms;
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"] button {
            position: relative;
            overflow: hidden;
            width: 100%;
            min-height: 272px;
            align-items: flex-start;
            justify-content: flex-start;
            padding: 1rem 0.62rem;
            color: #445066;
            background-color: var(--sheet-tint, #f4f6f9);
            background-image:
                linear-gradient(rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                linear-gradient(90deg, rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                linear-gradient(150deg, rgba(255,255,255,0.72), rgba(226,232,241,0.38));
            background-size: 16px 16px, 16px 16px, 100% 100%;
            border: 1px solid #cfd7e3;
            border-radius: 5px;
            box-shadow:
                inset 0 0 0 3px rgba(255,255,255,0.72),
                inset 0 0 0 4px rgba(117, 136, 167, 0.18),
                0 12px 25px rgba(23, 32, 51, 0.11);
            font-size: 0.73rem;
            font-weight: 650;
            text-align: left;
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"] button p {
            position: relative;
            z-index: 3;
            writing-mode: vertical-rl;
            text-orientation: upright;
            letter-spacing: 0.1em;
            line-height: 1.1;
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"] button::before {
            content: "";
            position: absolute;
            left: 25%;
            right: 9%;
            top: 28%;
            height: 34%;
            background: rgba(75, 94, 126, 0.22);
            clip-path: polygon(0 78%, 16% 58%, 33% 66%, 51% 38%, 68% 51%, 84% 27%, 100% 38%, 100% 41%, 84% 30%, 68% 54%, 51% 42%, 33% 70%, 16% 62%, 0 82%);
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"] button::after {
            content: "iFin";
            position: absolute;
            left: 50%;
            bottom: 0.9rem;
            transform: translateX(-50%);
            color: rgba(49, 62, 84, 0.58);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.03em;
        }

        .st-key-event_deck_material_views {
            left: 0;
            transform: rotate(-4deg);
            z-index: 1;
            --sheet-tint: #f3f6fa;
        }

        .st-key-event_deck_material_history {
            left: 19px;
            transform: rotate(-2.4deg);
            z-index: 2;
            --sheet-tint: #f6f5f1;
        }

        .st-key-event_deck_material_variables {
            left: 38px;
            transform: rotate(-1deg);
            z-index: 3;
            --sheet-tint: #f1f6f5;
        }

        .st-key-event_deck_material_risk {
            left: 57px;
            transform: rotate(0.8deg);
            z-index: 4;
            --sheet-tint: #f7f3f3;
        }

        .st-key-event_deck_material_transmission {
            left: 76px;
            transform: rotate(2.2deg);
            z-index: 5;
            --sheet-tint: #f3f4f8;
        }

        .st-key-event_deck_material_watch {
            left: 95px;
            transform: rotate(3.6deg);
            z-index: 6;
            --sheet-tint: #f4f7f2;
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"]:hover {
            transform: translateY(-24px) rotate(0deg);
            z-index: 20;
            filter: saturate(1.04);
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"]:hover button {
            border-color: #aab7cb;
            box-shadow:
                inset 0 0 0 3px rgba(255,255,255,0.76),
                inset 0 0 0 4px rgba(92, 116, 156, 0.22),
                0 18px 34px rgba(23, 32, 51, 0.16);
        }

        .st-key-event_deck_desktop [class*="st-key-event_deck_material_"]:has(.ifin-deck-selected-marker) {
            opacity: 0.34;
            transform: translateY(-18px) rotate(0deg);
            filter: grayscale(0.35);
        }

        .ifin-deck-selected-marker {
            position: absolute;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }

        .st-key-event_mobile_evidence {
            display: none;
        }

        .ifin-research-card {
            background: #ffffff;
            border: 1px solid #dfe4ec;
            border-radius: 10px;
            padding: 1.2rem 1.3rem;
            min-height: 360px;
            box-shadow: 0 14px 34px rgba(23, 32, 51, 0.07);
        }

        .ifin-research-card-enter {
            transform-origin: left bottom;
            backface-visibility: hidden;
            animation: ifin-pull-and-flip 520ms cubic-bezier(0.22, 0.78, 0.24, 1) both;
        }

        @keyframes ifin-pull-and-flip {
            0% {
                opacity: 0.2;
                transform: translate(-46%, 24%) scale(0.72) rotate(-7deg) rotateY(-82deg);
            }
            58% {
                opacity: 1;
                transform: translate(-8%, 1%) scale(0.96) rotate(-1deg) rotateY(8deg);
            }
            100% {
                opacity: 1;
                transform: translate(0, 0) scale(1) rotate(0deg) rotateY(0deg);
            }
        }

        .ifin-research-title {
            color: #172033;
            font-size: 1.35rem;
            font-weight: 800;
            margin: 0.4rem 0 0.75rem;
        }

        .ifin-research-core {
            color: #172033;
            font-size: 1.02rem;
            font-weight: 650;
            line-height: 1.55;
            padding-bottom: 0.9rem;
            border-bottom: 1px solid #eef1f5;
        }

        .ifin-research-contrast {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 0.9rem;
        }

        .ifin-research-contrast > div {
            background: #f7f9fc;
            border: 1px solid #e6eaf0;
            border-radius: 8px;
            padding: 0.75rem;
            color: #667085;
            font-size: 0.84rem;
            line-height: 1.48;
        }

        .ifin-research-source {
            color: #7b8496;
            font-size: 0.76rem;
            line-height: 1.45;
            margin-top: 0.9rem;
        }

        .ifin-market-snapshot {
            background: #f7f9fc;
            border: 1px solid #e1e6ee;
            border-radius: 10px;
            padding: 1rem;
            min-height: 280px;
        }

        .ifin-snapshot-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.65rem;
            margin-top: 0.65rem;
        }

        .ifin-snapshot-grid > div {
            background: #ffffff;
            border: 1px solid #e7ebf1;
            border-radius: 7px;
            padding: 0.65rem;
        }

        .ifin-snapshot-grid span,
        .ifin-snapshot-grid strong {
            display: block;
        }

        .ifin-snapshot-grid span {
            color: #7b8496;
            font-size: 0.7rem;
            margin-bottom: 0.22rem;
        }

        .ifin-snapshot-grid strong {
            color: #172033;
            font-size: 0.9rem;
            overflow-wrap: anywhere;
        }

        .ifin-snapshot-compact {
            min-height: 360px;
            padding: 0.85rem;
        }

        .ifin-snapshot-compact .ifin-snapshot-grid {
            grid-template-columns: 1fr;
            gap: 0.45rem;
        }

        .ifin-prototype-empty-focus {
            color: #7b8496;
            border: 1px dashed #cfd6e1;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            font-size: 0.84rem;
        }

        .ifin-full-analysis-anchor {
            border-top: 1px solid #e6eaf0;
            margin: 1.1rem 0 0.3rem;
        }

        @media (max-width: 768px) {
            .st-key-event_deck_desktop {
                display: none;
            }

            .st-key-event_mobile_evidence {
                display: block;
                position: sticky;
                top: 6.9rem;
                z-index: 24;
                overflow-x: auto;
                padding: 0.25rem 0;
                background: rgba(255, 255, 255, 0.97);
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] {
                display: flex;
                flex-wrap: nowrap;
                min-width: max-content;
                gap: 0;
                padding: 0.7rem 0.4rem 0.9rem;
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label {
                position: relative;
                overflow: hidden;
                align-items: flex-start;
                min-width: 116px;
                min-height: 174px;
                margin-left: -68px;
                padding: 0.75rem 0.55rem;
                color: #445066;
                background-color: #f4f6f9;
                background-image:
                    linear-gradient(rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                    linear-gradient(150deg, rgba(255,255,255,0.74), rgba(226,232,241,0.4));
                background-size: 14px 14px, 14px 14px, 100% 100%;
                border: 1px solid #cfd7e3;
                border-radius: 5px;
                box-shadow:
                    inset 0 0 0 3px rgba(255,255,255,0.7),
                    inset 0 0 0 4px rgba(117, 136, 167, 0.17),
                    0 9px 20px rgba(23, 32, 51, 0.1);
                transform: rotate(-2.5deg);
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label:first-child {
                margin-left: 0;
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label:nth-child(even) {
                transform: rotate(2deg);
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label:has(input:checked) {
                z-index: 10;
                transform: translateY(-12px) rotate(0deg);
                border-color: #9eb1d3;
                box-shadow: 0 10px 22px rgba(23, 32, 51, 0.13);
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label > div:first-child {
                display: none;
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label p {
                position: relative;
                z-index: 2;
                writing-mode: vertical-rl;
                text-orientation: upright;
                letter-spacing: 0.08em;
                font-size: 0.7rem;
                font-weight: 650;
            }

            .st-key-event_mobile_evidence div[role="radiogroup"] label::after {
                content: "iFin";
                position: absolute;
                left: 50%;
                bottom: 0.72rem;
                transform: translateX(-50%);
                color: rgba(49, 62, 84, 0.58);
                font-size: 0.64rem;
                font-weight: 760;
            }

            .ifin-prototype-topic-header {
                display: block;
            }

            .ifin-prototype-freshness {
                margin-top: 0.5rem;
            }

            .ifin-research-card,
            .ifin-market-snapshot,
            .ifin-snapshot-compact {
                min-height: auto;
            }

            .ifin-research-contrast,
            .ifin-snapshot-grid,
            .ifin-snapshot-compact .ifin-snapshot-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .ifin-research-card-enter {
                animation: none;
            }
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
