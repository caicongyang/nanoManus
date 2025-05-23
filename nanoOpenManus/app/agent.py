import json  
from enum import Enum  
from typing import Dict, List, Optional  

from nanoOpenManus.app.tools.base import ToolResult 
from nanoOpenManus.app.tools.tool_collection import ToolCollection  

class AgentState(str, Enum):  # 定义一个名为AgentState的类，它继承自str和Enum，表示代理可能处于的各种状态
    """代理的状态"""  # 类的文档字符串，解释这个类的用途
    IDLE = "idle"  # 定义IDLE状态，表示代理空闲
    RUNNING = "running"  # 定义RUNNING状态，表示代理正在处理任务
    FINISHED = "finished"  # 定义FINISHED状态，表示代理已完成任务
    ERROR = "error"  # 定义ERROR状态，表示代理在执行过程中遇到错误


class Message:  # 定义一个名为Message的类，用于封装对话中的消息
    """简化的消息类，用于代理与LLM之间的通信"""  # 类的文档字符串
    
    def __init__(self, role, content, tool_call_id: Optional[str] = None, tool_calls: Optional[List[Dict]] = None):  # Message类的构造函数（初始化方法）
        # 参数:
        #   role (str): 消息发送者的角色 (例如: "user", "assistant", "tool", "system")
        #   content (any): 消息的具体内容
        #   tool_call_id (Optional[str]): 对于角色为 "tool" 的消息，这个ID用于将其与特定的工具调用请求关联起来。默认为None。
        #   tool_calls (Optional[List[Dict]]): 对于角色为 "assistant" 且包含工具调用的消息，这里存储LLM返回的工具调用请求列表。默认为None。
        
        self.role = role  # 将传入的role参数赋值给实例的role属性
        self.content = content  # 将传入的content参数赋值给实例的content属性
        self.tool_call_id = tool_call_id  # 将传入的tool_call_id参数赋值给实例的tool_call_id属性
        self.tool_calls = tool_calls      # 将传入的tool_calls参数赋值给实例的tool_calls属性
    
    @staticmethod  # 这是一个静态方法，意味着它可以不创建类的实例而被调用
    def system_message(content):  # 定义一个创建系统消息的静态方法
        # 参数:
        #   content (str): 系统消息的内容
        return Message("system", content)  # 返回一个新的Message对象，角色为"system"，内容为传入的content
    
    @staticmethod  # 静态方法
    def user_message(content):  # 定义一个创建用户消息的静态方法
        # 参数:
        #   content (str): 用户消息的内容
        return Message("user", content)  # 返回一个新的Message对象，角色为"user"，内容为传入的content
    
    @staticmethod  # 静态方法
    def assistant_message(content, tool_calls: Optional[List[Dict]] = None):  # 定义一个创建助手消息的静态方法
        # 参数:
        #   content (str): 助手消息的内容
        #   tool_calls (Optional[List[Dict]]): 可选的工具调用列表。默认为None。
        return Message("assistant", content, tool_calls=tool_calls)  # 返回一个新的Message对象，角色为"assistant"，内容和工具调用信息如传入参数所示
    
    @staticmethod  # 静态方法
    def tool_message(content, tool_call_id: str):  # 定义一个创建工具消息的静态方法
        # 参数:
        #   content (str): 工具执行结果的内容
        #   tool_call_id (str): 与此工具结果对应的工具调用ID
        return Message("tool", content, tool_call_id=tool_call_id)  # 返回一个新的Message对象，角色为"tool"，内容和关联的tool_call_id如传入参数所示


class BaseAgent:  # 定义一个名为BaseAgent的基础代理类
    """基础代理类，提供状态管理和执行功能"""  # 类的文档字符串
    
    def __init__(self, name="base_agent", description="基础代理"):  # BaseAgent类的构造函数
        # 参数:
        #   name (str): 代理的名称，默认为"base_agent"
        #   description (str): 代理的描述，默认为"基础代理"
        
        self.name = name  # 将传入的name赋值给实例的name属性
        self.description = description  # 将传入的description赋值给实例的description属性
        self.state = AgentState.IDLE  # 初始化代理状态为IDLE (空闲)
        self.messages = []  # 初始化一个空列表，用于存储对话消息历史
        self.max_steps = 10  # 设置代理在一个任务中最大允许的思考-行动循环次数，默认为10
    
    def add_message(self, message):  # 定义一个将消息添加到历史记录的方法
        """添加消息到历史记录"""  # 方法的文档字符串
        # 参数:
        #   message (Message): 要添加的Message对象
        self.messages.append(message)  # 将传入的message对象追加到self.messages列表的末尾
    
    async def run(self, prompt: str) -> str:  # 定义一个异步方法run，用于启动代理处理用户请求
        # 参数:
        #   prompt (str): 用户的初始请求字符串
        # 返回:
        #   str: 代理执行完毕后的最终结果字符串
        """运行代理处理用户请求"""  # 方法的文档字符串
        
        self.state = AgentState.RUNNING  # 将代理状态设置为RUNNING (运行中)
        self.messages = [Message.user_message(prompt)]  # 初始化消息历史列表，并添加用户的第一条请求作为第一条消息
        
        step_count = 0  # 初始化步骤计数器为0
        result = ""  # 初始化最终结果字符串为空
        
        try:  # 开始一个try块，用于捕获执行过程中可能发生的异常
            while step_count < self.max_steps and self.state == AgentState.RUNNING:  # 当步骤数未达到上限且代理仍在运行时，循环执行
                step_count += 1  # 步骤计数器加1
                print(f"步骤 {step_count}: 思考中...")  # 打印当前步骤和状态
                
                # 执行一次思考-行动循环
                continue_loop = await self.think()  # 调用self.think()方法进行一次思考和行动，并等待其完成。think方法决定是否需要继续循环。
                if not continue_loop:  # 如果think方法返回False（或任何布尔值为False的值）
                    break  # 跳出while循环，结束代理的执行
                
                # 处理最终结果 - 查找最后一条没有工具调用的助手消息内容
                # 从消息历史的末尾开始反向查找
                final_assistant_messages = [ \
                    msg.content for msg in reversed(self.messages) \
                    # 筛选条件：消息角色是"assistant"，没有工具调用(msg.tool_calls为空或None)，并且消息内容不为None
                    if msg.role == "assistant" and not msg.tool_calls and msg.content is not None\
                ]
                if final_assistant_messages:  # 如果找到了这样的助手消息
                    result = final_assistant_messages[0]  # 将第一条符合条件的（即最新的）消息内容作为结果
                else: # 如果没有找到，或者作为备选方案，获取所有助手消息的内容
                    assistant_contents = [msg.content for msg in self.messages if msg.role == "assistant" and msg.content is not None]
                    result = assistant_contents[-1] if assistant_contents else "" # 如果存在助手消息内容，则取最后一条；否则结果仍为空字符串
            
            self.state = AgentState.FINISHED  # 当循环结束（正常完成或提前中断），将代理状态设置为FINISHED (已完成)
            # 如果result仍然是空字符串（意味着循环结束前没有找到合适的助手消息），则返回默认的完成信息
            return result or "任务已完成"  # 返回最终结果，如果结果为空，则返回"任务已完成"
        
        except Exception as e:  # 如果在try块的执行过程中捕获到任何异常
            self.state = AgentState.ERROR  # 将代理状态设置为ERROR (错误)
            error_msg = f"运行过程中出错: {str(e)}"  # 构建错误信息字符串
            print(error_msg)  # 打印错误信息
            return error_msg  # 返回错误信息作为执行结果
    
    async def think(self) -> bool:  # 定义一个异步方法think，表示代理的思考和行动逻辑
        # 返回:
        #   bool: True表示代理应该继续执行下一个循环，False表示代理应该停止
        """思考过程，需要子类实现"""  # 方法的文档字符串
        raise NotImplementedError("子类需要实现think方法")  # 抛出NotImplementedError，强制子类必须重写此方法


class ToolCall:  # 定义一个名为ToolCall的类，用于简单表示一个工具调用请求
    """工具调用的简单表示"""  # 类的文档字符串
    
    def __init__(self, id: str, function: Dict):  # ToolCall类的构造函数
        # 参数:
        #   id (str): 从助手（LLM）返回的工具调用ID (tool_call_id)
        #   function (Dict): 包含工具名称和参数的字典
        
        self.id = id  # 将传入的id赋值给实例的id属性
        self.function = function or {}  # 将传入的function赋值给实例的function属性。如果function为None，则赋值为空字典。


class ToolCallAgent(BaseAgent):  # 定义一个名为ToolCallAgent的类，它继承自BaseAgent，专门处理工具调用
    """处理工具调用的代理"""  # 类的文档字符串
    
    def __init__(  # ToolCallAgent类的构造函数
        self, 
        name="toolcall",  # 代理名称，默认为"toolcall"
        description="工具调用代理",  # 代理描述，默认为"工具调用代理"
        system_prompt="你是一个能够使用各种工具的AI助手。",  # 系统提示，用于指导LLM的行为
        next_step_prompt="根据用户的需求，选择合适的工具来解决问题。"  # 下一步提示，可能用于引导LLM的初步思考
    ):
        super().__init__(name, description)  # 调用父类BaseAgent的构造函数，传递name和description
        self.system_prompt = system_prompt  # 将传入的system_prompt赋值给实例的system_prompt属性
        self.next_step_prompt = next_step_prompt  # 将传入的next_step_prompt赋值给实例的next_step_prompt属性
        self.available_tools = ToolCollection()  # 初始化一个ToolCollection实例，用于管理此代理可用的工具
        self.special_tool_names = ["terminate"]  # 定义一个特殊工具名称列表，目前只有"terminate"（终止工具）
                                                # 特殊工具执行后可能会改变代理的状态，例如终止代理
        self.llm = None # 初始化llm属性为None。这个属性将在具体的Manus类（或其他子类）中被设置为一个LLM客户端实例。
    
    async def think(self) -> bool:  # 重写父类的think方法，实现工具调用代理的思考逻辑
        """处理当前状态并使用工具决定下一步行动"""  # 方法的文档字符串
        
        # 关于next_step_prompt的逻辑：通常这个提示只用于对话的第一轮，或者在需要重新引导对话时。
        # 这里的逻辑是：如果存在next_step_prompt，并且当前消息历史中只有一条用户消息（即对话刚开始），
        # 那么将next_step_prompt作为一条新的用户消息添加到历史中。
        if self.next_step_prompt and len(self.messages) == 1 and self.messages[0].role == 'user':
             self.add_message(Message.user_message(self.next_step_prompt)) # 添加引导性用户消息

        if self.llm:  # 检查self.llm是否已经被设置（即是否存在LLM客户端）
            # 调用LLM的ask_tool方法，发送当前消息历史、系统提示和可用工具列表
            llm_response = await self.llm.ask_tool(  # 等待LLM的响应
                messages=self.messages,  # 传入当前完整的消息历史
                system_msgs=[Message.system_message(self.system_prompt)] if self.system_prompt else None,  # 如果有系统提示，则包装成列表传入
                tools=self.available_tools.to_params(),  # 获取可用工具的参数描述，并传入
                tool_choice="auto"  # 让LLM自动决定是否以及调用哪个工具
            )
            
            assistant_content = llm_response.content  # 从LLM响应中获取文本内容部分
            pending_tool_calls = llm_response.tool_calls  # 从LLM响应中获取请求调用的工具列表

            # 将助手的响应（可能包含文本内容、工具调用请求，或两者都有）添加到消息历史中
            self.add_message(Message.assistant_message(assistant_content, tool_calls=pending_tool_calls))

            if assistant_content:  # 如果LLM的响应中包含文本内容
                print(f"✨ {self.name}的思考: {assistant_content}")  # 打印助手的思考文本

            if pending_tool_calls:  # 如果LLM的响应中包含工具调用请求
                print(f"🛠️ {self.name}请求执行 {len(pending_tool_calls)} 个工具")  # 打印请求执行的工具数量
                for tc_data in pending_tool_calls:  # 遍历每一个工具调用请求数据
                    # 从llm.ask_tool返回的tc_data已经是包含id和function的正确结构
                    tool_call_to_execute = ToolCall(id=tc_data['id'], function=tc_data['function'])  # 创建ToolCall对象
                    await self.execute_tool(tool_call_to_execute)  # 调用execute_tool方法执行该工具调用，并等待完成
                    
                    # 如果某个工具（例如terminate工具）的执行改变了代理的状态（比如变为FINISHED或ERROR）
                    if self.state != AgentState.RUNNING:  # 检查代理状态是否仍然是RUNNING
                        return False # 如果状态不再是RUNNING，则停止循环，不再处理后续的工具调用或思考
                return True # 如果所有请求的工具都已执行（或尝试执行）完毕，并且代理状态仍然是RUNNING，则继续循环
            else:  # 如果LLM的响应中没有工具调用请求
                # 这意味着助手直接给出了答案，或者任务已经完成。
                # 如果助手通过其文本内容隐式地指示任务结束（而不是通过调用terminate工具），
                # 这种逻辑需要通过解析助手消息内容或某种特殊信号来处理。
                # 目前的逻辑是：如果没有工具调用，则假定LLM提供了最终回复或需要新的用户输入。
                return False # 停止循环，因为没有工具需要调用。
        
        else: # 如果self.llm为None（即没有配置真实的LLM API密钥，处于模拟LLM模式）
            print("✨ (模拟) 思考: 分析用户请求并选择合适的工具...")  # 打印模拟思考的提示
            # 简化的模拟逻辑
            if any(tool_msg.role == "tool" for tool_msg in self.messages): # 检查消息历史中是否已有工具执行结果
                # 如果上一步有工具调用，则模拟一个助手对工具结果的总结性回复
                self.add_message(Message.assistant_message("(模拟) 工具执行完成，这是我的总结。"))
                return False # 结束循环
            else: # 如果上一步没有工具调用
                # 模拟一个对python_execute工具的调用请求
                simulated_tool_call_id = "call_sim_python_123"  # 模拟一个工具调用ID
                simulated_tool_calls = [{  # 模拟一个工具调用列表
                    "id": simulated_tool_call_id,  # 工具调用ID
                    "type": "function",  # 工具类型为函数
                    "function": {"name": "python_execute", "arguments": json.dumps({"code": "print('Hello from simulated Docker!')"})} # 工具名称和参数
                }]
                # 添加一个模拟的助手消息，该消息不包含文本内容，只包含工具调用请求
                self.add_message(Message.assistant_message(content=None, tool_calls=simulated_tool_calls))
                print(f"🛠️ (模拟) {self.name}请求执行 1 个工具") # 打印模拟请求执行工具的提示
                # 使用模拟的工具调用ID和函数定义来创建一个ToolCall对象，并执行它
                await self.execute_tool(ToolCall(id=simulated_tool_call_id, function=simulated_tool_calls[0]['function']))
                return True # 继续循环，因为模拟调用了工具

    async def execute_tool(self, tool_to_execute: ToolCall) -> None:  # 定义异步方法execute_tool，用于执行单个工具调用
        # 参数:
        #   tool_to_execute (ToolCall): 要执行的ToolCall对象
        # 返回:
        #   None: 此方法不直接返回结果，而是将工具执行的结果（或错误）作为新的Message对象添加到消息历史中
        """执行单个工具调用并将结果添加到消息历史""" # 方法的文档字符串
        
        tool_call_id = tool_to_execute.id  # 从ToolCall对象中获取工具调用ID
        tool_name = tool_to_execute.function.get("name")  # 从ToolCall对象的function字典中获取工具名称
        
        if not tool_name:  # 如果工具名称为空（未提供）
            observation = "错误: 工具调用中缺少工具名称"  # 设置观察结果为错误信息
            print(observation)  # 打印错误信息
            self.add_message(Message.tool_message(observation, tool_call_id))  # 将错误信息作为工具消息添加到历史，并关联tool_call_id
            return  # 提前返回，不执行后续逻辑

        if tool_name not in self.available_tools.tool_map:  # 如果请求的工具名称不在可用工具列表中
            observation = f"错误: 未知工具 '{tool_name}'"  # 设置观察结果为错误信息
            print(observation)  # 打印错误信息
            self.add_message(Message.tool_message(observation, tool_call_id))  # 将错误信息作为工具消息添加到历史
            return  # 提前返回

        try:  # 开始一个try块，用于捕获工具执行和参数解析过程中可能发生的异常
            arguments_str = tool_to_execute.function.get("arguments", "{}")  # 获取工具参数的字符串形式，如果不存在则默认为空JSON对象"{}"
            args = json.loads(arguments_str)  # 将参数字符串解析为Python字典
            
            print(f"🔧 激活工具: '{tool_name}' (ID: {tool_call_id}) 参数: {args}")  # 打印激活工具的日志信息
            # 调用ToolCollection的execute方法来实际执行工具，并等待其完成
            # tool_input参数需要的是一个字典
            tool_result: ToolResult = await self.available_tools.execute(name=tool_name, tool_input=args)
            
            if tool_result.error:  # 如果工具执行结果中包含错误信息
                observation = f"工具 `{tool_name}` (ID: {tool_call_id}) 执行出错:\\n{str(tool_result.error)}"  # 构建包含错误详情的观察结果字符串
            else:  # 如果工具执行没有错误
                observation = (  # 构建观察结果字符串
                    # 如果tool_result.output不为None，则使用其内容
                    f"工具 `{tool_name}` (ID: {tool_call_id}) 的执行结果:\\n{str(tool_result.output)}"
                    if tool_result.output is not None 
                    # 否则，表示工具执行完成但没有输出
                    else f"工具 `{tool_name}` (ID: {tool_call_id}) 执行完成，没有输出"
                )
            
            print(f"📝 工具结果 ({tool_name}): {observation}")  # 打印工具执行的最终观察结果
            self.add_message(Message.tool_message(observation, tool_call_id))  # 将观察结果作为工具消息添加到历史，并关联tool_call_id
            
            # 调用_handle_special_tool处理可能的特殊工具逻辑（如terminate）
            await self._handle_special_tool(name=tool_name, result=tool_result)
            
        except json.JSONDecodeError:  # 如果在解析工具参数字符串时发生JSON解码错误
            error_msg = f"解析工具 '{tool_name}' (ID: {tool_call_id}) 的参数时出错: 无效的JSON格式 - '{arguments_str}'"  # 构建错误信息
            print(error_msg)  # 打印错误信息
            self.add_message(Message.tool_message(error_msg, tool_call_id))  # 将错误信息作为工具消息添加到历史
        except Exception as e:  # 如果在工具执行过程中捕获到任何其他未预料的异常
            error_msg = f"⚠️ 工具 '{tool_name}' (ID: {tool_call_id}) 遇到问题: {str(e)}"  # 构建包含异常信息的错误提示
            print(error_msg)  # 打印错误提示
            self.add_message(Message.tool_message(error_msg, tool_call_id))  # 将错误提示作为工具消息添加到历史
    
    async def _handle_special_tool(self, name: str, result: ToolResult) -> None:  # 定义异步方法_handle_special_tool，用于处理特殊工具的后效
        # 参数:
        #   name (str): 被执行的工具名称
        #   result (ToolResult): 工具的执行结果对象
        """处理特殊工具执行和状态变更"""  # 方法的文档字符串
        
        if not self._is_special_tool(name):  # 调用_is_special_tool检查该工具是否为特殊工具
            return  # 如果不是特殊工具，则直接返回，不执行任何操作
        
        # 如果工具是"terminate"（不区分大小写），并且执行没有出错
        if name.lower() == "terminate" and not result.error:
             print(f"🏁 特殊工具 '{name}' 已完成任务! 代理将终止。")  # 打印终止信息
             self.state = AgentState.FINISHED  # 将代理状态设置为FINISHED (已完成)
        # Potentially other special tools could be handled here  # 注释：将来可能会在这里处理其他特殊工具的逻辑
    
    def _is_special_tool(self, name: str) -> bool:  # 定义方法_is_special_tool，检查给定名称的工具是否为特殊工具
        # 参数:
        #   name (str): 要检查的工具名称
        # 返回:
        #   bool: 如果是特殊工具则返回True，否则返回False
        """检查工具名称是否在特殊工具列表中"""  # 方法的文档字符串
        # 将输入的工具名称转换为小写，并检查它是否存在于self.special_tool_names列表中（列表中的名称也转换为小写进行比较，以实现不区分大小写的匹配）
        return name.lower() in [n.lower() for n in self.special_tool_names] 