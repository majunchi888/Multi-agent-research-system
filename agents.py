from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import httpx

from tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

# llm model setup

# http_client = httpx.Client(
#     verify=False,
#     timeout=httpx.Timeout(60.0),
#     proxy=None,
#     transport=httpx.HTTPTransport(
#         retries=2,
#         limits=httpx.Limits(max_connections=10)
#     )
# )

os.environ["NO_PROXY"] = "dashscope.aliyuncs.com,*.aliyuncs.com"
os.environ["no_proxy"] = "dashscope.aliyuncs.com,*.aliyuncs.com"

llm = ChatOpenAI(model="qwen3.6-flash", 
                 temperature=0,
                 api_key=os.getenv("ALIYUN_API_KEY"), # pyright: ignore[reportArgumentType] # type: ignore
                 base_url=os.getenv("ALIYUN_URL"),
                 ) # type: ignore

# llm = ChatOpenAI(model="deepseek-v4-flash",api_key=os.getenv("DEEPSEEK_API_KEY"),temperature=0.5,base_url=os.getenv("DEEPSEEK_URL"), # type: ignore
#                  extra_body={
#                      "enable_thinking": False,     # ← 关键：关闭思考模式
#                     "thinking_budget": 0        # 也可以这样写
#      }) # type: ignore

# 1st agent
def build_search_agent():
  
  return create_agent(
    model = llm,
    tools = [web_search],
  )

# 2nd agent
def build_reader_agent():
  return create_agent(
    model = llm,
    tools = [scrape_url],
  )

# chain
write_prompt = ChatPromptTemplate.from_messages([
  ("system", "You are a helpful writer. 你可以写正确、简洁、清晰、结构化的报道。"),
  ("human", """用下面的Topic来写一篇详细的报道
   
   Topic:{topic}
   
   内容提供：{research}
   
   报告结构如下：
   - 介绍
   - 关键的发现 （最少三个解释清楚的要点）
   - 结论
   - 来源（列举出所有信息来源的URL）

   请回答的详细，客观，专业"""),
])

writer_chain = write_prompt | llm | StrOutputParser()

# critic_chain
critic_prompt = ChatPromptTemplate.from_messages([
  ("system", "你是一个尖锐且有建设性的批评家。不要被内容的日期和时间与事实束缚，因为都是最新的消息，你还不知道。你的工作是仔细审查报道，找出逻辑漏洞、缺失的信息或偏见。请给出具体的改进建议。"),
  ("human", """请审查以下报道并且评估它的严谨性：

  Report:{report}
   
  用以下确切的格式回答：

  分数： X/10

  优点：
   -...
   -...

  不足：
   -...
   -... 

  一句话总结：
   ...

  """),
])

critic_chain = critic_prompt | llm | StrOutputParser()