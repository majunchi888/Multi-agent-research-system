#!/bin/bash

echo "======================================="
echo "🚀 Multi-Agent System 启动脚本"
echo "======================================="

# 关键：设置网络相关环境变量
export NO_PROXY="dashscope.aliyuncs.com,*.aliyuncs.com,localhost,127.0.0.1,0.0.0.0"
export no_proxy="dashscope.aliyuncs.com,*.aliyuncs.com,localhost,127.0.0.1,0.0.0.0"
export PYTHONUNBUFFERED=1

# 启动 FastAPI 服务（后台运行）
echo "📡 正在启动 FastAPI 服务 (端口 8000)..."
uvicorn app:app --host 0.0.0.0 --port 8000 &

# 给 FastAPI 一点启动时间
sleep 5

# 启动 Streamlit 服务（前台运行，容器主进程）
echo "🌊 正在启动 Streamlit 服务 (端口 8501)..."
streamlit run ui.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --theme.base "light" \
    --logger.level "info"

# 如果 Streamlit 崩溃，容器也会退出