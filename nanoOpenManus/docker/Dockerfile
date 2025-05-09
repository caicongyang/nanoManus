FROM python:3.9-slim

# 创建非root用户
RUN groupadd -r manus && useradd -r -g manus -m -s /bin/bash manus

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install python-dotenv

# 创建固定的工作目录，只有这个目录可以被写入
RUN mkdir -p /app/workspace && \
    chown manus:manus /app/workspace

# 复制应用代码 (在docker-compose中会挂载，这里只是为了Dockerfile的完整性)
COPY .. /app

# 切换到非root用户
USER manus

# 设置环境变量
ENV PYTHONPATH=/app
ENV MAX_STEPS=15
ENV DEBUG=true

# 定义限制可写目录的环境变量
ENV ALLOWED_WRITE_DIR=/app/workspace

# 运行入口脚本
ENTRYPOINT ["/app/docker/entrypoint.sh"] 