#!/bin/bash

# 环境检查
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please install Docker first."
    exit
fi

# 创建必要的目录
mkdir -p logs

# 启动服务
echo "Starting AI Gateway services..."
docker-compose -f deploy/docker-compose.yml up -d

echo "Services started successfully!"
echo "AI Gateway: http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Metrics: http://localhost:8000/metrics"
