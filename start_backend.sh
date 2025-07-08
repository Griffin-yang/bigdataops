#!/bin/bash

echo "启动 BigDataOps 后端..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "检查并安装Python依赖..."
pip install -r requirements.txt

# 启动后端服务
echo "启动后端API服务..."
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 