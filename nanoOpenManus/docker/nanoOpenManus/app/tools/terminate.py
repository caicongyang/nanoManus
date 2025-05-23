from nanoOpenManus.app.tools.base import BaseTool, ToolResult


class Terminate(BaseTool):
    """终止代理执行的工具"""
    
    def __init__(self):
        super().__init__(
            name="terminate",
            description="完成任务并终止代理执行。当任务完成且没有更多工作要做时使用此工具。",
            parameters={
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "终止执行的原因或总结。",
                    },
                },
                "required": ["reason"],
            }
        )
    
    async def execute(self, reason: str) -> ToolResult:
        """
        终止代理执行
        
        Args:
            reason: 终止执行的原因或总结
            
        Returns:
            ToolResult: 包含终止原因的结果
        """
        return ToolResult(output=f"任务已完成: {reason}") 