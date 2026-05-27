FROM python:3.13-slim

# 设置容器内的工作目录为 /app，后面所有的命令都在这个目录下执行。
WORKDIR /app   

#把宿主机当前目录的所有文件复制到容器内的 /app 目录。
COPY . /app

# 绕过代理设置
ENV NO_PROXY="dashscope.aliyuncs.com,*.aliyuncs.com,localhost,127.0.0.1"
ENV no_proxy="dashscope.aliyuncs.com,*.aliyuncs.com,localhost,127.0.0.1"
ENV PYTHONUNBUFFERED=1

# 赋予 start.sh 执行权限
RUN chmod +x start.sh

# 更新 apt 软件源，并安装系统依赖,curl：后面 HEALTHCHECK 要用到;最后清理缓存，减少镜像体积;国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*


#     安装 Python 依赖包
# --no-cache-dir：不缓存 pip 安装包，进一步减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright
RUN pip install playwright

# 安装浏览器
RUN playwright install --with-deps chromium


EXPOSE 8000
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health


# 容器启动时 默认执行 bash start.sh 这个命令。
# 通常这个脚本会同时启动 FastAPI 和 Streamlit 两个服务（比如用 supervisord 或 concurrently）。
CMD ["bash", "start.sh"]