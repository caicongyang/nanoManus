import threading
import resource
import sys
from io import StringIO
# from .base import BaseTool, ToolResult # New relative import
from nanoOpenManus.app.tools.base import BaseTool, ToolResult # Changed back to absolute for docker exec context
# Note: We are defining the class as PythonExecute directly to replace the original.

class PythonExecute(BaseTool): # Changed from SecurePythonExecute(PythonExecute) to PythonExecute(BaseTool)
    """增强安全性的Python代码执行工具 (直接替换版)
    此类将直接作为 app.tools.python_execute.PythonExecute 使用。
    """
    _name = "python_execute" # Use _ to avoid clash if super() also sets name
    _description = "安全地执行Python代码片段，并返回标准输出。受限于超时和资源限制。"
    _parameters = [
        {
            "name": "code",
            "type": "string",
            "description": "要执行的Python代码字符串。"
        },
        {
            "name": "timeout",
            "type": "integer",
            "description": "代码执行的超时时间（秒），默认为5秒。",
            "optional": True
        }
    ]

    def __init__(self):
        super().__init__(name=self._name, description=self._description, parameters=self._parameters)

    async def execute(self, code: str, timeout: int = 5) -> ToolResult:
        result = {"output": ""}
        dangerous_modules = [
            "subprocess", "os.system", "shutil.rmtree", "sys.modules", # sys.modules is too broad, consider specific harmful modules
            "__import__('subprocess')", "__import__('os').system",
            # "exec(", "eval(", "compile(", # These are fundamental, blocking them breaks functionality.
            # Instead, we rely on the sandboxed global environment.
            # "open(", "file(", # Also fundamental. File access is controlled by FileSaver tool.
            "socket", # Example: disallow direct socket creation
            "multiprocessing",
            "ctypes",
            "_thread",
            # Add other modules/builtins deemed dangerous for direct execution if not explicitly sandboxed
        ]
        # Check for explicit import or direct usage of dangerous keywords
        # This is a basic check and might need refinement for more complex obfuscation
        for pattern in dangerous_modules:
            if pattern in code:
                # Allow specific exec/eval if they are part of a known safe pattern or library call if needed in future
                # For now, this is a simple string check
                return ToolResult(error=f"安全错误: 代码包含不允许的操作或模块: {pattern}")
        
        # Further check for direct open() call if not via FileSaver
        # This is tricky as 'open(' can appear in strings. A more robust check might use AST parsing.
        # if "open(" in code and not "FileSaver" in code and not "with open(" in code: # very naive
        #    return ToolResult(error=f"安全错误: 检测到直接的 open() 调用。请使用 FileSaver 工具进行文件操作。")

        def run_code_in_thread():
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            redirected_output = StringIO()
            redirected_error = StringIO()
            sys.stdout = redirected_output
            sys.stderr = redirected_error

            try:
                # Set resource limits (लागू नहीं होगा सीधे विंडोज पर, लिनक्स/मैक पर काम करेगा)
                # Memory limit (e.g., 500MB)
                if hasattr(resource, 'RLIMIT_AS'):
                    resource.setrlimit(resource.RLIMIT_AS, (500 * 1024 * 1024, 500 * 1024 * 1024))
                # CPU time limit (e.g., timeout seconds) - This is harder to enforce directly for CPU time slices
                # The threading.join(timeout) is the primary timeout mechanism here.

                # Define a limited set of globals for the exec environment
                safe_globals = {
                    "__builtins__": {
                        "abs": abs, "all": all, "any": any, "ascii": ascii,
                        "bin": bin, "bool": bool, "bytearray": bytearray, "bytes": bytes, "callable": callable,
                        "chr": chr, "complex": complex, "dict": dict, "dir": dir, "divmod": divmod,
                        "enumerate": enumerate, "filter": filter, "float": float, "format": format,
                        "frozenset": frozenset, "getattr": getattr, "hasattr": hasattr, "hash": hash, 
                        "help": help, "hex": hex, "id": id, "input": input, "int": int, 
                        "isinstance": isinstance, "issubclass": issubclass, "iter": iter, "len": len, 
                        "list": list, "locals": locals, "map": map, "max": max, "memoryview": memoryview, 
                        "min": min, "next": next, "object": object, "oct": oct, "ord": ord, 
                        "pow": pow, "print": print, "property": property, "range": range, "repr": repr, 
                        "reversed": reversed, "round": round, "set": set, "setattr": setattr, 
                        "slice": slice, "sorted": sorted, "staticmethod": staticmethod, "str": str, 
                        "sum": sum, "super": super, "tuple": tuple, "type": type, "vars": vars, "zip": zip,
                        # 'open': open, # Explicitly do not include open, use FileSaver tool
                        # 'eval': eval, 'exec': exec, 'compile': compile # Do not include these directly
                    },
                    # Commonly used safe modules
                    "math": __import__('math'),
                    "random": __import__('random'),
                    "datetime": __import__('datetime'),
                    "time": __import__('time'),
                    "json": __import__('json'),
                    "re": __import__('re'),
                    "collections": __import__('collections'),
                    "functools": __import__('functools'),
                    "itertools": __import__('itertools'),
                    "operator": __import__('operator'),
                    "string": __import__('string'),
                    "decimal": __import__('decimal')
                }
                
                exec(code, safe_globals, {}) # Local scope for exec is empty
                result["output"] = redirected_output.getvalue()
                error_output = redirected_error.getvalue()
                if error_output:
                    result["output"] += "\nSTDERR:\n" + error_output

            except MemoryError:
                result["output"] = "错误: 执行代码超出内存限制。"
            except Exception as e:
                result["output"] = f"执行代码时出错: {type(e).__name__}: {str(e)}"
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        thread = threading.Thread(target=run_code_in_thread)
        thread.daemon = True # Ensure thread doesn't block program exit
        thread.start()
        thread.join(timeout) # Wait for the thread to complete or timeout
        
        if thread.is_alive():
            # Thread is still running after timeout, implies it's stuck or taking too long
            # Attempt to clean up (though forceful termination of threads is tricky in Python)
            # For now, we just report timeout.
            return ToolResult(error=f"执行超时 ({timeout} 秒)。代码可能包含无限循环或长时间操作。")
        
        if "错误:" in result["output"] or "STDERR:" in result["output"]:
             return ToolResult(error=result["output"])
        return ToolResult(output=result["output"]) 