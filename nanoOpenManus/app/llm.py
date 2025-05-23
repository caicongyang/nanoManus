import json
import os
from typing import Dict, List, Optional

import httpx

from nanoOpenManus.app.agent import Message


class LLMResponse:
    """标准化的LLM响应对象，包含内容和工具调用"""
    def __init__(self, content: Optional[str], tool_calls: Optional[List[Dict]]):
        self.content = content
        self.tool_calls = tool_calls if tool_calls is not None else []


class LLM:
    """LLM 客户端，负责与LLM API通信"""
    
    def __init__(self, api_key=None, model="deepseek-chat", base_url="https://api.deepseek.com"):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API 密钥未提供，请设置 DEEPSEEK_API_KEY 环境变量或在初始化时提供")
        
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _convert_messages_to_api_format(self, messages: List[Message]) -> List[Dict]:
        """将内部Message对象列表转换为API所需的字典列表格式"""
        api_messages = []
        for msg in messages:
            if msg.role == "system":
                api_messages.append({"role": "system", "content": msg.content})
            elif msg.role == "user":
                api_messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                entry = {"role": "assistant"}
                if msg.content:
                    entry["content"] = msg.content
                if msg.tool_calls: # msg.tool_calls should be a list of dicts from the API
                    entry["tool_calls"] = msg.tool_calls
                # An assistant message should have content or tool_calls or both. If neither, it might be an issue.
                if "content" not in entry and "tool_calls" not in entry:
                    entry["content"] = "" # Ensure content is at least an empty string if no tool_calls
                api_messages.append(entry)
            elif msg.role == "tool":
                if msg.tool_call_id:
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": msg.tool_call_id,
                        "content": msg.content
                    })
                else:
                    # This case should ideally not happen if tool_call_ids are managed correctly
                    print(f"警告: 工具消息缺少 tool_call_id: {msg.content}")
                    # Fallback: send as a generic content string, though this might not be what the API expects
                    # api_messages.append({"role": "user", "content": f"Tool Output: {msg.content}"})
        return api_messages

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
    
    async def ask_tool(self, messages: List[Message], system_msgs: Optional[List[Message]] = None, tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = "auto"):
        """发送消息到 LLM 并获取可能包含工具调用的响应"""
        api_request_messages = []
        if system_msgs:
            api_request_messages.extend(self._convert_messages_to_api_format(system_msgs))
        api_request_messages.extend(self._convert_messages_to_api_format(messages))
        
        request_data = {
            "model": self.model,
            "messages": api_request_messages,
            "temperature": 0.0, # Lower temperature for more deterministic tool use
        }
        
        if tools:
            request_data["tools"] = tools
            if tool_choice: # DeepSeek might expect tool_choice only if tools are present
                # OpenAI format for forcing a specific function or any function:
                # tool_choice = {"type": "function", "function": {"name": "my_function"}}
                # tool_choice = "required" (to force any function from the list)
                # tool_choice = "auto" (default)
                # tool_choice = "none"
                if tool_choice == "required": # If you want to force a tool call
                    request_data["tool_choice"] = "required" # Or {"type": "function"} if API expects object
                elif tool_choice != "auto": # "none" or a specific function call object
                    request_data["tool_choice"] = tool_choice
        
        # Debug: Print the request payload
        # print(f"--- Request to LLM API ---")
        # print(json.dumps(request_data, indent=2, ensure_ascii=False))
        # print(f"---------------------------")

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json=request_data,
            )
            
            response.raise_for_status() # Will raise HTTPStatusError for 4xx/5xx responses
            result = response.json()
            
            # Debug: Print the raw API response
            # print(f"--- Response from LLM API ---")
            # print(json.dumps(result, indent=2, ensure_ascii=False))
            # print(f"-----------------------------")
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response content: {e.response.text}")
            # Return an LLMResponse indicating error or re-raise
            # For simplicity, let's return an empty response that the agent can check
            return LLMResponse(content=f"API Error: {e.response.status_code} - {e.response.text}", tool_calls=[])
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            return LLMResponse(content=f"Request Error: {str(e)}", tool_calls=[])
        except Exception as e: # Catch any other unexpected errors during request or parsing
            print(f"An unexpected error occurred: {str(e)}")
            return LLMResponse(content=f"Unexpected Error: {str(e)}", tool_calls=[])

        api_message = result.get("choices",[{}])[0].get("message", {})
        content = api_message.get("content") # Content can be None if only tool_calls are present
        
        # API typically returns tool_calls as a list of objects, each with an id, type (function), and function (name, arguments)
        raw_tool_calls = api_message.get("tool_calls") 
        parsed_tool_calls = []
        if raw_tool_calls:
            for tc in raw_tool_calls:
                if tc.get("type") == "function":
                    parsed_tool_calls.append({
                        "id": tc.get("id"),
                        "type": "function", # Keep type for consistency if needed later
                        "function": tc.get("function") # This is {name: "...", arguments: "..."}
                    })
        
        return LLMResponse(content=content, tool_calls=parsed_tool_calls) 