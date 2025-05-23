import os
from nanoOpenManus.app.agent import ToolCallAgent
from nanoOpenManus.app.tools.file_saver import FileSaver
from nanoOpenManus.app.tools.python_execute import PythonExecute
from nanoOpenManus.app.tools.terminate import Terminate
from nanoOpenManus.app.tools.environment_check import EnvironmentCheck
from nanoOpenManus.app.tools.tool_collection import ToolCollection

# 尝试导入LLM和配置
try:
    from nanoOpenManus.app.llm import LLM
    from nanoOpenManus.app.config import config
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class Manus(ToolCallAgent):
    """
    Manus代理 - 一个通用的能够解决各种任务的代理
    
    这个代理继承了ToolCallAgent，集成了多种工具和能力，包括Python代码执行、
    文件操作和终止功能，可以处理各种用户请求。
    """
    
    def __init__(
        self,
        name="Manus",
        description="一个能够使用多种工具解决各种任务的通用代理",
        max_steps=15,
        api_key=None,
        model=None,
        base_url=None,
    ):
        system_prompt = "你是OpenManus，一个全能的AI助手，能够解决用户提出的任何任务。你可以调用各种工具来高效完成复杂的请求。无论是编程、信息检索、文件处理还是网页浏览，你都能应对自如。"
        next_step_prompt = """你可以使用以下工具与计算机交互：
        
1. python_execute: 执行Python代码，用于与计算机系统交互、数据处理、自动化任务等。
2. file_saver: 在本地保存文件，如txt、py、html等。
3. environment_check: 检查代码执行环境，验证是本地环境还是Docker容器。
4. terminate: 完成任务后终止代理执行。

根据用户需求，主动选择最合适的工具或工具组合。对于复杂任务，可以将问题分解，逐步使用不同的工具来解决。每次使用工具后，清晰地解释执行结果并提出下一步建议。"""

        super().__init__(name, description, system_prompt, next_step_prompt)
        self.max_steps = max_steps
        
        # 添加内置工具
        self.available_tools.add_tool(PythonExecute())
        self.available_tools.add_tool(FileSaver())
        self.available_tools.add_tool(EnvironmentCheck())
        self.available_tools.add_tool(Terminate())
        
        # 如果LLM可用，初始化LLM客户端
        if LLM_AVAILABLE:
            # 获取API密钥 - 优先使用传入的参数，其次使用配置，最后使用环境变量
            llm_api_key = api_key or (hasattr(config, 'llm_api_key') and config.llm_api_key) or os.environ.get("DEEPSEEK_API_KEY")
            llm_model = model or (hasattr(config, 'llm_model') and config.llm_model) or "deepseek-chat"
            llm_base_url = base_url or (hasattr(config, 'llm_base_url') and config.llm_base_url) or "https://api.deepseek.com"
            
            if llm_api_key:
                try:
                    self.llm = LLM(
                        api_key=llm_api_key,
                        model=llm_model,
                        base_url=llm_base_url
                    )
                    print(f"✅ LLM客户端初始化成功 (模型: {llm_model})")
                except Exception as e:
                    print(f"⚠️ LLM客户端初始化失败: {str(e)}")
                    self.llm = None
            else:
                print("⚠️ 未提供API密钥，使用模拟思考模式")
                self.llm = None
        else:
            print("⚠️ LLM模块不可用，使用模拟思考模式")
            self.llm = None
