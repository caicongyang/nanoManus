import os

from nanoOpenManus.app.tools.base import BaseTool, ToolResult


class FileSaver(BaseTool):
    """保存内容到文件的工具"""
    
    def __init__(self):
        super().__init__(
            name="file_saver",
            description="""将内容保存到指定路径的本地文件中。
当需要保存文本、代码或生成的内容到本地文件系统时使用此工具。
该工具接受内容和文件路径，并将内容保存到该位置。""",
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要保存到文件的内容。",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "文件保存的路径，包括文件名和扩展名。",
                    },
                    "mode": {
                        "type": "string",
                        "description": "文件打开模式。默认为'w'（写入）。使用'a'表示追加内容。",
                        "enum": ["w", "a"],
                        "default": "w",
                    },
                },
                "required": ["content", "file_path"],
            }
        )
    
    async def execute(self, content: str, file_path: str, mode: str = "w") -> ToolResult:
        """
        将内容保存到指定路径的文件中
        
        Args:
            content: 要保存的内容
            file_path: 保存文件的路径
            mode: 文件打开模式，'w'为写入（覆盖），'a'为追加
            
        Returns:
            ToolResult: 包含操作结果或错误信息
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 写入文件
            with open(file_path, mode, encoding="utf-8") as file:
                file.write(content)
            
            return ToolResult(output=f"内容已成功保存到 {file_path}")
        except Exception as e:
            return ToolResult(error=f"保存文件时出错: {str(e)}") 