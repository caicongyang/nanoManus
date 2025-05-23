import os
from pathlib import Path
# from app.tools.base import BaseTool, ToolResult # Old import
from nanoOpenManus.app.tools.base import BaseTool, ToolResult # Changed back to absolute for docker exec context
# Note: We are defining the class as FileSaver directly to replace the original.
# The original FileSaver class definition is assumed to be in a different file
# or will be effectively overridden by this one in the Docker image.

class FileSaver(BaseTool): # Changed from SecureFileSaver(FileSaver) to FileSaver(BaseTool)
    """增强安全性的文件保存工具 (直接替换版)
    此类将直接作为 app.tools.file_saver.FileSaver 使用。
    """
    _name = "file_saver"
    _description = "将内容保存到运行环境的指定工作区内的文件中。"
    _parameters = [
        {
            "name": "content",
            "type": "string",
            "description": "要保存的文本内容。"
        },
        {
            "name": "file_path",
            "type": "string",
            "description": "相对于允许写入目录的文件路径，例如 'output.txt' 或 'subdirectory/report.html'。"
        },
        {
            "name": "mode",
            "type": "string",
            "description": "文件打开模式，默认为 'w' (写入，覆盖)。可以是 'a' (追加)。",
            "optional": True
        }
    ]

    def __init__(self):
        super().__init__(name=self._name, description=self._description, parameters=self._parameters)

    async def execute(self, content: str, file_path: str, mode: str = "w") -> ToolResult:
        allowed_dir = os.environ.get("ALLOWED_WRITE_DIR", "/workspace")
        # print(f"[FileSaver-Secure] ALLOWED_WRITE_DIR: {allowed_dir}")

        # 确保 file_path 是相对路径，并且不包含向上遍历的组件
        if os.path.isabs(file_path) or ".." in file_path.split(os.sep):
            return ToolResult(error=f"安全错误: file_path 必须是相对路径且不包含 '..'. 输入: '{file_path}'")

        # 规范化路径，并与允许的目录连接
        # allowed_dir 应该是绝对路径且已规范化
        allowed_dir = os.path.normpath(allowed_dir)
        if not os.path.isabs(allowed_dir):
            # This case should not happen if ALLOWED_WRITE_DIR is set correctly from a secure env
            print(f"Warning: ALLOWED_WRITE_DIR '{allowed_dir}' is not absolute. This might be a security risk.")
            # For safety, we might want to error out or have a default secure absolute path.
            # However, for now, we'll proceed assuming it's intentional for some specific setup.

        full_path = os.path.normpath(os.path.join(allowed_dir, file_path))

        # print(f"[FileSaver-Secure] Attempting to write to: {full_path}")

        # 再次检查，确保最终路径仍在 allowed_dir 管辖下
        if not full_path.startswith(allowed_dir):
            return ToolResult(error=f"安全错误: 最终路径 '{full_path}' 超出了允许的目录 '{allowed_dir}'.")

        # 检查文件大小
        if len(content.encode('utf-8')) > 10 * 1024 * 1024:  # 10MB limit on byte length
            return ToolResult(error="安全错误: 文件大小超过限制 (最大10MB)")
        
        try:
            # 创建目标目录 (如果不存在)
            directory = os.path.dirname(full_path)
            if not os.path.exists(directory):
                # 在创建目录前再次检查，确保目录路径也是安全的
                if not directory.startswith(allowed_dir):
                     return ToolResult(error=f"安全错误: 尝试创建不允许的目录 '{directory}'.")
                os.makedirs(directory, exist_ok=True)
            
            with open(full_path, mode, encoding="utf-8") as file:
                file.write(content)
            return ToolResult(output=f"内容已成功保存到 {file_path} (在允许的工作区内)")
        except Exception as e:
            return ToolResult(error=f"保存文件 '{file_path}' 时出错: {str(e)}") 