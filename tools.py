from langchain.tools import tool
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# import requests
import os
from tavily import TavilyClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich import print

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str, days: int = 180) -> str:
  """搜索最近期的网站来获取最近并且可靠的信息关于指定主题。返回Titles, URLs, Snippets。
     days参数控制搜索最近多少天内的新闻，默认180天。"""
  end_date = datetime.now().strftime("%Y-%m-%d")
  start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
  results = tavily.search(
      query=query, max_results=5, topic="news",
      start_date=start_date, end_date=end_date,
  )

  out = []

  for r in results["results"]:
    out.append(f"Title: {r["title"]}\nURL: {r["url"]}\nSnippet: {r["content"][:300]}\n")

  return "\n------\n".join(out)

# @tool
# def scrape_url(url: str) -> str:
#   """从给定的URL中进行更详细的阅读并且抓取和返回干净的文本内容"""
#   try:
#     resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})  #伪装成浏览器 模拟 Chrome 浏览器
#     soup = BeautifulSoup(resp.text, "html.parser")                          # BeautifulSoup(内容, 解析方式) 把str解析为 html 
#     for tag in soup(["script", "style", "nav", "footer"]): 
#       tag.decompose()
#     return soup.get_text(separator=" ", strip=True)[:1000]
#   except Exception as e:
#     return f"Could not scrape {url}: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """从给定的URL中抓取干净详细的文本内容（支持动态页面）"""
    try:
        with sync_playwright() as p:
            # 添加更多启动参数，提高成功率
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            )
            
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # 等待页面主要内容加载
            page.wait_for_timeout(3000)
            
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        
        # 移除不需要的标签
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]   # 适当增加返回长度

    except Exception as e:
        return f"Could not scrape {url}: {str(e)}"
