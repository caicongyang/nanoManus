# OpenManus 工具参考文档

本文档详细列出了OpenManus框架中所有可用的工具，包括它们的功能、参数和使用示例。

## 核心工具概览

OpenManus提供了一系列强大的工具，使代理能够执行各种任务，从网页浏览到代码执行。每个工具都设计为解决特定类型的问题，并且可以通过代理的工具调用机制进行访问。

## 1. BrowserUseTool

### 描述
允许代理与网页浏览器交互，执行各种浏览操作，如导航、点击、输入文本、截图等。

### 参数
- **action** (必需): 要执行的浏览器操作，可选值包括:
  - `navigate`: 导航到指定URL
  - `click`: 点击页面上的元素
  - `input_text`: 在元素中输入文本
  - `screenshot`: 捕获页面截图
  - `get_html`: 获取页面HTML内容
  - `get_text`: 获取页面文本内容
  - `read_links`: 获取页面上的所有链接
  - `execute_js`: 执行JavaScript代码
  - `scroll`: 滚动页面
  - `switch_tab`: 切换到特定标签页
  - `new_tab`: 打开新标签页
  - `close_tab`: 关闭当前标签页
  - `refresh`: 刷新当前页面
- **url** (对于navigate和new_tab操作必需): 要导航到的URL
- **index** (对于click和input_text操作必需): 要操作的元素索引
- **text** (对于input_text操作必需): 要输入的文本
- **script** (对于execute_js操作必需): 要执行的JavaScript代码
- **scroll_amount** (对于scroll操作必需): 滚动像素数（正值向下滚动，负值向上滚动）
- **tab_id** (对于switch_tab操作必需): 要切换到的标签页ID

### 使用示例
```python
# 导航到网页
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "navigate", "url": "https://example.com"}
)

# 点击页面上的第5个元素
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "click", "index": 5}
)

# 在搜索框中输入文本
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "input_text", "index": 2, "text": "OpenManus AI"}
)

# 获取页面文本内容
result = await agent.available_tools.execute(
    name="browser_use",
    tool_input={"action": "get_text"}
)
```

## 2. GoogleSearch

### 描述
执行Google搜索并返回相关链接列表，用于获取网络信息和最新数据。

### 参数
- **query** (必需): 要提交给Google的搜索查询
- **num_results** (可选): 要返回的搜索结果数量，默认为10

### 使用示例
```python
# 搜索OpenManus相关信息
result = await agent.available_tools.execute(
    name="google_search",
    tool_input={"query": "OpenManus AI agent framework", "num_results": 5}
)
```

## 3. PythonExecute

### 描述
执行Python代码并返回执行结果，允许代理动态生成和运行代码来解决问题。

### 参数
- **code** (必需): 要执行的Python代码字符串

### 使用示例
```python
# 执行简单的Python代码
result = await agent.available_tools.execute(
    name="python_execute",
    tool_input={
        "code": """
import math
for i in range(5):
    print(f"Square root of {i} is {math.sqrt(i)}")
"""
    }
)
```

## 4. FileSaver

### 描述
将内容保存到文件中，用于生成报告、保存数据或创建脚本文件。

### 参数
- **filename** (必需): 要保存的文件名
- **content** (必需): 要写入文件的内容
- **overwrite** (可选): 如果文件已存在，是否覆盖，默认为False

### 使用示例
```python
# 保存文本到文件
result = await agent.available_tools.execute(
    name="file_saver",
    tool_input={
        "filename": "report.txt",
        "content": "这是一份由OpenManus生成的报告。\n包含了重要的分析结果。",
        "overwrite": True
    }
)
```

## 5. Bash

### 描述
执行Bash命令并返回执行结果，允许代理与操作系统交互，执行系统命令。

### 参数
- **command** (必需): 要执行的Bash命令字符串
  - 可以为空，用于查看上一个命令的额外日志（当上一个命令的退出码为-1时）
  - 可以是`ctrl+c`，用于中断当前正在运行的进程

### 使用示例
```python
# 列出当前目录内容
result = await agent.available_tools.execute(
    name="bash",
    tool_input={"command": "ls -la"}
)

# 查找文件
result = await agent.available_tools.execute(
    name="bash",
    tool_input={"command": "find . -name '*.py' | grep 'tool'"}
)

# 中断当前运行的进程
result = await agent.available_tools.execute(
    name="bash",
    tool_input={"command": "ctrl+c"}
)
```

### 特性
- 维护一个持久的Bash会话，可以保持环境变量和工作目录
- 支持标准输入、输出和错误流
- 可以执行复杂的命令链和管道
- 有120秒的默认超时时间

## 6. CreateChatCompletion

### 描述
使用LLM生成结构化的文本响应，允许代理在需要时获取额外的语言模型输出，并可以指定输出的格式。

### 参数
- 动态参数: 根据初始化时指定的响应类型，工具会自动生成所需的参数结构
- 默认情况下，需要提供:
  - **prompt** (必需): 发送给语言模型的提示
  - **system_prompt** (可选): 系统级提示，用于设置上下文
  - **temperature** (可选): 生成文本的随机性，默认为0.7

### 高级功能
- 支持指定响应类型，可以是简单的字符串或复杂的结构化数据
- 自动生成JSON模式，用于验证和格式化LLM的响应
- 支持多种数据类型，包括字符串、整数、浮点数、布尔值、字典和列表
- 支持联合类型和嵌套结构

### 使用示例
```python
# 基本使用 - 生成文本响应
result = await agent.available_tools.execute(
    name="create_chat_completion",
    tool_input={
        "prompt": "解释量子计算的基本原理",
        "system_prompt": "你是一位物理学专家，擅长简明解释复杂概念",
        "temperature": 0.3
    }
)

# 高级使用 - 使用自定义响应类型
from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    name: str
    age: int
    skills: List[str]

# 创建自定义工具实例
custom_completion = CreateChatCompletion(response_type=Person)
agent.available_tools.add_tool(custom_completion)

# 使用自定义工具
result = await agent.available_tools.execute(
    name="create_chat_completion",
    tool_input={
        "prompt": "创建一个虚构人物的资料",
        "system_prompt": "你是一位创意写作专家"
    }
)
# 结果将是一个符合Person模型的结构化数据
```

## 7. Terminate

### 描述
终止代理的执行流程，通常在任务完成或需要提前结束时使用。

### 参数
- **reason** (可选): 终止执行的原因

### 使用示例
```python
# 终止代理执行
result = await agent.available_tools.execute(
    name="terminate",
    tool_input={"reason": "任务已成功完成，无需进一步操作"}
)
```

## 工具扩展指南

OpenManus允许开发者创建自定义工具来扩展代理的能力。以下是创建自定义工具的基本步骤：

1. 继承BaseTool类
2. 定义工具名称、描述和参数
3. 实现execute方法
4. 将工具添加到代理的工具集合中

### 自定义工具示例

```python
from app.tool.base import BaseTool, ToolResult

class WeatherTool(BaseTool):
    name: str = "weather_tool"
    description: str = "获取指定城市的天气信息"
    parameters: dict = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "要查询天气的城市名称",
            },
            "days": {
                "type": "integer",
                "description": "预报天数，1-7之间",
            },
        },
        "required": ["city"],
    }

    async def execute(self, city: str, days: int = 1) -> ToolResult:
        # 实现天气查询逻辑
        # 这里只是示例，实际实现需要调用天气API
        weather_data = f"{city}未来{days}天天气：晴天，温度25°C"
        return ToolResult(output=weather_data)

# 添加到代理
agent = Manus()
agent.available_tools.add_tool(WeatherTool())
```

## 工具使用最佳实践

1. **选择合适的工具**: 根据任务需求选择最合适的工具，避免不必要的工具调用
2. **参数验证**: 确保提供所有必需的参数，并验证参数格式
3. **错误处理**: 妥善处理工具执行过程中可能出现的错误
4. **安全考虑**: 特别是使用PythonExecute和Bash工具时，注意代码安全性
5. **组合使用**: 多个工具组合使用可以解决复杂问题，例如先使用GoogleSearch获取信息，再使用BrowserUseTool深入探索

## 工具限制

1. **BrowserUseTool**: 
   - 不支持处理复杂的CAPTCHA验证
   - 某些网站可能限制自动化访问

2. **PythonExecute**:
   - 执行时间限制为5秒
   - 运行在受限环境中，某些库和系统调用可能不可用
   - 只能看到print输出，不能直接获取返回值

3. **GoogleSearch**:
   - 受API限制，可能有请求频率限制
   - 搜索结果可能因地区而异

4. **FileSaver**:
   - 只能在允许的目录中创建文件
   - 文件大小可能有限制

5. **Bash**:
   - 执行时间限制为120秒
   - 可能受到系统权限限制
   - 某些命令可能因安全原因被禁用

6. **CreateChatCompletion**:
   - 受LLM API限制，可能有请求频率和token限制
   - 复杂的结构化输出可能不总是符合预期
