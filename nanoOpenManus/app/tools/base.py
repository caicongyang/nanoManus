from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ToolResult:
    """工具执行结果的简单表示"""
    
    def __init__(self, output=None, error=None):
        self.output = output
        self.error = error
    
    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return str(self.output)


class BaseTool(ABC):
    """所有工具的基类，定义了工具的基本接口"""
    
    def __init__(self, name, description, parameters=None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    async def __call__(self, **kwargs) -> Any:
        """执行工具的简便方法"""
        return await self.execute(**kwargs)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行工具的具体逻辑，需要子类实现"""
        pass
    
    def to_param(self) -> Dict:
        """将工具转换为函数调用格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        } 