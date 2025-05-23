from typing import Dict, List

from nanoOpenManus.app.tools.base import BaseTool


class ToolCollection:
    """管理多个工具的集合"""
    
    def __init__(self, *tools):
        self.tool_map: Dict[str, BaseTool] = {}
        for tool in tools:
            self.add_tool(tool)
    
    def add_tool(self, tool: BaseTool) -> None:
        """添加一个工具到集合中"""
        self.tool_map[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """根据名称获取工具"""
        return self.tool_map.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有可用的工具名称"""
        return list(self.tool_map.keys())
    
    async def execute(self, name: str, tool_input: Dict) -> str:
        """执行指定名称的工具"""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        
        try:
            result = await tool.execute(**tool_input)
            return result
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"
    
    def to_params(self) -> List[Dict]:
        """将所有工具转换为函数调用格式列表"""
        return [tool.to_param() for tool in self.tool_map.values()] 