# NanoOpenManus Docker 沙箱环境

这个目录包含将NanoOpenManus工具放入Docker沙箱环境的所有必要文件。沙箱环境提供了更安全的执行环境，特别是对于Python代码执行和文件操作功能。

## 安全特性

- **容器隔离**: 使用Docker提供基本的系统隔离
- **非root用户**: 容器内以非特权用户运行
- **文件系统安全**: 
  - 限制写入操作只能在特定目录
  - 防止路径遍历攻击
  - 文件大小限制
- **Python执行安全**:
  - 禁止危险模块和操作
  - 资源限制(CPU, 内存)
  - 执行超时
  - 安全的执行环境

## 目录结构

- `Dockerfile`: 定义Docker镜像
- `docker-compose.yml`: 简化容器管理
- `entrypoint.sh`: 容器启动脚本
- `workspace/`: 容器内唯一可写入的目录，会被挂载到主机
- `home/`: 用户主目录，只读挂载

## 使用方法

### 构建和启动容器

1. 确保已安装Docker和docker-compose

2. 设置OpenAI API密钥:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. 构建和启动容器:
   ```bash
   cd nanoOpenManus/docker
   docker-compose up -d
   ```

### 与容器交互

1. 通过命令行交互:
   ```bash
   docker exec -it nanomanus-sandbox /bin/bash
   ```

2. 查看日志:
   ```bash
   docker logs nanomanus-sandbox
   ```

3. 直接使用:
   ```bash
   docker exec -it nanomanus-sandbox python start.py
   ```

### 工作目录访问

容器的`/app/workspace`目录被挂载到主机的`nanoOpenManus/docker/workspace`目录。你可以通过这个目录与容器共享文件:

1. 放置文件到`nanoOpenManus/docker/workspace`，它们会在容器内的`/app/workspace`中可用
2. 容器内生成的所有文件都会保存在这个共享目录中

## 问题排查

1. 容器无法启动
   - 检查Docker日志: `docker logs nanomanus-sandbox`
   - 确认API密钥是否正确设置

2. 工具执行错误
   - 查看容器日志了解详细错误信息
   - 检查`workspace`目录的权限是否正确

## 安全注意事项

尽管此沙箱提供了多层安全措施，但Docker容器并不是完全隔离的安全环境。在处理不受信任的代码时仍需谨慎。

- 不要在生产环境中使用此沙箱处理高风险代码
- 定期更新Docker和基础镜像
- 考虑附加安全措施如SELinux或AppArmor配置 