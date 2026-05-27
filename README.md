# 演示图片

<details>
<summary>查看完整系统截图</summary>

<img src="images/Multi-Agent research System.png"/>

</details>
## 创作流程

### 第 1 步 — 环境搭建

创建一个虚拟环境(uv venv)，安装需要的库从requirements.txt中，创建.env文件存入llm的api key和base url 和工具Tavily API key.

### 第 2 步 — 创建 tools.py

我们将使用 @tool 装饰器构建 2 个自定义工具：
web_search 工具：与 Tavily API 交互，从互联网获取实时搜索结果。
scrape_url 工具：接收一个 URL，访问该网页并使用 BeautifulSoup 从中提取干净易读的文本内容。

### 第 3 步 — 创建 agents.py

这是整个项目的核心部分，我们将在这里构建 4 个模块：
搜索代理（Search Agent）：使用 react_agent 构建，将调用 web_search 工具。
阅读代理（Reader Agent）：采用与搜索代理相同的模式构建，但将调用 scrape_url 工具。
写作链（Writer Chain）：使用现代的 LCEL（LangChain 表达式语言）管道语法 prompt | llm | StrOutputParser() 构建，接收所有研究内容并生成一份完整报告。
评审链（Critic Chain）：同样使用 LCEL 管道构建，读取生成的报告并给出评分与修改反馈。

### 第 4 步 — 创建 pipeline.py

这个文件是整个流程的总调度中枢（监管器）。
我们会编写一个名为 run_research_pipeline 的函数，按照正确顺序依次调用前面全部 4 个智能代理与处理链，并通过共享状态字典在各个模块之间传递运行结果。
这些代理采用消息格式进行输入与输出：
我们传入格式为 {"messages": [("user", "查询内容")]} 的数据，再从 result["messages"][-1].content 中读取代理返回结果。
每一步流程执行完毕后，程序都会在终端打印输出内容，方便学习者清晰看到每个代理的完整运行过程。

### 第 5 步 — 运行与测试

在终端执行命令 python pipeline.py，输入你想要调研的主题。
随后你就能看到 4 个代理按顺序依次工作：信息检索 → 网页精读 → 报告撰写 → 内容评审
最终终端会直接输出完整调研报告，以及评审环节给出的打分与优化建议。

### 第 6 步 — 创建app.py

增加 FastAPI 作为后端服务，实现前后端分离。相比直接在 Streamlit 中调用 Agent Pipeline，FastAPI 更适合 AI 应用的后续扩展与部署，例如多端调用、Docker 部署、Streaming 输出以及后续增加数据库、用户系统、多 Agent 并发等功能。同时，FastAPI 提供标准 API 接口，前端只需要通过 HTTP 请求即可调用整个 Research Pipeline。
然后运行 uvicorn app:app --reload
http://127.0.0.1:8000/docs 查看 API 文档。

### 第 7 步 — 创建ui.py

使用 Streamlit 构建 AI Research 前端界面。用户输入研究主题后，Streamlit 会通过 HTTP 请求调用 FastAPI 后端，并实时接收 Streaming 返回的 Agent 执行结果，包括搜索状态、网页内容、最终报告以及 Critic Feedback，实现类似 ChatGPT / Deep Research 的实时交互体验。

### 第 8 步 — Docker 部署

将 FastAPI 后端 + Streamlit 前端打包成一个 Docker 镜像，实现一键部署、环境一致性和生产级运行能力。Docker 部署可以解决本地环境差异、依赖冲突、端口管理等问题，适合将整个 Multi-Agent Research 系统部署到服务器、云平台（阿里云、腾讯云、Railway、Render 等）或内网服务器。

## — 遇到的问题

问题： 1. 很多网站拒绝抓取 1. 页面提示需要启用JavaScript才能运行应用，说明该页面是动态渲染的，当前工具无法解析其内容。
原因：
你现在的 requests + BeautifulSoup 或 Tavily 默认抓取方式
只能拿到「初始 HTML」
方法：
换Playwright（最推荐）自动执行 JS；等页面加载；再获取 HTML；
搜索多个url，选取最相关的可爬取的url

问题2： 搜索到的网站都是2024年的
方法： 给Tavily工具增加搜索时间段的参数；agent提示词修改：对工具搜索到的内容进行翻译，不让其随意加工。

问题3： FastAPI 后端只有在整个 Agent 执行流程全部完成后，才会一次性将全部结果返回给前端，没有实现后端输出一点，前端显示一点
方法：使用 FastAPI 的 StreamingResponse 结合 Server-Sent Events (SSE) 实现流式输出。
修改返回方式：将原来的 return 改为 yield 生成器形式。
使用 StreamingResponse 返回 SSE 数据流。Streamlit接收方式改为requests + iter_content 处理流式数据。
