# OpenManus API参考文档

本文档详细说明了OpenManus项目的主要API接口，包括Web API和代理API。

## Web API

OpenManus提供了一组RESTful API，用于创建、管理和监控代理任务。

### 1. 创建任务

创建一个新的代理任务。

**请求**:
```
POST /tasks
Content-Type: application/json

{
  "prompt": "查询今天的天气"
}
```

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 获取任务列表

获取所有任务的列表。

**请求**:
```
GET /tasks
```

**响应**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt": "查询今天的天气",
    "created_at": "2023-01-01T12:00:00Z",
    "status": "completed",
    "steps": [
      {
        "step": 1,
        "result": "正在搜索天气信息...",
        "type": "step"
      },
      {
        "step": 2,
        "result": "今天的天气是晴天，温度25°C",
        "type": "result"
      }
    ]
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "prompt": "编写一个Python脚本",
    "created_at": "2023-01-01T13:00:00Z",
    "status": "running",
    "steps": []
  }
]
```

### 3. 获取特定任务

获取特定任务的详细信息。

**请求**:
```
GET /tasks/{task_id}
```

**响应**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt": "查询今天的天气",
  "created_at": "2023-01-01T12:00:00Z",
  "status": "completed",
  "steps": [
    {
      "step": 1,
      "result": "正在搜索天气信息...",
      "type": "step"
    },
    {
      "step": 2,
      "result": "今天的天气是晴天，温度25°C",
      "type": "result"
    }
  ]
}
```

### 4. 获取任务事件流

使用服务器发送事件(SSE)获取任务的实时更新。

**请求**:
```
GET /tasks/{task_id}/events
```

**响应**:
```
event: status
data: {"type": "status", "status": "running", "steps": []}

event: think
data: {"type": "think", "step": 0, "result": "我需要搜索天气信息"}

event: tool
data: {"type": "tool", "step": 0, "result": "Executing tool: google_search\nInput: {\"query\": \"今天的天气\"}"}

event: act
data: {"type": "act", "step": 0, "result": "Executing action: 搜索天气信息"}

event: result
data: {"type": "result", "step": 1, "result": "今天的天气是晴天，温度25°C"}

event: complete
data: {"type": "complete"}
```

## 代理API

OpenManus提供了一组Python API，用于创建和使用代理。

### 1. 创建Manus代理

```python
from app.agent.manus import Manus

# 创建代理实例
agent = Manus(
    name="Manus",
    description="A versatile agent that can solve various tasks",
    max_steps=30
)
```

### 2. 运行代理

```python
# 异步运行代理
result = await agent.run("查询今天的天气")
print(result)
```

### 3. 自定义代理回调

```python
# 定义回调函数
async def on_think(thought):
    print(f"思考: {thought}")

async def on_tool_execute(tool, input):
    print(f"执行工具: {tool}, 输入: {input}")

async def on_action(action):
    print(f"执行动作: {action}")

# 创建带回调的代理
agent = Manus()
agent.on_think = on_think
agent.on_tool_execute = on_tool_execute
agent.on_action = on_action

# 运行代理
await agent.run("查询今天的天气")
```

### 4. 添加自定义工具

```python
from app.tool.base import BaseTool

# 创建自定义工具
class MyCustomTool(BaseTool):
    name: str = "my_custom_tool"
    description: str = "A custom tool that does something useful"
    parameters: dict = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "First parameter",
            },
            "param2": {
                "type": "integer",
                "description": "Second parameter",
            },
        },
        "required": ["param1"],
    }

    async def execute(self, param1: str, param2: int = 0) -> str:
        # 实现工具逻辑
        return f"Processed {param1} with value {param2}"

# 添加工具到代理
agent = Manus()
agent.available_tools.add_tool(MyCustomTool())

# 运行代理
await agent.run("使用我的自定义工具")
```

### 5. 配置LLM

```python
from app.llm import LLM
from app.config import LLMSettings

# 创建自定义LLM配置
llm_config = LLMSettings(
    model="gpt-4o",
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    max_tokens=4096,
    temperature=0.0
)

# 创建LLM实例
llm = LLM(config_name="custom", llm_config=llm_config)

# 创建使用自定义LLM的代理
agent = Manus()
agent.llm = llm

# 运行代理
await agent.run("使用自定义LLM配置")
```

## 工具API

OpenManus提供了多种内置工具，每个工具都有特定的参数和用途。

### 1. BrowserUseTool

用于与网页浏览器交互的工具。

```python
# 导航到URL
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "navigate", "url": "https://example.com"}
)

# 点击元素
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "click", "index": 5}
)

# 输入文本
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "input_text", "index": 2, "text": "Hello world"}
)

# 获取页面内容
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "get_text"}
)
```

### 2. GoogleSearch

用于执行谷歌搜索的工具。

```python
# 执行搜索
result = await agent.available_tools.execute(
    name="google_search",
    tool_input={"query": "OpenManus AI agent", "num_results": 5}
)
```

### 3. PythonExecute

用于执行Python代码的工具。

```python
# 执行Python代码
result = await agent.available_tools.execute(
    name="python_execute",
    tool_input={"code": "print('Hello, world!')\nfor i in range(5):\n    print(i)"}
)
```

### 4. FileSaver

用于保存文件的工具。

```python
# 保存文件
result = await agent.available_tools.execute(
    name="file_saver",
    tool_input={
        "filename": "example.txt",
        "content": "This is an example file content",
        "overwrite": True
    }
)
```

## 错误处理

所有API都使用标准HTTP状态码表示成功或失败：

- 200: 请求成功
- 400: 请求无效
- 404: 资源不存在
- 500: 服务器错误

对于Web API，错误响应的格式如下：

```json
{
  "message": "错误描述"
}
```

对于Python API，错误通常以异常的形式抛出，应使用try/except块进行处理。 