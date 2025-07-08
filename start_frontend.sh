#!/bin/bash

echo "启动 BigDataOps 前端..."

# 检查是否在正确的目录
if [ ! -d "frontend/bigdata-frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 进入前端目录
cd frontend/bigdata-frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动开发服务器
echo "启动前端开发服务器..."
echo "前端地址: http://localhost:5173"
echo "默认登录账号: admin / admin"
echo ""

npm run dev 