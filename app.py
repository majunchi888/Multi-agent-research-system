import streamlit as st
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from tools import web_search

st.set_page_config(page_title="Multi-Agent Research System", layout="wide")
st.title("Multi-Agent Research System")
st.markdown("输入一个主题，系统将自动搜索、抓取、撰写报告并进行评审。")

topic = st.text_input("研究主题", placeholder="例如：最新人工智能发展趋势...")

if st.button("开始研究", type="primary", disabled=not topic):
    state = {}

    # --- Step 1: Search ---
    with st.status("Step 1: 正在搜索...", expanded=True) as status1:
        try:
            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"运用工具：web_search，搜索最近关于{topic}的最新报道，返回web_search结果中的Title\nURL\nSnippet\n['content'][:300]，除了url，其他都返回中文。")]
              }) # type: ignore # type: ignore
            state["search_results"] = search_result["messages"][-1].content
            st.subheader("搜索结果")
            st.markdown(state["search_results"])
            status1.update(label="Step 1: 搜索完成", state="complete", expanded=False)
        except Exception as e:
            status1.update(label=f"Step 1: 搜索失败 - {e}", state="error")
            st.stop()

    # --- Step 2: Reader Agent ---
    with st.status("Step 2: 阅读代理正在抓取网页内容...", expanded=True) as status2:
        try:
            reader_agent = build_reader_agent()
            read_result = reader_agent.invoke({
                "messages": [("user", f"从下面这些关于{topic}的搜索结果中，进行梳理和整理。"
                                      f"选取最相关的URL，抓取和返回干净详细的文本内容。\n\n"
                                      f"这些搜索结果是：{state['search_results'][:800]}"
                             )]
            }) # type: ignore
            state["scraped_content"] = read_result["messages"][-1].content
            st.subheader("抓取内容")
            st.markdown(state["scraped_content"])
            status2.update(label="Step 2: 网页抓取完成", state="complete", expanded=False)
        except Exception as e:
            status2.update(label=f"Step 2: 抓取失败 - {e}", state="error")
            st.stop()

    # --- Step 3: Writer Chain ---
    with st.status("Step 3: 撰写代理正在起草报告...", expanded=True) as status3:
        try:
            research_combined = (
                f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"SCRAPPED CONTENT:\n{state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({
                "topic": topic,
                "research": research_combined
            })
            st.subheader("最终报告")
            st.markdown(state["report"])
            status3.update(label="Step 3: 报告撰写完成", state="complete", expanded=False)
        except Exception as e:
            status3.update(label=f"Step 3: 撰写失败 - {e}", state="error")
            st.stop()

    # --- Step 4: Critic Chain ---
    with st.status("Step 4: 评审代理正在评估报告...", expanded=True) as status4:
        try:
            state["feedback"] = critic_chain.invoke({
                "report": state["report"]
            })
            st.subheader("评审反馈")
            feedback = state["feedback"]
            for line in feedback.split("\n"):
                if ("分数" in line or "/10" in line) and not line.strip().startswith("-"):
                    try:
                        score_str = line.strip().split("：")[-1].split("/")[0].strip()
                        score = int(score_str)
                        st.progress(score / 10, text=line.strip())
                    except ValueError:
                        st.markdown(line)
                else:
                    st.markdown(line)
            status4.update(label="Step 4: 评审完成", state="complete", expanded=False)
        except Exception as e:
            status4.update(label=f"Step 4: 评审失败 - {e}", state="error")
            st.stop()

    st.success(f"对 **{topic}** 的研究已全部完成！")
    st.balloons()
