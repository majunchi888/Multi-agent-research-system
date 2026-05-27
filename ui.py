import json
import requests
import streamlit as st
from datetime import datetime

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="AI Deep Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM CSS
# =====================================
st.markdown("""
<style>

/* ---- Global ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(160deg, #f8fafc 0%, #eef2ff 40%, #faf5ff 100%);
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #a5b4fc, #c4b5fd);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #818cf8, #a78bfa);
}

/* ---- Main container tune ---- */
.block-container {
    max-width: 1300px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ---- Glass card (header) ---- */
.glass-card {
    background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
    border-radius: 24px;
    padding: 32px 36px;
    border: 1px solid #e8ecf4;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.03),
        0 8px 30px rgba(99,102,241,0.06);
    margin-bottom: 28px;
    transition: box-shadow 0.3s ease;
}
.glass-card:hover {
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 12px 40px rgba(99,102,241,0.10);
}

/* ---- Header title gradient ---- */
.gradient-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}

/* ---- Status cards ---- */
.status-card {
    background: linear-gradient(135deg, #ffffff, #f9fafb);
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 10px;
    font-weight: 500;
    font-size: 15px;
    color: #1e293b;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    animation: slideIn 0.35s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(1.3); }
}

.pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6366f1;
    margin-right: 8px;
    animation: pulse-dot 1.4s ease-in-out infinite;
}

/* ---- Result wrapper cards ---- */
.result-wrapper {
    background: #ffffff;
    border-radius: 18px;
    padding: 26px 28px;
    border: 1px solid #eef1f6;
    box-shadow:
        0 1px 2px rgba(0,0,0,0.02),
        0 6px 20px rgba(99,102,241,0.04);
    margin-bottom: 20px;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.result-wrapper:hover {
    box-shadow:
        0 1px 2px rgba(0,0,0,0.03),
        0 10px 32px rgba(99,102,241,0.08);
    transform: translateY(-1px);
}

/* ---- Section title inside cards ---- */
.result-wrapper h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e1b4b;
    margin-top: 0;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid #eef1f6;
}

/* ---- Input field ---- */
div[data-testid="stTextInput"] input {
    background: #ffffff;
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 14px 18px;
    font-size: 16px;
    color: #1e293b;
    transition: all 0.25s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
div[data-testid="stTextInput"] input:focus {
    border-color: #818cf8;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.10);
    outline: none;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #c4c8d4;
}

/* ---- Button ---- */
.stButton > button {
    width: 100%;
    border-radius: 16px;
    height: 50px;
    border: none;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    color: #fff;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 0.3px;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(99,102,241,0.25);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    box-shadow: 0 6px 28px rgba(99,102,241,0.40);
    transform: translateY(-1px);
    opacity: 1;
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(99,102,241,0.25);
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fafbff 0%, #f5f3ff 100%);
    border-right: 1px solid #e8ecf4;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* ---- Sidebar pipeline steps ---- */
.sidebar-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    margin-bottom: 6px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid #eef1f6;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    transition: all 0.2s ease;
}
.sidebar-step:hover {
    border-color: #c7d2fe;
    background: #eef2ff;
}
.sidebar-step-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}

/* ---- Divider ---- */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    margin: 28px 0;
}

/* ---- Footer ---- */
.footer-text {
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
}
.footer-text a {
    color: #6366f1;
    text-decoration: none;
}
.footer-text a:hover {
    text-decoration: underline;
}

/* ---- Warning / Error polish ---- */
div[data-testid="stNotification"] {
    border-radius: 14px !important;
}

/* ---- Markdown text inside result-wrapper ---- */
.result-wrapper p,
.result-wrapper li {
    color: #374151;
    line-height: 1.7;
}
/* 去掉红色边框 */
  div[data-baseweb="input"] {
       border-radius: 12px;
       border: 1px solid #e5e7eb;
        }
        

</style>
""", unsafe_allow_html=True)


# =====================================
# SIDEBAR
# =====================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:8px;">
        <span style="font-size:2.6rem;">🧠</span>
    </div>
    <h3 style="text-align:center; color:#1e1b4b; margin-top:0;">
        Deep Research
    </h3>
    <p style="text-align:center; color:#6b7280; font-size:13px; margin-bottom:24px;">
        Multi-Agent Pipeline
    </p>
    """, unsafe_allow_html=True)

    st.markdown("**⚡ Pipeline**")

    steps = [
        ("🔍", "Search", "#6366f1", "Web Search Agent"),
        ("📖", "Read", "#8b5cf6", "Content Scraper"),
        ("✍️", "Write", "#a855f7", "Report Writer"),
        ("🧠", "Critique", "#c084fc", "Quality Review"),
    ]
    for icon, name, color, desc in steps:
        st.markdown(f"""
        <div class="sidebar-step">
            <div class="sidebar-step-icon" style="background:{color}15; color:{color};">
                {icon}
            </div>
            <div>
                <strong>{name}</strong>
                <div style="font-size:12px; color:#9ca3af;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**💡 使用说明**")
    st.markdown("""
    <ol style="font-size:13px; color:#6b7280; padding-left:18px; line-height:1.8;">
        <li>输入研究主题</li>
        <li>点击「开始研究」按钮</li>
        <li>等待 AI Agent 依次完成搜索、阅读、写作、评估</li>
        <li>查看最终报告和评审反馈</li>
    </ol>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <p style="font-size:11px; color:#c4c8d4; text-align:center;">
        Powered by LangChain + Tavily<br>
        {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </p>
    """, unsafe_allow_html=True)


# =====================================
# HEADER
# =====================================
st.markdown("""
<div class="glass-card">
    <div class="gradient-title">AI Deep Research Agent</div>
    <p style="color:#6b7280; font-size:16px; margin-top:6px; margin-bottom:0;">
        输入研究主题，系统自动完成 &nbsp;
        <span style="color:#6366f1;font-weight:600;">搜索</span> →
        <span style="color:#8b5cf6;font-weight:600;">阅读</span> →
        <span style="color:#a855f7;font-weight:600;">写作</span> →
        <span style="color:#c084fc;font-weight:600;">评估</span>
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================
# INPUT
# =====================================
col1, col2 = st.columns([5, 1],vertical_alignment="bottom")

with col1:
    topic = st.text_input(
        "🔎 Research Topic",
        placeholder="例如：最新 AI Agent 技术发展趋势..."
    )

with col2:
    # st.write("")
    # st.write("")
    run_button = st.button("🚀 开始研究", use_container_width=True)


# =====================================
# CONTAINERS
# =====================================
status_container = st.container()

search_container = st.container()

reader_container = st.container()

report_container = st.container()

feedback_container = st.container()


# =====================================
# STATUS FUNCTION
# =====================================
def add_status(message: str):
    status_container.markdown(
        f"""
        <div class="status-card">
            <span class="pulse-dot"></span>
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================
# MAIN LOGIC
# =====================================
if run_button:

    if not topic.strip():
        st.warning("请输入研究主题")
        st.stop()

    add_status("⚡ Connecting to FastAPI server...")

    try:

        response = requests.post(
            "http://127.0.0.1:8000/research",
            json={"topic": topic},
            stream=True,
            timeout=600
        )

        if response.status_code != 200:
            st.error(f"Server Error: {response.status_code}")
            st.stop()

        # placeholders
        search_placeholder = search_container.empty()
        reader_placeholder = reader_container.empty()
        report_placeholder = report_container.empty()
        feedback_placeholder = feedback_container.empty()

        # streaming
        for line in response.iter_lines():

            if not line:
                continue

            decoded_line = line.decode("utf-8")

            if not decoded_line.startswith("data: "):
                continue

            content = decoded_line.replace("data: ", "")

            # DONE
            if content == "[DONE]":

                add_status("✅ Research Finished")

                break

            # parse json
            try:
                data = json.loads(content)

            except Exception:
                continue

            msg_type = data.get("type")
            msg_content = data.get("content")
            msg_content = msg_content.replace("\n", "  \n")

            # =====================================
            # STATUS
            # =====================================
            if msg_type == "status":

                add_status(msg_content)

            # =====================================
            # SEARCH RESULTS
            # =====================================
            elif msg_type == "search":

                 with search_placeholder.container():

                     st.markdown("## 🔍 Search Results")

                     st.markdown(msg_content)

                     st.markdown(
                         '</div>',
                         unsafe_allow_html=True
                     )

            # =====================================
            # READER CONTENT
            # =====================================
            elif msg_type == "reader":

                 with reader_placeholder.container():

                     st.markdown("## 📖 Scraped Content")

                     st.markdown(msg_content)

                     st.markdown(
                         '</div>',
                         unsafe_allow_html=True
                     )

            # =====================================
            # REPORT
            # =====================================
            elif msg_type == "report":

                  with report_placeholder.container():

                      st.markdown("## 📄 Final Report")

                      st.markdown(msg_content)

                      st.markdown(
                          '</div>',
                          unsafe_allow_html=True
                      )

            # =====================================
            # FEEDBACK
            # =====================================
            elif msg_type == "feedback":

                with feedback_placeholder.container():

                    st.markdown("## 🧠 Critic Feedback")

                    st.markdown(msg_content)

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

    except requests.exceptions.ConnectionError:

        st.error("❌ 无法连接 FastAPI 服务")

        st.code("uvicorn app:app --reload")

    except Exception as e:

        st.error(f"❌ Error: {str(e)}")


# =====================================
# FOOTER
# =====================================
st.divider()

st.markdown("""
<div class="footer-text">
    Built with
    <span style="color:#ef4444;">&#10084;</span>
    using FastAPI &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; LangChain &nbsp;·&nbsp; Tavily
</div>
""", unsafe_allow_html=True)
