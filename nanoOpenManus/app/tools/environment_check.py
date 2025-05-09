import os
import socket
import platform

from nanoOpenManus.app.tools.base import BaseTool, ToolResult


class EnvironmentCheck(BaseTool):
    """检查执行环境的工具"""
    
    def __init__(self):
        super().__init__(
            name="environment_check",
            description="检查代码执行的环境信息，包括主机名、操作系统、Python版本等。",
            parameters={
                "type": "object",
                "properties": {
                    "detail_level": {
                        "type": "string",
                        "description": "返回的详细程度，basic或full",
                        "enum": ["basic", "full"],
                        "default": "basic",
                    },
                },
                "required": [],
            }
        )
    
    async def execute(self, detail_level: str = "basic") -> ToolResult:
        """
        检查并返回当前执行环境的信息
        
        Args:
            detail_level: 返回的详细程度，basic或full
            
        Returns:
            ToolResult: 包含环境信息的结果
        """
        try:
            # 基本信息
            env_info = {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "process_id": os.getpid(),
                "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            }
            
            # 检查是否在Docker容器中运行
            in_docker = os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")
            env_info["in_docker"] = in_docker
            
            # 如果是详细模式，添加更多信息
            if detail_level == "full":
                import sys
                import psutil
                
                # 当前工作目录
                env_info["current_dir"] = os.getcwd()
                
                # 内存使用情况
                process = psutil.Process(os.getpid())
                mem_info = process.memory_info()
                env_info["memory_usage"] = {
                    "rss": f"{mem_info.rss / (1024 * 1024):.2f} MB",
                    "vms": f"{mem_info.vms / (1024 * 1024):.2f} MB",
                }
                
                # 环境变量
                env_info["env_vars"] = {
                    key: value for key, value in os.environ.items()
                    if not key.startswith("OPENAI_") and not "KEY" in key.upper()  # 排除敏感信息
                }
                
                # 系统信息
                env_info["system_info"] = {
                    "cpu_count": os.cpu_count(),
                    "total_memory": f"{psutil.virtual_memory().total / (1024 * 1024 * 1024):.2f} GB",
                }
                
                # Python路径
                env_info["python_path"] = sys.executable
            
            # 格式化输出
            output = "环境信息:\n"
            output += f"主机名: {env_info['hostname']}\n"
            output += f"平台: {env_info['platform']}\n"
            output += f"Python版本: {env_info['python_version']}\n"
            output += f"进程ID: {env_info['process_id']}\n"
            output += f"用户: {env_info['user']}\n"
            output += f"Docker容器中: {'是' if env_info['in_docker'] else '否'}\n"
            
            if detail_level == "full":
                output += "\n详细信息:\n"
                output += f"当前目录: {env_info['current_dir']}\n"
                output += f"Python路径: {env_info['python_path']}\n"
                output += f"\n内存使用:\n"
                output += f"  RSS: {env_info['memory_usage']['rss']}\n"
                output += f"  VMS: {env_info['memory_usage']['vms']}\n"
                output += f"\nCPU核心数: {env_info['system_info']['cpu_count']}\n"
                output += f"总内存: {env_info['system_info']['total_memory']}\n"
                
                output += "\n环境变量:\n"
                for key, value in env_info['env_vars'].items():
                    output += f"  {key}: {value}\n"
            
            return ToolResult(output=output)
            
        except Exception as e:
            return ToolResult(error=f"获取环境信息时出错: {str(e)}") 