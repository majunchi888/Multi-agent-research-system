from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain 

def run_research_pipeline(topic: str) -> dict: # type: ignore
  state = {}

  #search agent working
  print("\n"+"="*40+"Step 1: SEARCH AGENT WORKING"+"="*40+"\n")

  search_agent = build_search_agent()
  search_result = search_agent.invoke({
      "messages": [("user", f"运用工具：web_search，搜索最近关于{topic}的最新报道，返回web_search结果中的Title\nURL\nSnippet\n['content'][:300]，除了url，其他都返回中文。")]
    }) # type: ignore
  state["search_results"] = search_result["messages"][-1].content # type: ignore

  print("\nsearch results: ", state["search_results"])

  # step 2 - reader agent
  print("\n"+"="*40+"Step 2: READER AGENT is srcrapping..."+"="*40+"\n")
  
  reader_agent = build_reader_agent()
  read_result = reader_agent.invoke({
    "messages": [("user", f"从下面这些关于{topic}的搜索结果中，进行梳理和整理。"
                          f"选取最相关的URL，抓取和返回干净详细的文本内容。\n\n"
                          f"这些搜索结果是：{state['search_results'][:800]}"
                  )]
  }) # type: ignore
  
  state["scraped_content"] = read_result["messages"][-1].content

  print("\nscraped content:\n", state["scraped_content"])

  # step 3 - writer chain
  print("\n"+"="*40+"Step 3: Writer is drafting the report..."+"="*40+"\n")

  research_combined = (
     f"SEARCH RESULTS:\n{state['search_results']}\n\n"
     f"SCRAPPED CONTENT:\n{state['scraped_content']}"
   )
  
  state["report"] = writer_chain.invoke({
    "topic": topic,
    "research": research_combined
  })

  print("\n"+"="*40+"Final Report"+"="*40+"\n")
  print(state["report"])

  # step 4 - critic chain
  print("\n"+"="*40+"Step 4: Critic is evaluating the report..."+"="*40+"\n")
  
  state["feedback"] =  critic_chain.invoke({
    "report": state["report"]
  })

  print("\n"+"="*40+"Critic's Feedback on Report"+"="*40+"\n")
  print(state["feedback"])  

  return state

# if __name__ == "__main__":
#   topic = input("\n请输入你想要搜寻的主题：")
#   run_research_pipeline(topic)


  