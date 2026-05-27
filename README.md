第 1 步 — 环境搭建 创建一个虚拟环境(uv venv)，安装需要的库从requirements.txt中，创建.env文件存入llm的api key和base url 和工具Tavily API key.

第 2 步 — 创建 tools.py
我们将使用 @tool 装饰器构建 2 个自定义工具：
web_search 工具：与 Tavily API 交互，从互联网获取实时搜索结果。
scrape_url 工具：接收一个 URL，访问该网页并使用 BeautifulSoup 从中提取干净易读的文本内容。

第 3 步 — 创建 agents.py
这是整个项目的核心部分，我们将在这里构建 4 个模块：
搜索代理（Search Agent）：使用 react_agent 构建，将调用 web_search 工具。
阅读代理（Reader Agent）：采用与搜索代理相同的模式构建，但将调用 scrape_url 工具。
写作链（Writer Chain）：使用现代的 LCEL（LangChain 表达式语言）管道语法 prompt | llm | StrOutputParser() 构建，接收所有研究内容并生成一份完整报告。
评审链（Critic Chain）：同样使用 LCEL 管道构建，读取生成的报告并给出评分与修改反馈。

第 4 步 — 创建 pipeline.py
这个文件是整个流程的总调度中枢（监管器）。
我们会编写一个名为 run_research_pipeline 的函数，按照正确顺序依次调用前面全部 4 个智能代理与处理链，并通过共享状态字典在各个模块之间传递运行结果。
这些代理采用消息格式进行输入与输出：
我们传入格式为 {"messages": [("user", "查询内容")]} 的数据，再从 result["messages"][-1].content 中读取代理返回结果。
每一步流程执行完毕后，程序都会在终端打印输出内容，方便学习者清晰看到每个代理的完整运行过程。

第 5 步 — 运行与测试
在终端执行命令 python pipeline.py，输入你想要调研的主题。
随后你就能看到 4 个代理按顺序依次工作：信息检索 → 网页精读 → 报告撰写 → 内容评审
最终终端会直接输出完整调研报告，以及评审环节给出的打分与优化建议。

💡 术语补充（LangChain 项目）
shared state dictionary 共享状态字典：多 Agent 协作的核心，全程保存所有任务数据、搜索结果、原文内容、生成报告、评审反馈，全流程共用一份数据
message-based 消息式 IO：LangChain REACT Agent 标准交互格式，用对话消息数组传递所有上下文
result["messages"][-1].content：取对话历史里最新一条消息的文本内容

问题： 1. 很多网站拒绝抓取 例如：1. **Pantone官网（https://www.pantone.com/hk/tc/fashion-color-trend-report）**：页面提示需要启用JavaScript才能运行应用，说明该页面是动态渲染的，当前工具无法解析其内容。2. **iaseshop.com（https://www.iaseshop.com/en/pages.php?pageid=55）**：页面显示为加载中状态，且内容主要是导航和产品目录，未包含具体的2025春夏流行色趋势报告正文。

原因：
你现在的 requests + BeautifulSoup 或 Tavily 默认抓取方式
只能拿到「初始 HTML」

方法1： 换Playwright（最推荐）自动执行 JS；等页面加载；再获取 HTML；
搜索多个url，选取最相关的可爬取的url

问题2： 搜索到的网站都是2024年的

方法2： 给Tavily工具增加搜索时间段的参数；agent提示词修改：对工具搜索到的内容进行翻译，不让其随意加工。
