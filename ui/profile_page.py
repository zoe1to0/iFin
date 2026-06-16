import streamlit as st

from modules.ui_sections import render_bullets
from ui.components import (
    PROFILE_DEMO_INSIGHTS,
    PROFILE_TOPIC_TAGS,
    render_event_section_title,
    render_header,
)


def get_profile_insights():
    if st.session_state.saved_insights:
        return list(reversed(st.session_state.saved_insights))
    return PROFILE_DEMO_INSIGHTS


def render_user_card(insight_count):
    st.markdown(
        f"""
        <div class="ifin-user-card">
            <div class="ifin-user-main">
                <div class="ifin-avatar">ZQ</div>
                <div>
                    <div class="ifin-user-name">zw Q</div>
                    <div class="ifin-user-handle">@ziwenqin960</div>
                    <div class="ifin-user-desc">AI Financial Insight Explorer</div>
                </div>
            </div>
            <div class="ifin-user-meta">
                <div class="ifin-user-meta-item">
                    <div class="ifin-stat-label">加入时间</div>
                    <div class="ifin-kv-value">2026.06</div>
                </div>
                <div class="ifin-user-meta-item">
                    <div class="ifin-stat-label">已记录</div>
                    <div class="ifin-kv-value">{insight_count}</div>
                </div>
                <div class="ifin-user-meta-item">
                    <div class="ifin-stat-label">最近活动</div>
                    <div class="ifin-kv-value">今天</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile_overview(insights):
    render_event_section_title("记录概览")
    cols = st.columns(3)
    overview = [
        {"label": "浏览历史", "value": "14", "note": "用户查看过的事件数量"},
        {"label": "已记录内容", "value": str(len(insights)), "note": "用户保存过的笔记数量"},
        {"label": "最关注主题", "value": "流动性", "note": "用户最常记录或关注的主题"},
    ]
    for column, item in zip(cols, overview):
        with column:
            st.markdown(
                f"""
                <div class="ifin-stat-card">
                    <div class="ifin-stat-label">{item["label"]}</div>
                    <div class="ifin-stat-value">{item["value"]}</div>
                    <div class="ifin-card-body">{item["note"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_profile_note_detail(item):
    st.markdown("**事件摘要**")
    st.write(item.get("event_summary") or "暂无完整事件摘要。")
    st.markdown("**支持逻辑**")
    render_bullets(item.get("support_logic") or ["暂无支持逻辑记录。"])
    st.markdown("**担忧逻辑**")
    render_bullets(item.get("concern_logic") or ["暂无担忧逻辑记录。"])
    st.markdown("**风险雷达**")
    render_bullets(item.get("risk_radar") or ["暂无风险雷达记录。"])
    st.markdown("**iFin Insight / 认知锚点**")
    st.write(item.get("ifin_insight") or "暂无认知锚点。")
    st.markdown("**完整笔记内容**")
    st.write(item.get("note") or "暂无笔记内容。")


def render_profile_notes(insights):
    render_event_section_title("我的笔记")
    st.caption("按时间顺序记录你的市场观察与思考")
    editing_key = st.session_state.setdefault("editing_profile_note", None)
    pending_delete = st.session_state.setdefault("pending_delete_note", None)

    for index, item in enumerate(insights):
        created_at = item.get("created_at") or item.get("date", "")
        updated_at = item.get("updated_at") or "未修改"
        note_summary = item.get("note") or "暂无笔记内容。"
        if len(note_summary) > 86:
            note_summary = note_summary[:86] + "..."

        st.markdown(
            f"""
            <div class="ifin-note-card">
                <div class="ifin-note-date">{item.get("date", "")}</div>
                <div class="ifin-card-title">{item.get("event", "未命名事件")}</div>
                <div class="ifin-card-body">{note_summary}</div>
                <div class="ifin-card-meta">创建于：{created_at} · 最后修改：{updated_at}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_col, edit_col, delete_col = st.columns([5, 1, 1])
        with edit_col:
            if st.button("编辑", key=f"profile-edit-{index}"):
                st.session_state.editing_profile_note = index
                st.rerun()
        with delete_col:
            if st.button("删除", key=f"profile-delete-{index}"):
                st.session_state.pending_delete_note = index
                st.rerun()

        if pending_delete == index:
            st.warning("确认删除这条笔记吗？")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                if st.button("确认删除", key=f"profile-confirm-delete-{index}"):
                    if st.session_state.saved_insights:
                        original_index = len(st.session_state.saved_insights) - 1 - index
                        st.session_state.saved_insights.pop(original_index)
                    st.session_state.pending_delete_note = None
                    st.rerun()
            with cancel_col:
                if st.button("取消", key=f"profile-cancel-delete-{index}"):
                    st.session_state.pending_delete_note = None
                    st.rerun()

        if editing_key == index:
            edited_note = st.text_area(
                "编辑笔记",
                value=item.get("note", ""),
                key=f"profile-edit-note-{index}",
                height=180,
            )
            save_col, cancel_col = st.columns(2)
            with save_col:
                if st.button("保存修改", key=f"profile-save-edit-{index}"):
                    if st.session_state.saved_insights:
                        original_index = len(st.session_state.saved_insights) - 1 - index
                        st.session_state.saved_insights[original_index]["note"] = edited_note
                        st.session_state.saved_insights[original_index]["updated_at"] = datetime.now().strftime("%Y.%m.%d")
                    st.session_state.editing_profile_note = None
                    st.rerun()
            with cancel_col:
                if st.button("取消编辑", key=f"profile-cancel-edit-{index}"):
                    st.session_state.editing_profile_note = None
                    st.rerun()

        with st.expander("展开记录"):
            render_profile_note_detail(item)


def render_profile_topics(insights):
    render_event_section_title("关注主题")
    tags = []
    for item in insights:
        tags.extend(item.get("focus_tags") or [])
    tags = tags or PROFILE_TOPIC_TAGS
    unique_tags = list(dict.fromkeys(tags))
    tags_html = "".join(f'<span class="ifin-watch-tag">{tag}</span>' for tag in unique_tags)
    st.markdown(f'<div class="ifin-watch-tags">{tags_html}</div>', unsafe_allow_html=True)


def render_profile_trends():
    render_event_section_title("长期关注趋势")
    st.markdown(
        """
        <div class="ifin-coming-soon">
            <div class="ifin-card-title">Coming Soon</div>
            <div class="ifin-card-body">未来将展示：关注主题变化、长期观察方向、历史记录趋势、判断回顾。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile():
    render_header("Profile", "这里是你的个人记录空间，用来回顾市场观察与思考。")
    insights = get_profile_insights()
    render_user_card(len(insights))
    render_profile_overview(insights)
    render_profile_notes(insights)
    render_profile_topics(insights)
    render_profile_trends()
