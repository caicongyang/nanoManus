import json
from enum import Enum
from typing import Dict, List, Optional

from nanoOpenManus.app.tools.base import ToolResult
from nanoOpenManus.app.tools.tool_collection import ToolCollection


class AgentState(str, Enum):
    """代理的状态"""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class Message:
    """简化的消息类，用于代理与LLM之间的通信"""
    
    def __init__(self, role, content):
        self.role = role
        self.content = content
    
    @staticmethod
    def system_message(content):
        return Message("system", content)
    
    @staticmethod
    def user_message(content):
        return Message("user", content)
    
    @staticmethod
    def assistant_message(content):
        return Message("assistant", content)
    
    @staticmethod
    def tool_message(content, tool_name=None, tool_input=None):
        msg = Message("tool", content)
        msg.tool_name = tool_name
        msg.tool_input = tool_input
        return msg


class BaseAgent:
    """基础代理类，提供状态管理和执行功能"""
    
    def __init__(self, name="base_agent", description="基础代理"):
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.messages = []
        self.max_steps = 10
    
    def add_message(self, message):
        """添加消息到历史记录"""
        self.messages.append(message)
    
    async def run(self, prompt: str) -> str:
        """运行代理处理用户请求"""
        self.state = AgentState.RUNNING
        self.messages = [Message.user_message(prompt)]
        
        step_count = 0
        result = ""
        
        try:
            while step_count < self.max_steps and self.state == AgentState.RUNNING:
                step_count += 1
                print(f"步骤 {step_count}: 思考中...")
                
                # 执行一次思考-行动循环
                continue_loop = await self.think()
                if not continue_loop:
                    break
                
                # 处理最终结果
                last_messages = self.messages[-3:] if len(self.messages) > 3 else self.messages
                result = "\n".join([msg.content for msg in last_messages if msg.role == "assistant"])
            
            self.state = AgentState.FINISHED
            return result or "任务已完成，但没有生成结果。"
        
        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = f"运行过程中出错: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def think(self) -> bool:
        """思考过程，需要子类实现"""
        raise NotImplementedError("子类需要实现think方法")


class ToolCall:
    """工具调用的简单表示"""
    
    def __init__(self, function=None):
        self.function = function or {}


class ToolCallAgent(BaseAgent):
    """处理工具调用的代理"""
    
    def __init__(
        self, 
        name="toolcall", 
        description="工具调用代理",
        system_prompt="你是一个能够使用各种工具的AI助手。",
        next_step_prompt="根据用户的需求，选择合适的工具来解决问题。"
    ):
        super().__init__(name, description)
        self.system_prompt = system_prompt
        self.next_step_prompt = next_step_prompt
        self.available_tools = ToolCollection()
        self.tool_calls = []
        self.special_tool_names = ["terminate"]  # 特殊工具，执行后会终止代理
        # LLM 属性将在 Manus 类中设置
        self.llm = None
    
    async def think(self) -> bool:
        """处理当前状态并使用工具决定下一步行动"""
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.add_message(user_msg)
        
        # 如果存在LLM客户端，则使用它获取响应
        if self.llm:
            # 调用LLM获取响应和工具调用
            response = await self.llm.ask_tool(
                messages=self.messages,
                system_msgs=[Message.system_message(self.system_prompt)] if self.system_prompt else None,
                tools=self.available_tools.to_params(),
                tool_choice="auto"
            )
            
            print(f"✨ {self.name}的思考: {response.content}")
            
            # 处理工具调用
            self.tool_calls = []
            if response.tool_calls:
                print(f"🛠️ {self.name}选择了 {len(response.tool_calls)} 个工具")
                
                for tool_call_data in response.tool_calls:
                    tool_call = ToolCall(tool_call_data["function"])
                    self.tool_calls.append(tool_call)
                    
                    # 执行工具
                    await self.execute_tool(tool_call)
            
            # 如果状态已经变为FINISHED，说明执行了终止工具，应该停止循环
            if self.state == AgentState.FINISHED:
                return False
            
            # 添加助手消息
            self.add_message(Message.assistant_message(response.content))
            
            return True
        else:
            # 模拟LLM响应，仅作演示
            print("✨ 思考: 分析用户请求并选择合适的工具...")
            
            # 模拟工具选择逻辑
            self.tool_calls = [
                ToolCall({"name": "python_execute", "arguments": json.dumps({"code": "print('Hello world')"})}),
            ]
            
            # 执行选定的工具
            for tool_call in self.tool_calls:
                await self.execute_tool(tool_call)
            
            # 如果状态已经变为FINISHED，说明执行了终止工具，应该停止循环
            if self.state == AgentState.FINISHED:
                return False
            
            # 模拟LLM响应
            self.add_message(Message.assistant_message("工具执行完成，结果已返回。"))
            
            return True
    
    async def execute_tool(self, command: ToolCall) -> str:
        """执行单个工具调用"""
        if not command or not command.function or not command.function.get("name"):
            return "错误: 无效的命令格式"
        
        name = command.function.get("name")
        if name not in self.available_tools.tool_map:
            return f"错误: 未知工具 '{name}'"
        
        try:
            # 解析参数
            args = json.loads(command.function.get("arguments") or "{}")
            
            # 执行工具
            print(f"🔧 激活工具: '{name}'...")
            result = await self.available_tools.execute(name=name, tool_input=args)
            
            # 格式化结果用于显示
            observation = (
                f"工具 `{name}` 的执行结果:\n{str(result)}"
                if result
                else f"工具 `{name}` 执行完成，没有输出"
            )
            
            # 添加工具消息到历史
            self.add_message(Message.tool_message(observation, name, args))
            
            # 处理特殊工具，如终止
            await self._handle_special_tool(name=name, result=result)
            
            return observation
        except json.JSONDecodeError:
            error_msg = f"解析 {name} 的参数时出错: 无效的JSON格式"
            print(f"📝 参数解析错误: '{name}' 的参数不是有效的JSON")
            return f"错误: {error_msg}"
        except Exception as e:
            error_msg = f"⚠️ 工具 '{name}' 遇到问题: {str(e)}"
            print(error_msg)
            return f"错误: {error_msg}"
    
    async def _handle_special_tool(self, name: str, result: any) -> None:
        """处理特殊工具执行和状态变更"""
        if not self._is_special_tool(name):
            return
        
        # 设置代理状态为完成
        print(f"🏁 特殊工具 '{name}' 已完成任务!")
        self.state = AgentState.FINISHED
    
    def _is_special_tool(self, name: str) -> bool:
        """检查工具名称是否在特殊工具列表中"""
        return name.lower() in [n.lower() for n in self.special_tool_names] 