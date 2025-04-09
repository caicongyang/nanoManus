# OpenManus Browser-Use 和 Computer-Use 代码分析

## 1. 工具基础架构

### 1.1 基础工具类定义
```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """所有工具的基类"""
    name: str
    description: str

    @abstractmethod
    async def execute(self, tool_input: dict) -> dict:
        """执行工具操作的抽象方法"""
        pass
```

### 1.2 工具管理器
```python
class ToolManager:
    def __init__(self):
        self.tools = {}
        self.security_manager = SecurityManager()

    def register_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    async def execute_tool(self, name: str, input_data: dict) -> dict:
        if name not in self.tools:
            return {"status": "error", "message": f"Tool {name} not found"}
        return await self.tools[name].execute(input_data)
```

## 2. Browser-Use 实现

### 2.1 核心类实现
```python
from playwright.async_api import async_playwright

class BrowserUse(BaseTool):
    name = "browser_use"
    description = "执行浏览器自动化操作"

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def setup(self):
        """初始化浏览器环境"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def execute(self, tool_input: dict) -> dict:
        try:
            if not self.browser:
                await self.setup()

            # 处理URL访问
            if "url" in tool_input:
                await self.page.goto(tool_input["url"])

            # 执行动作序列
            if "actions" in tool_input:
                for action in tool_input["actions"]:
                    await self._execute_action(action)

            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _execute_action(self, action: dict):
        """执行具体的浏览器动作"""
        action_type = action.get("type")
        if action_type == "click":
            await self.page.click(action["selector"])
        elif action_type == "type":
            await self.page.fill(action["selector"], action["text"])
        elif action_type == "screenshot":
            await self.page.screenshot(path=action["path"])
```

### 2.2 使用示例
```python
# Browser-Use 使用示例
async def browser_example():
    browser_tool = BrowserUse()
    result = await browser_tool.execute({
        "url": "https://example.com",
        "actions": [
            {"type": "click", "selector": "#search-button"},
            {"type": "type", "selector": "#search-input", "text": "OpenManus"},
            {"type": "screenshot", "path": "search_result.png"}
        ]
    })
```

## 3. Computer-Use 实现

### 3.1 核心类实现
```python
import os
import asyncio

class ComputerUse(BaseTool):
    name = "computer_use"
    description = "执行本地计算机操作"

    async def execute(self, tool_input: dict) -> dict:
        try:
            operation_type = tool_input.get("type")
            if operation_type == "file":
                return await self._handle_file_operation(tool_input)
            elif operation_type == "command":
                return await self._handle_command(tool_input)
            return {"status": "error", "message": "Unknown operation type"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _handle_file_operation(self, input_data: dict):
        """处理文件操作"""
        operation = input_data.get("operation")
        path = input_data.get("path")

        if operation == "read":
            with open(path, 'r') as f:
                content = f.read()
            return {"status": "success", "content": content}
        elif operation == "write":
            with open(path, 'w') as f:
                f.write(input_data.get("content", ""))
            return {"status": "success"}

    async def _handle_command(self, input_data: dict):
        """处理系统命令"""
        command = input_data.get("command")
        args = input_data.get("args", [])
        cwd = input_data.get("cwd")

        process = await asyncio.create_subprocess_exec(
            command,
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return {
            "status": "success",
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "return_code": process.returncode
        }
```

### 3.2 使用示例
```python
# Computer-Use 使用示例
async def computer_example():
    computer_tool = ComputerUse()

    # 文件操作示例
    file_result = await computer_tool.execute({
        "type": "file",
        "operation": "write",
        "path": "test.txt",
        "content": "Hello OpenManus!"
    })

    # 命令执行示例
    command_result = await computer_tool.execute({
        "type": "command",
        "command": "ls",
        "args": ["-la"],
        "cwd": "/project/directory"
    })
```

## 4. 安全机制

### 4.1 安全管理器
```python
class SecurityManager:
    def __init__(self):
        self.allowed_domains = ["github.com", "google.com"]
        self.allowed_paths = ["/project", "/data"]
        self.allowed_commands = ["ls", "git", "python"]

    def validate_url(self, url: str) -> bool:
        """验证URL是否允许访问"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain in self.allowed_domains

    def validate_path(self, path: str) -> bool:
        """验证文件路径是否允许访问"""
        return any(path.startswith(allowed) for allowed in self.allowed_paths)

    def validate_command(self, command: str) -> bool:
        """验证命令是否允许执行"""
        return command in self.allowed_commands
```

## 5. 错误处理和资源管理

### 5.1 错误处理
```python
class ErrorHandler:
    @staticmethod
    async def handle_browser_error(error, browser_tool):
        """处理浏览器错误"""
        if isinstance(error, TimeoutError):
            await browser_tool.restart()
        elif isinstance(error, ConnectionError):
            await browser_tool.reconnect()
        return {"status": "error", "message": str(error)}

    @staticmethod
    async def handle_computer_error(error):
        """处理系统操作错误"""
        if isinstance(error, PermissionError):
            return {"status": "error", "message": "Permission denied"}
        elif isinstance(error, FileNotFoundError):
            return {"status": "error", "message": "File not found"}
        return {"status": "error", "message": str(error)}
```

### 5.2 资源管理器
```python
class ResourceManager:
    def __init__(self):
        self.active_browsers = []
        self.active_processes = []

    async def cleanup(self):
        """清理资源"""
        for browser in self.active_browsers:
            await browser.close()
        for process in self.active_processes:
            process.terminate()

    async def add_browser(self, browser):
        """添加浏览器实例"""
        self.active_browsers.append(browser)

    async def add_process(self, process):
        """添加进程"""
        self.active_processes.append(process)
```

## 6. 最佳实践

1. **浏览器操作**:
   - 使用显式等待而不是固定延时
   - 实现重试机制处理临时性失败
   - 及时清理浏览器资源
   - 使用页面池优化性能

2. **系统操作**:
   - 严格控制命令执行权限
   - 实现超时机制
   - 记录所有操作日志
   - 定期清理临时文件

3. **错误处理**:
   - 实现优雅的错误恢复机制
   - 提供详细的错误信息
   - 记录错误日志
   - 实现回滚机制

4. **安全考虑**:
   - 实现访问控制白名单
   - 验证所有输入数据
   - 限制资源使用
   - 监控异常行为
