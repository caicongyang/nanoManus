#!/bin/bash
set -e

# 打印欢迎信息
echo "========================================"
echo "NanoOpenManus 沙箱环境"
echo "========================================"
echo "- 工作目录: /app/workspace"
echo "- 最大步骤数: $MAX_STEPS"
echo "- 调试模式: $DEBUG"
echo "========================================"

# 创建必要的目录
mkdir -p /app/workspace

# 修补FileSaver工具，添加安全限制
cat > /app/nanoOpenManus/app/tools/file_saver_patch.py << 'EOF'
import os
from pathlib import Path
from nanoOpenManus.app.tools.base import BaseTool, ToolResult
from nanoOpenManus.app.tools.file_saver import FileSaver

class SecureFileSaver(FileSaver):
    """增强安全性的文件保存工具"""
    
    async def execute(self, content: str, file_path: str, mode: str = "w") -> ToolResult:
        """
        安全地将内容保存到指定路径的文件中
        
        Args:
            content: 要保存的内容
            file_path: 保存文件的路径
            mode: 文件打开模式，'w'为写入（覆盖），'a'为追加
            
        Returns:
            ToolResult: 包含操作结果或错误信息
        """
        # 获取允许写入的目录
        allowed_dir = os.environ.get("ALLOWED_WRITE_DIR", "/app/workspace")
        
        # 规范化路径
        file_path = os.path.normpath(file_path)
        allowed_dir = os.path.normpath(allowed_dir)
        
        # 确保file_path是绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(allowed_dir, file_path)
        
        # 安全检查 - 确保文件路径在允许的目录下
        if not os.path.commonpath([file_path]) == os.path.commonpath([allowed_dir]) and \
           not os.path.commonpath([file_path]) == os.path.commonpath([os.path.join(allowed_dir, os.path.basename(file_path))]):
            return ToolResult(error=f"安全错误: 不允许在 '{allowed_dir}' 之外写入文件")
        
        # 文件大小限制 (如果内容超过10MB)
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return ToolResult(error="安全错误: 文件大小超过限制 (最大10MB)")
            
        # 执行原始FileSaver的逻辑
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
EOF

# 修补PythonExecute工具，增强安全性
cat > /app/nanoOpenManus/app/tools/python_execute_patch.py << 'EOF'
import threading
import resource
import sys
from io import StringIO
from nanoOpenManus.app.tools.base import BaseTool, ToolResult
from nanoOpenManus.app.tools.python_execute import PythonExecute

class SecurePythonExecute(PythonExecute):
    """增强安全性的Python代码执行工具"""
    
    async def execute(self, code: str, timeout: int = 5) -> ToolResult:
        """
        安全地执行Python代码并返回结果
        
        Args:
            code: 要执行的Python代码
            timeout: 执行超时时间（秒）
            
        Returns:
            ToolResult: 包含执行输出或错误信息
        """
        result = {"output": ""}
        
        # 检查高危模块和操作
        dangerous_modules = [
            "subprocess", "os.system", "shutil.rmtree", "sys.modules",
            "__import__('subprocess')", "__import__('os').system", 
            "exec(", "eval(", "compile(", "open(", "file(", "execfile("
        ]
        
        for module in dangerous_modules:
            if module in code:
                return ToolResult(error=f"安全错误: 代码包含不允许的操作或模块: {module}")
        
        def run_code():
            try:
                # 设置资源限制
                resource.setrlimit(resource.RLIMIT_AS, (500 * 1024 * 1024, 500 * 1024 * 1024))  # 内存限制500MB
                
                # 创建安全的执行环境
                safe_globals = {
                    "__builtins__": {
                        # 允许的内置函数
                        "abs": abs, "all": all, "any": any, "ascii": ascii,
                        "bin": bin, "bool": bool, "bytes": bytes, "callable": callable,
                        "chr": chr, "complex": complex, "dict": dict, "dir": dir,
                        "divmod": divmod, "enumerate": enumerate, "filter": filter,
                        "float": float, "format": format, "frozenset": frozenset,
                        "hash": hash, "hex": hex, "id": id, "int": int,
                        "isinstance": isinstance, "issubclass": issubclass, "iter": iter,
                        "len": len, "list": list, "map": map, "max": max,
                        "min": min, "next": next, "object": object, "oct": oct,
                        "ord": ord, "pow": pow, "print": print, "range": range,
                        "repr": repr, "reversed": reversed, "round": round, "set": set,
                        "slice": slice, "sorted": sorted, "str": str, "sum": sum,
                        "tuple": tuple, "type": type, "zip": zip,
                    }
                }
                
                # 导入安全模块
                import math
                import random
                import datetime
                import json
                import re
                
                safe_globals["math"] = math
                safe_globals["random"] = random
                safe_globals["datetime"] = datetime
                safe_globals["json"] = json
                safe_globals["re"] = re
                
                # 捕获标准输出
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
        thread.daemon = True  # 标记为守护线程，防止阻止程序退出
        thread.start()
        thread.join(timeout)
        
        # 检查是否超时
        if thread.is_alive():
            return ToolResult(error=f"执行超时（{timeout}秒）")
        
        return ToolResult(output=result["output"])
EOF

# 修补主程序，使用安全版本的工具
cat > /app/nanoOpenManus/app/tools_patch.py << 'EOF'
# 导入补丁模块
import importlib.util
import sys

# 动态加载补丁模块
def load_patch_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# 加载安全工具补丁
secure_file_saver_module = load_patch_module(
    "nanoOpenManus.app.tools.file_saver_patch", 
    "/app/nanoOpenManus/app/tools/file_saver_patch.py"
)

secure_python_execute_module = load_patch_module(
    "nanoOpenManus.app.tools.python_execute_patch",
    "/app/nanoOpenManus/app/tools/python_execute_patch.py"
)

# 替换原始类
from nanoOpenManus.app.manus import Manus
from nanoOpenManus.app.tools.terminate import Terminate
from nanoOpenManus.app.tools.tool_collection import ToolCollection

# 保存原始初始化方法
original_init = Manus.__init__

# 创建增强安全性的初始化方法
def secure_init(self, *args, **kwargs):
    # 调用原始初始化方法
    original_init(self, *args, **kwargs)
    
    # 替换工具为安全版本
    self.available_tools = ToolCollection()
    self.available_tools.add_tool(secure_python_execute_module.SecurePythonExecute())
    self.available_tools.add_tool(secure_file_saver_module.SecureFileSaver())
    self.available_tools.add_tool(Terminate())
    
    print("✅ 已加载安全增强版工具")

# 替换初始化方法
Manus.__init__ = secure_init
EOF

# 创建启动脚本
cat > /app/start.py << 'EOF'
import sys
import os
import asyncio

# 导入安全补丁
import nanoOpenManus.app.tools_patch

# 导入主模块
from nanoOpenManus.main import main

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
EOF

# 运行应用
cd /app && python start.py "$@" 