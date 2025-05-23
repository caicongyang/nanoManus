import json
import os
import subprocess
import asyncio
from typing import Dict, Any

from nanoOpenManus.app.tools.base import BaseTool, ToolResult


class DockerToolProxy:
    """
    工具代理类，将工具调用转发到Docker容器中执行
    """
    
    def __init__(self, container_name="nanomanus-sandbox"):
        self.container_name = container_name
        self._ensure_container_running()
    
    def _ensure_container_running(self):
        """确保Docker容器正在运行"""
        try:
            # 检查容器是否存在
            check_cmd = ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"]
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if not result.stdout.strip():
                # 容器不存在，尝试启动
                print(f"⚠️ 容器 {self.container_name} 不存在，正在启动...")
                self._start_container()
            elif not result.stdout.strip().startswith("Up"):
                # 容器存在但未运行
                print(f"⚠️ 容器 {self.container_name} 未运行，正在启动...")
                start_cmd = ["docker", "start", self.container_name]
                subprocess.run(start_cmd, check=True)
                
            print(f"✅ 容器 {self.container_name} 已准备就绪")
        except Exception as e:
            raise RuntimeError(f"准备Docker容器时出错: {str(e)}")
    
    def _start_container(self):
        """启动Docker容器"""
        try:
            # 切换到Docker目录
            docker_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docker")
            
            # 启动容器
            subprocess.run(
                ["docker-compose", "up", "-d"], 
                cwd=docker_dir, 
                check=True
            )
        except Exception as e:
            raise RuntimeError(f"启动Docker容器时出错: {str(e)}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        在Docker容器中执行工具
        
        Args:
            tool_name: 要执行的工具名称
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        try:
            # 准备工具调用JSON
            tool_call = {
                "tool": tool_name,
                "args": kwargs
            }
            
            # 将调用转换为JSON字符串
            tool_call_json = json.dumps(tool_call)
            
            # 准备Python命令
            python_cmd = (
                f"import json, asyncio; "
                f"from nanoOpenManus.app.tools.tool_collection import ToolCollection; "
                f"from nanoOpenManus.app.tools.python_execute import PythonExecute; "
                f"from nanoOpenManus.app.tools.file_saver import FileSaver; "
                f"from nanoOpenManus.app.tools.terminate import Terminate; "
                f"tools = ToolCollection(PythonExecute(), FileSaver(), Terminate()); "
                f"tool_call = json.loads({repr(tool_call_json)}); "
                f"result = asyncio.run(tools.execute(name=tool_call['tool'], tool_input=tool_call['args'])); "
                f"print(json.dumps({{'output': str(result.output) if result.output is not None else None, "
                f"'error': str(result.error) if result.error is not None else None}}));"
            )
            
            # 在Docker容器中执行命令
            cmd = ["docker", "exec", self.container_name, "python", "-c", python_cmd]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return ToolResult(error=f"在Docker中执行工具失败: {stderr.decode().strip()}")
            
            # 解析结果
            try:
                result_json = json.loads(stdout.decode().strip())
                if result_json.get("error"):
                    return ToolResult(error=result_json["error"])
                return ToolResult(output=result_json["output"])
            except json.JSONDecodeError:
                # 如果无法解析JSON，直接返回输出
                return ToolResult(output=stdout.decode().strip())
                
        except Exception as e:
            return ToolResult(error=f"工具代理错误: {str(e)}")


class DockerToolWrapper(BaseTool):
    """
    包装原始工具，将执行转发到Docker容器
    """
    
    def __init__(self, original_tool: BaseTool, proxy: DockerToolProxy):
        """
        初始化工具包装器
        
        Args:
            original_tool: 原始工具实例
            proxy: Docker工具代理
        """
        # 保持原始工具的属性
        super().__init__(
            name=original_tool.name,
            description=original_tool.description,
            parameters=original_tool.parameters
        )
        self.proxy = proxy
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具，转发到Docker容器
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        return await self.proxy.execute_tool(self.name, **kwargs) 