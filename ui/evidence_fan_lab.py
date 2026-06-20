from html import escape

import streamlit as st


LAB_MATERIALS = [
    {
        "id": "views",
        "title": "观点矛盾",
        "question": "市场为什么存在分歧？",
        "core": "支持与谨慎解释同时存在，关键是识别双方依赖的不同前提。",
        "source": "Public market commentary",
    },
    {
        "id": "history",
        "title": "历史镜像",
        "question": "如果从历史相似阶段看呢？",
        "core": "历史案例提供比较框架，但相似性不能替代对当前环境的判断。",
        "source": "Historical market context",
    },
    {
        "id": "variables",
        "title": "关键变量",
        "question": "哪些变量真正驱动这次变化？",
        "core": "先识别决定市场解释的核心变量，再观察后续证据是否验证它们。",
        "source": "Market and fundamental data",
    },
    {
        "id": "risk",
        "title": "风险来源",
        "question": "如果从风险角度看呢？",
        "core": "风险不只是负面结果，也包括当前解释赖以成立的条件发生变化。",
        "source": "Risk signals",
    },
    {
        "id": "transmission",
        "title": "影响路径",
        "question": "这件事如何逐层影响市场？",
        "core": "从起点、关键变量到市场反应，关注中间传导是否真的成立。",
        "source": "Transmission analysis",
    },
    {
        "id": "watch",
        "title": "后续观察",
        "question": "接下来什么信息最值得验证？",
        "core": "把注意力放在能够强化或削弱当前解释的新证据上。",
        "source": "Forward watchlist",
    },
]


def inject_lab_styles():
    st.markdown(
        """
        <style>
        .fan-lab-header {
            padding: 2.1rem 0 1rem;
            border-bottom: 1px solid #e5e9f0;
            margin-bottom: 1rem;
        }

        .fan-lab-kicker {
            color: #667085;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .fan-lab-header h1 {
            color: #172033;
            font-size: 1.75rem;
            letter-spacing: 0;
            margin: 0.35rem 0 0.3rem;
        }

        .fan-lab-header p {
            color: #667085;
            margin: 0;
            font-size: 0.9rem;
        }

        .fan-lab-zone-label {
            color: #667085;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .st-key-fan_lab_deck {
            position: relative;
            overflow: visible;
            min-height: 520px;
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] {
            position: absolute;
            width: 168px;
            transform-origin: 50% 100%;
            transition: transform 170ms ease, opacity 170ms ease, filter 170ms ease;
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] button {
            position: relative;
            overflow: hidden;
            width: 100%;
            min-height: 304px;
            align-items: flex-start;
            justify-content: flex-start;
            padding: 1rem 0.68rem;
            color: #445066;
            background-color: var(--lab-sheet, #f4f6f9);
            background-image:
                linear-gradient(rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                linear-gradient(90deg, rgba(74, 91, 121, 0.055) 1px, transparent 1px),
                linear-gradient(150deg, rgba(255,255,255,0.74), rgba(226,232,241,0.42));
            background-size: 16px 16px, 16px 16px, 100% 100%;
            border: 1px solid #cbd4e1;
            border-radius: 5px;
            box-shadow:
                inset 0 0 0 3px rgba(255,255,255,0.72),
                inset 0 0 0 4px rgba(105, 126, 161, 0.2),
                0 16px 34px rgba(23, 32, 51, 0.14);
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] button p {
            position: relative;
            z-index: 3;
            writing-mode: vertical-rl;
            text-orientation: upright;
            letter-spacing: 0.1em;
            line-height: 1.1;
            font-size: 0.74rem;
            font-weight: 650;
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] button::before {
            content: "";
            position: absolute;
            left: 24%;
            right: 9%;
            top: 29%;
            height: 32%;
            background: rgba(75, 94, 126, 0.23);
            clip-path: polygon(0 79%, 16% 58%, 33% 67%, 51% 38%, 68% 51%, 84% 27%, 100% 38%, 100% 41%, 84% 30%, 68% 54%, 51% 42%, 33% 70%, 16% 62%, 0 82%);
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] button::after {
            content: "iFin";
            position: absolute;
            left: 50%;
            bottom: 1rem;
            transform: translateX(-50%);
            color: rgba(49, 62, 84, 0.58);
            font-size: 0.72rem;
            font-weight: 760;
        }

        .st-key-fan_lab_material_views {
            left: 0;
            bottom: 18px;
            transform: rotate(-11deg);
            z-index: 1;
            --lab-sheet: #f3f6fa;
        }

        .st-key-fan_lab_material_history {
            left: 24px;
            bottom: 30px;
            transform: rotate(-7deg);
            z-index: 2;
            --lab-sheet: #f6f5f1;
        }

        .st-key-fan_lab_material_variables {
            left: 48px;
            bottom: 38px;
            transform: rotate(-3deg);
            z-index: 3;
            --lab-sheet: #f1f6f5;
        }

        .st-key-fan_lab_material_risk {
            left: 72px;
            bottom: 38px;
            transform: rotate(2deg);
            z-index: 4;
            --lab-sheet: #f7f3f3;
        }

        .st-key-fan_lab_material_transmission {
            left: 96px;
            bottom: 30px;
            transform: rotate(7deg);
            z-index: 5;
            --lab-sheet: #f3f4f8;
        }

        .st-key-fan_lab_material_watch {
            left: 120px;
            bottom: 18px;
            transform: rotate(11deg);
            z-index: 6;
            --lab-sheet: #f4f7f2;
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"]:hover {
            z-index: 30;
            transform: translateY(-34px) rotate(0deg);
        }

        .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"]:has(.fan-lab-selected) {
            opacity: 0.28;
            filter: grayscale(0.45);
        }

        .fan-lab-selected {
            position: absolute;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }

        .fan-lab-empty,
        .fan-lab-research-card {
            min-height: 470px;
            border: 1px solid #dfe4ec;
            border-radius: 10px;
            background: #ffffff;
        }

        .fan-lab-empty {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #7b8496;
            font-size: 0.9rem;
            border-style: dashed;
        }

        .fan-lab-research-card {
            padding: 1.5rem 1.65rem;
            box-shadow: 0 18px 42px rgba(23, 32, 51, 0.08);
        }

        .fan-lab-card-title {
            color: #172033;
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0.6rem 0 0.45rem;
        }

        .fan-lab-card-question {
            color: #3b6ff5;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
        }

        .fan-lab-card-core {
            color: #344054;
            font-size: 1.02rem;
            line-height: 1.65;
            max-width: 620px;
        }

        .fan-lab-card-source {
            color: #7b8496;
            font-size: 0.78rem;
            margin-top: 1.6rem;
            padding-top: 0.8rem;
            border-top: 1px solid #edf0f4;
        }

        .fan-lab-card-enter {
            transform-origin: left bottom;
            backface-visibility: hidden;
            animation: fan-lab-pull 560ms cubic-bezier(0.22, 0.78, 0.24, 1) both;
        }

        @keyframes fan-lab-pull {
            0% {
                opacity: 0.18;
                transform: translate(-58%, 28%) scale(0.62) rotate(-10deg) rotateY(-84deg);
            }
            58% {
                opacity: 1;
                transform: translate(-9%, 1%) scale(0.96) rotate(-1deg) rotateY(8deg);
            }
            100% {
                opacity: 1;
                transform: translate(0, 0) scale(1) rotate(0deg) rotateY(0deg);
            }
        }

        @media (max-width: 900px) {
            .st-key-fan_lab_deck {
                min-height: 390px;
            }

            .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] {
                width: 138px;
            }

            .st-key-fan_lab_deck [class*="st-key-fan_lab_material_"] button {
                min-height: 240px;
            }

            .fan-lab-empty,
            .fan-lab-research-card {
                min-height: 340px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .fan-lab-card-enter {
                animation: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_fan_lab():
    inject_lab_styles()
    st.session_state.setdefault("fan_lab_selected", "")
    st.session_state.setdefault("fan_lab_animate", False)

    st.markdown(
        """
        <div class="fan-lab-header">
            <div class="fan-lab-kicker">Evidence Fan Lab</div>
            <h1>选择一个研究角度</h1>
            <p>独立交互实验：Fan → Pull → Research Card</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fan_column, card_column = st.columns([1.15, 2.85], gap="large")
    selected_id = st.session_state.fan_lab_selected

    with fan_column:
        st.markdown('<div class="fan-lab-zone-label">Research Material Fan</div>', unsafe_allow_html=True)
        with st.container(key="fan_lab_deck"):
            for material in LAB_MATERIALS:
                with st.container(key=f"fan_lab_material_{material['id']}"):
                    if selected_id == material["id"]:
                        st.markdown('<span class="fan-lab-selected"></span>', unsafe_allow_html=True)
                    if st.button(
                        material["title"],
                        key=f"fan_lab_select_{material['id']}",
                        width="stretch",
                    ):
                        st.session_state.fan_lab_selected = material["id"]
                        st.session_state.fan_lab_animate = True
                        st.rerun()

    with card_column:
        st.markdown('<div class="fan-lab-zone-label">Research Card</div>', unsafe_allow_html=True)
        selected = next(
            (item for item in LAB_MATERIALS if item["id"] == selected_id),
            None,
        )
        if selected is None:
            st.markdown(
                '<div class="fan-lab-empty">从左下扇面调取一份研究材料</div>',
                unsafe_allow_html=True,
            )
        else:
            enter_class = " fan-lab-card-enter" if st.session_state.fan_lab_animate else ""
            st.markdown(
                f"""
                <div class="fan-lab-research-card{enter_class}">
                    <div class="fan-lab-kicker">Research Angle</div>
                    <div class="fan-lab-card-title">{escape(selected['title'], quote=True)}</div>
                    <div class="fan-lab-card-question">{escape(selected['question'], quote=True)}</div>
                    <div class="fan-lab-card-core">{escape(selected['core'], quote=True)}</div>
                    <div class="fan-lab-card-source">Source preview · {escape(selected['source'], quote=True)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.fan_lab_animate = False

