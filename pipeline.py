from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain 
import json

def run_research_pipeline_stream(topic: str) : # type: ignore
  state = {}

  #search agent working
  yield f"data: {json.dumps({
    'type': 'status',
    'content': '🔍 Search Agent working...'
  }, ensure_ascii=False)}\n\n"

  search_agent = build_search_agent()
  search_result = search_agent.invoke({
      "messages": [("user", f"运用工具：web_search，搜索最近关于{topic}的最新报道，返回web_search结果中的Title\nURL\nSnippet\n['content'][:300]，除了url，其他都返回中文。")]
    }) # type: ignore
  state["search_results"] = search_result["messages"][-1].content # type: ignore

  yield f"data: {json.dumps({
    'type': 'search',
    'content': state['search_results']
  }, ensure_ascii=False)}\n\n"

  # step 2 - reader agent
  yield f"data: {json.dumps({
    'type': 'status',
    'content': '📖 Reader Agent working...'
  }, ensure_ascii=False)}\n\n"
  
  reader_agent = build_reader_agent()
  read_result = reader_agent.invoke({
    "messages": [("user", f"从下面这些关于{topic}的搜索结果中，进行梳理和整理。"
                          f"选取最相关的URL，抓取和返回干净详细的文本内容。\n\n"
                          f"这些搜索结果是：{state['search_results'][:800]}"
                  )]
  }) # type: ignore
  
  state["scraped_content"] = read_result["messages"][-1].content

  yield f"data: {json.dumps({
    'type': 'reader',
    'content': state['scraped_content']
  }, ensure_ascii=False)}\n\n"

  # step 3 - writer chain
  yield f"data: {json.dumps({
    'type': 'status',
    'content': '✍ Writer working...'
  },ensure_ascii=False)}\n\n"

  research_combined = (
     f"SEARCH RESULTS:\n{state['search_results']}\n\n"
     f"SCRAPPED CONTENT:\n{state['scraped_content']}"
   )
  
  state["report"] = writer_chain.invoke({
    "topic": topic,
    "research": research_combined
  })

  yield f"data: {json.dumps({
    'type': 'report',
    'content': state['report']
  }, ensure_ascii=False)}\n\n"

  # step 4 - critic chain
  yield f"data: {json.dumps({
    'type': 'status',
    'content': '🧠 Critic working...'
  }, ensure_ascii=False)}\n\n"
  
  state["feedback"] =  critic_chain.invoke({
    "report": state["report"]
  })

  yield f"data: {json.dumps({
    'type': 'feedback',
    'content': state['feedback']
  }, ensure_ascii=False)}\n\n"

  yield "data: [DONE]\n\n"

# if __name__ == "__main__":
#   topic = input("\n请输入你想要搜寻的主题：")
#   run_research_pipeline(topic)


  