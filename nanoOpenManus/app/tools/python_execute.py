import threading

from nanoOpenManus.app.tools.base import BaseTool, ToolResult


class PythonExecute(BaseTool):
    """执行Python代码的工具"""
    
    def __init__(self):
        super().__init__(
            name="python_execute",
            description="执行Python代码字符串。注意：只有print输出可见，函数返回值不会被捕获。使用print语句查看结果。",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码。",
                    },
                },
                "required": ["code"],
            }
        )
    
    async def execute(self, code: str, timeout: int = 5) -> ToolResult:
        """
        执行Python代码并返回结果
        
        Args:
            code: 要执行的Python代码
            timeout: 执行超时时间（秒）
            
        Returns:
            ToolResult: 包含执行输出或错误信息
        """
        result = {"output": ""}
        
        def run_code():
            try:
                # 创建安全的执行环境
                safe_globals = {"__builtins__": dict(__builtins__)}
                
                # 捕获标准输出
                import sys
                from io import StringIO
                
                output_buffer = StringIO()
                sys.stdout = output_buffer
                
                # 执行代码
                exec(code, safe_globals, {})
                
                # 恢复标准输出
                sys.stdout = sys.__stdout__
                
                # 获取输出
                result["output"] = output_buffer.getvalue()
                
            except Exception as e:
                result["output"] = f"错误: {str(e)}"
        
        # 在线程中执行代码
        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout)
        
        # 检查是否超时
        if thread.is_alive():
            return ToolResult(error=f"执行超时（{timeout}秒）")
        
        return ToolResult(output=result["output"]) 