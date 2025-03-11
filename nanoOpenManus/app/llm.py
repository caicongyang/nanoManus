import json
import os
from typing import Dict, List, Optional

import httpx

from nanoOpenManus.app.agent import Message


class LLM:
    """LLM 客户端，负责与LLM API通信"""
    
    def __init__(self, api_key=None, model="gpt-4o", base_url="https://api.openai.com/v1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API 密钥未提供，请设置 OPENAI_API_KEY 环境变量或在初始化时提供")
        
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def ask(self, messages, system_msgs=None):
        """发送消息到 LLM 并获取响应"""
        all_messages = []
        
        # 添加系统消息
        if system_msgs:
            for msg in system_msgs:
                all_messages.append({"role": msg.role, "content": msg.content})
        
        # 添加对话历史
        for msg in messages:
            message_dict = {"role": msg.role, "content": msg.content}
            
            # 处理工具消息
            if msg.role == "tool" and hasattr(msg, "tool_name"):
                message_dict = {
                    "role": "tool",
                    "tool_call_id": "call_" + msg.tool_name,
                    "content": msg.content,
                }
            
            all_messages.append(message_dict)
        
        # 发送请求
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={
                "model": self.model,
                "messages": all_messages,
                "temperature": 0.0,
            },
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 解析响应
        content = result["choices"][0]["message"]["content"]
        return content
    
    async def ask_tool(self, messages, system_msgs=None, tools=None, tool_choice="auto"):
        """发送消息到 LLM 并获取可能包含工具调用的响应"""
        all_messages = []
        
        # 添加系统消息
        if system_msgs:
            for msg in system_msgs:
                all_messages.append({"role": msg.role, "content": msg.content})
        
        # 添加对话历史
        for msg in messages:
            message_dict = {"role": msg.role, "content": msg.content}
            
            # 处理工具消息
            if msg.role == "tool" and hasattr(msg, "tool_name"):
                message_dict = {
                    "role": "tool",
                    "tool_call_id": "call_" + msg.tool_name,
                    "content": msg.content,
                }
            
            all_messages.append(message_dict)
        
        # 准备请求数据
        request_data = {
            "model": self.model,
            "messages": all_messages,
            "temperature": 0.0,
        }
        
        # 添加工具定义
        if tools:
            request_data["tools"] = tools
            
            if tool_choice == "required":
                request_data["tool_choice"] = {"type": "function"}
            elif tool_choice == "none":
                request_data["tool_choice"] = "none"
        
        # 发送请求
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json=request_data,
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 解析响应
        message = result["choices"][0]["message"]
        content = message.get("content", "")
        
        # 解析工具调用
        tool_calls = []
        if "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                if tool_call["type"] == "function":
                    function = tool_call["function"]
                    tool_calls.append({
                        "function": {
                            "name": function["name"],
                            "arguments": function["arguments"],
                        }
                    })
        
        # 创建响应对象
        class Response:
            def __init__(self, content, tool_calls):
                self.content = content
                self.tool_calls = tool_calls
        
        return Response(content, tool_calls) 