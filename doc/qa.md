# OpenManus 工具选择与调用 Q&A

## Q: OpenManus 是如何选择工具或者调用tools的？

A: OpenManus 采用了一个结构化的工具选择和调用流程，具体工作原理如下：

### 工具选择流程

1. **代理决策**: Manus 代理（继承自 ToolCallAgent）接收用户请求后，通过 LLM 分析用户需求，确定需要使用哪些工具。

2. **工具可用性**: 代理会根据 `available_tools` 集合中注册的工具来确定可以使用哪些工具。这些工具在代理初始化时被添加:
   ```python
   self.available_tools.add_tool(PythonExecute())
   self.available_tools.add_tool(FileSaver())
   self.available_tools.add_tool(Terminate())
   ```

3. **工具匹配**: 代理使用系统提示（system_prompt）和下一步提示（next_step_prompt）来指导 LLM 选择合适的工具，这些提示明确告诉 LLM 可用的工具及其用途。

### 工具调用机制

1. **工具调用格式**: 当代理决定调用工具时，会生成包含工具名称和参数的请求。例如：
   ```python
   {"name": "python_execute", "arguments": {"code": "print('Hello, world!')"}}
   ```

2. **参数验证**: 工具调用前，系统会验证提供的参数是否符合工具定义的要求。

3. **执行过程**: 工具调用通过 `ToolCollection` 类的 `execute` 方法进行，它会：
   - 查找请求的工具
   - 验证工具参数
   - 执行工具操作
   - 返回执行结果

4. **结果处理**: 工具执行的结果会返回给代理，代理会解析结果并决定下一步操作。

### 工具调用示例

以下是一个工具调用的典型流程：

1. 用户请求："帮我写一个计算斐波那契数列的程序"

2. 代理分析请求并决定使用 `python_execute` 工具

3. 代理生成工具调用：
   ```python
   await agent.available_tools.execute(
       name="python_execute",
       tool_input={"code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(10):\n    print(fibonacci(i))"}
   )
   ```

4. 工具执行代码并返回结果

5. 代理解析结果，可能决定使用 `file_saver` 工具保存代码，或使用 `terminate` 工具结束任务

### 关键组件

- **ToolCallAgent**: 基础代理类，提供工具调用能力
- **ToolCollection**: 管理工具集合的类
- **LLM**: 负责决策的大语言模型，分析用户需求并选择合适工具
- **系统提示**: 指导 LLM 如何理解工具并做出选择的关键信息

### 优势

这种架构使 OpenManus 能够灵活地选择和组合工具，根据用户的具体需求提供解决方案。工具是可扩展的，可以通过添加新工具来增强代理的能力。

## Q: OpenManus 是如何使用 browser-use 和 computer-use 的？

A: OpenManus 通过集成 browser-use 和 computer-use 工具来实现网页浏览和计算机操作功能。以下是详细说明：

### Browser-Use 使用机制

1. **功能定义**：
   - 用于自动化浏览器操作
   - 支持网页访问、点击、输入、截图等操作
   - 基于 Playwright 实现

2. **主要操作类型**：
   ```python
   {
       "type": "browser",
       "url": "要访问的网址",
       "actions": [
           {"type": "click", "selector": "元素选择器"},
           {"type": "type", "selector": "输入框选择器", "text": "要输入的文本"},
           {"type": "screenshot", "path": "截图保存路径"}
       ]
   }
   ```

3. **使用场景**：
   - 网页信息采集
   - 自动化表单填写
   - 网页交互测试
   - 网页截图保存

### Computer-Use 使用机制

1. **功能定义**：
   - 执行本地计算机操作
   - 文件系统操作
   - 系统命令执行
   - 环境变量管理

2. **主要操作类型**：
   ```python
   {
       "type": "computer",
       "command": "要执行的命令",
       "args": ["命令参数"],
       "cwd": "工作目录"
   }
   ```

3. **使用场景**：
   - 文件创建、读取、写入
   - 目录操作
   - 系统命令执行
   - 环境配置管理

### 工具集成流程

1. **初始化**：
   ```python
   class ManusAgent(ToolCallAgent):
       def __init__(self):
           super().__init__()
           self.available_tools.add_tool(BrowserUse())
           self.available_tools.add_tool(ComputerUse())
   ```

2. **调用流程**：
   - LLM 分析用户需求
   - 选择合适的工具（browser-use 或 computer-use）
   - 生成工具调用参数
   - 执行操作并返回结果

3. **错误处理**：
   - 工具执行失败时的重试机制
   - 异常情况的错误报告
   - 操作超时处理

### 安全考虑

1. **Browser-Use 安全机制**：
   - 浏览器沙箱环境
   - 访问域名白名单
   - 敏感操作确认

2. **Computer-Use 安全机制**：
   - 命令执行权限控制
   - 文件系统访问限制
   - 环境变量保护

### 使用示例

1. **Browser-Use 示例**：
   ```python
   await agent.available_tools.execute(
       name="browser_use",
       tool_input={
           "type": "browser",
           "url": "https://example.com",
           "actions": [
               {"type": "click", "selector": "#search-button"},
               {"type": "type", "selector": "#search-input", "text": "OpenManus"}
           ]
       }
   )
   ```

2. **Computer-Use 示例**：
   ```python
   await agent.available_tools.execute(
       name="computer_use",
       tool_input={
           "type": "computer",
           "command": "ls",
           "args": ["-la"],
           "cwd": "/project/directory"
       }
   )
   ```

### 最佳实践

1. **工具选择原则**：
   - 网页相关操作优先使用 browser-use
   - 本地系统操作优先使用 computer-use
   - 需要组合操作时可以串联使用两个工具

2. **性能优化**：
   - 浏览器实例复用
   - 命令执行并行化
   - 资源释放管理

3. **错误处理**：
   - 实现优雅的失败处理
   - 提供清晰的错误信息
   - 支持操作回滚
