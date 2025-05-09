import os
from nanoOpenManus.app.manus import Manus
from nanoOpenManus.app.tools.python_execute import PythonExecute
from nanoOpenManus.app.tools.file_saver import FileSaver
from nanoOpenManus.app.tools.terminate import Terminate
from nanoOpenManus.app.tools.environment_check import EnvironmentCheck
from nanoOpenManus.app.tools.docker_proxy import DockerToolProxy, DockerToolWrapper


class DockerManus(Manus):
    """
    Docker版本的Manus代理 - 将工具执行转发到Docker容器
    
    这个代理继承了Manus，但替换了工具的实现，使工具在Docker容器中执行
    """
    
    def __init__(
        self,
        name="DockerManus",
        description="Docker版本的Manus代理，将工具执行安全地隔离在Docker容器中",
        max_steps=15,
        api_key=None,
        model=None,
        base_url=None,
        container_name="nanomanus-sandbox"
    ):
        # 使用父类初始化基本属性
        super().__init__(
            name=name,
            description=description,
            max_steps=max_steps,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        
        # 创建Docker工具代理
        try:
            self.docker_proxy = DockerToolProxy(container_name)
            
            # 替换工具为Docker包装版本
            self._wrap_tools_with_docker()
            
            print(f"🐳 工具已配置为在Docker容器 '{container_name}' 中执行")
        except Exception as e:
            print(f"⚠️ Docker代理初始化失败: {str(e)}")
            print("⚠️ 将继续使用本地工具执行")
    
    def _wrap_tools_with_docker(self):
        """将工具替换为Docker包装版本"""
        # 创建原始工具实例
        python_tool = PythonExecute()
        file_tool = FileSaver()
        terminate_tool = Terminate()
        env_check_tool = EnvironmentCheck()
        
        # 使用Docker包装器包装工具
        docker_python_tool = DockerToolWrapper(python_tool, self.docker_proxy)
        docker_file_tool = DockerToolWrapper(file_tool, self.docker_proxy)
        docker_terminate_tool = DockerToolWrapper(terminate_tool, self.docker_proxy)
        docker_env_check_tool = DockerToolWrapper(env_check_tool, self.docker_proxy)
        
        # 替换工具集合
        self.available_tools.tool_map = {}
        self.available_tools.add_tool(docker_python_tool)
        self.available_tools.add_tool(docker_file_tool)
        self.available_tools.add_tool(docker_terminate_tool)
        self.available_tools.add_tool(docker_env_check_tool) 