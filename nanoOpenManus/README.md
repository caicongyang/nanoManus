# NanoOpenManus

NanoOpenManus 是 [OpenManus](https://github.com/mannaandpoem/OpenManus) 项目的简化版本，专为入门者学习和理解 AI 代理系统而设计。它保留了核心功能，但简化了实现，使代码更易于理解和学习。

## 项目概述

NanoOpenManus 是一个基于工具调用的 AI 代理框架，它允许 AI 助手使用各种工具来解决复杂问题。该项目的核心理念是：

1. **代理（Agent）**：负责理解用户请求，规划解决方案，并调用适当的工具
2. **工具（Tool）**：提供特定功能的模块，如执行 Python 代码、保存文件等
3. **工具调用（Tool Call）**：代理决定使用哪个工具及其参数，并处理工具执行结果

## 系统架构

NanoOpenManus 采用了简洁的分层架构：

```
+------------------+
|      用户        |
+--------+---------+
         |
         v
+--------+---------+
|    Manus 代理    |
+--------+---------+
         |
         v
+--------+---------+
|    工具集合      |
+--------+---------+
         |
         v
+--------+---------+
| Python | 文件  | 环境 | 终止 |
| 执行   | 保存  | 检查 | 工具 |
+--------+---------+
```

## 安装指南

### 前提条件

- Python 3.8 或更高版本
- pip 或其他 Python 包管理工具
- 如需使用Docker沙箱模式，需安装Docker和docker-compose

### 安装步骤

1. 克隆仓库（或下载代码）：

```bash
git clone https://github.com/yourusername/nanoOpenManus.git
cd nanoOpenManus
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

**注意**:
- 如果要使用 LLM 集成功能，需要安装 `httpx` 库
- 如果要使用 .env 文件进行配置，需要安装 `python-dotenv` 库
- 如果要使用环境检查工具，需要安装 `psutil` 库

## 配置说明

NanoOpenManus 支持多种配置方式，您可以根据需要选择最方便的方式：

### 1. 使用 .env 文件配置（推荐）

这是最推荐的配置方式，便于管理敏感信息和开发环境配置：

1. 复制模板文件创建配置：

```bash
cp .env.template .env
```

2. 编辑 `.env` 文件，填入您的配置：

```ini
# OpenAI API 密钥
OPENAI_API_KEY=your-api-key-here

# 其他配置（可选）
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1
MAX_STEPS=15
DEBUG=false
```

### 2. 环境变量配置

您也可以直接设置系统环境变量：

```bash
# 必需 - 如果要使用真实的LLM功能
export OPENAI_API_KEY="your-api-key-here"

# 可选 - 自定义设置
export LLM_MODEL="gpt-4o"  # 默认为 gpt-4o
export LLM_BASE_URL="https://api.openai.com/v1"  # 默认为 OpenAI API 地址
export MAX_STEPS="15"  # 默认为 15
export DEBUG="false"  # 默认为 false
```

### 3. 命令行参数配置

运行时通过命令行参数指定：

```bash
python -m nanoOpenManus.main --api-key "your-api-key" --model "gpt-4o" --base-url "https://api.openai.com/v1" --max-steps 15
```

## 使用方法

### 启动 NanoOpenManus

**标准模式**:

```bash
# 使用.env文件或环境变量配置
python -m nanoOpenManus.main

# 或使用命令行参数
python -m nanoOpenManus.main --api-key "your-api-key"
```

**Docker沙箱模式**:

```bash
# 使用Docker沙箱模式启动，工具将在Docker容器内执行
python -m nanoOpenManus.docker_start --api-key "your-api-key"

# 或者使用标准模式也可选择启用Docker沙箱
python -m nanoOpenManus.main --use-docker
```

### 运行模式

NanoOpenManus 有以下几种运行模式：

1. **标准模式**: 工具在本地环境直接执行。
2. **Docker沙箱模式**: 工具在隔离的Docker容器中执行，提供更高的安全性。
3. **LLM 模式**: 使用真实的大语言模型 API，提供智能的代理功能。需要配置 API 密钥。
4. **模拟模式**: 当未配置 API 密钥或 LLM 客户端初始化失败时自动切换到此模式。使用预设的模拟响应进行测试和学习。

### Docker沙箱模式

Docker沙箱模式提供了一个安全的执行环境，尤其适合执行不受信任的代码。在这种模式下：

1. 所有工具调用都转发到Docker容器中执行
2. 文件操作被限制在特定目录内
3. Python执行环境受到资源限制和安全增强
4. 代码在非root用户下运行

详细的Docker沙箱说明请参阅[Docker沙箱文档](./docker/README.md)。

### 使用示例

在启动 NanoOpenManus 后，您可以在终端中输入请求，例如：

```
🙋 请输入您的请求: 请帮我写一个计算斐波那契数列的函数，并保存到 fib.py 文件中
```

NanoOpenManus 将：
1. 分析您的请求
2. 选择合适的工具（在这个例子中可能是 python_execute 和 file_saver）
3. 执行工具并返回结果

验证Docker沙箱是否正常工作：
```
🙋 请输入您的请求: 检查当前执行环境
```

## 内置工具

NanoOpenManus 提供了以下基本工具：

1. **PythonExecute**：执行 Python 代码，用法示例：
   ```
   请执行以下Python代码: print("Hello, world!")
   ```

2. **FileSaver**：保存内容到文件，用法示例：
   ```
   请将以下内容保存到 hello.txt 文件: Hello, NanoOpenManus!
   ```

3. **EnvironmentCheck**：检查执行环境信息，用法示例：
   ```
   检查当前运行环境信息
   ```

4. **Terminate**：完成任务并终止代理执行，通常由代理自动调用。

## 扩展 NanoOpenManus

### 添加新工具

1. 创建新的工具类，继承 `BaseTool`：

```python
from nanoOpenManus.app.tools.base import BaseTool, ToolResult

class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_new_tool",
            description="这是一个自定义工具",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "参数1"},
                },
                "required": ["param1"]
            }
        )
    
    async def execute(self, param1, **kwargs) -> ToolResult:
        # 实现工具逻辑
        return ToolResult(output=f"处理了参数: {param1}")
```

2. 在 Manus 类中注册新工具：

```python
from my_module import MyNewTool

# 创建Manus实例
agent = Manus()

# 添加自定义工具
agent.available_tools.add_tool(MyNewTool())
```

## LLM 集成

NanoOpenManus 默认支持 LLM 集成，需要配置 API 密钥：

1. 通过 .env 文件：在 `.env` 文件中设置 `OPENAI_API_KEY=your-api-key`
2. 通过环境变量：`export OPENAI_API_KEY="your-api-key"`
3. 通过命令行：`python -m nanoOpenManus.main --api-key "your-api-key"`

**支持的 LLM 设置**：
- **模型**：可通过配置文件、环境变量或命令行参数设置
- **API 端点**：可自定义以支持兼容的其他 LLM 提供商
- **超时设置**：LLM 请求默认超时时间为 60 秒

**使用其他 LLM 提供商**：
如果您想使用与 OpenAI API 兼容的其他 LLM 提供商（如 Azure OpenAI），只需修改 `LLM_BASE_URL` 指向对应的 API 端点。

## 项目结构

```
nanoOpenManus/
├── .env.template          # 环境变量模板文件
├── app/                   # 主应用代码
│   ├── agent.py           # 代理类实现
│   ├── config.py          # 配置管理
│   ├── docker_manus.py    # Docker版本的Manus代理
│   ├── llm.py             # LLM 客户端
│   ├── manus.py           # Manus 代理实现
│   └── tools/             # 工具实现
│       ├── base.py        # 基础工具类
│       ├── docker_proxy.py # Docker工具代理
│       ├── environment_check.py # 环境检查工具
│       ├── file_saver.py  # 文件保存工具
│       ├── python_execute.py # Python执行工具
│       ├── terminate.py   # 终止工具
│       └── tool_collection.py # 工具集合
├── docker/                # Docker沙箱相关文件
│   ├── Dockerfile         # 定义Docker镜像
│   ├── docker-compose.yml # Docker容器配置
│   ├── entrypoint.sh      # 容器启动脚本
│   ├── README.md          # Docker沙箱说明
│   ├── workspace/         # 容器内外共享目录
│   └── home/              # 用户主目录
├── docs/                  # 文档
│   └── llm_integration.md # LLM集成文档
├── docker_start.py        # Docker模式启动脚本
├── main.py                # 主入口
├── README.md              # 项目说明
└── requirements.txt       # 依赖清单
```

## 常见问题解答

### Q: 为什么我的请求没有得到智能响应？

A: 可能有以下几个原因：
- 未配置 API 密钥，系统使用的是模拟模式
- API 密钥无效或过期
- 请求格式不正确

### Q: 如何使用其他 LLM 服务提供商？

A: 修改 .env 文件中的 `LLM_BASE_URL` 或命令行参数中的 `--base-url` 到您想要使用的 API 端点，但请确保该 API 与 OpenAI API 兼容。

### Q: 如何查看系统的详细日志？

A: 在 .env 文件中设置 `DEBUG=true` 或设置环境变量 `DEBUG=true` 可以启用详细日志。

### Q: Docker沙箱模式启动失败怎么办？

A: 检查以下几点：
- 确保已安装Docker和docker-compose
- 检查Docker服务是否启动
- 查看Docker日志以获取详细错误信息：`docker logs nanomanus-sandbox`
- 尝试手动构建Docker容器：`cd nanoOpenManus/docker && docker-compose up -d`

### Q: 无法安装依赖怎么办？

A: 尝试逐个安装依赖：
```bash
pip install asyncio
pip install httpx
pip install python-dotenv
pip install psutil
```

### Q: 运行时遇到"模块未找到"错误怎么办？

A: 这可能是因为 Python 模块路径问题，请确保您在正确的目录下运行，或尝试添加项目路径到 PYTHONPATH：
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/parent/directory
```

## 学习资源

- [OpenManus 官方仓库](https://github.com/mannaandpoem/OpenManus)
- [LangChain 文档](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI 函数调用文档](https://platform.openai.com/docs/guides/function-calling)
- [Docker 文档](https://docs.docker.com/)

## 贡献指南

欢迎对 NanoOpenManus 做出贡献！您可以通过以下方式参与：

1. 报告问题或提出建议
2. 提交 Pull Request 修复 bug 或添加新功能
3. 完善文档或添加示例

## 许可证

MIT 