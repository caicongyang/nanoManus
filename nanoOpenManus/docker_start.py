#!/usr/bin/env python3
"""
Docker沙箱模式启动脚本

这个脚本是nanoOpenManus的快捷启动方式，强制使用Docker沙箱模式。
它会自动检查Docker容器是否已经准备好，并执行必要的准备工作。
"""

import os
import asyncio
import argparse

# 导入Docker版本的Manus
from nanoOpenManus.app.docker_manus import DockerManus


async def main():
    """
    Docker模式的NanoOpenManus主入口函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='NanoOpenManus - Docker沙箱模式')
    parser.add_argument('--api-key', help='OpenAI API密钥')
    parser.add_argument('--model', default='gpt-4o', help='LLM模型名称 (默认: gpt-4o)')
    parser.add_argument('--base-url', default='https://api.openai.com/v1', 
                        help='API基础URL (默认: https://api.openai.com/v1)')
    parser.add_argument('--max-steps', type=int, default=15, help='最大执行步骤数 (默认: 15)')
    parser.add_argument('--container-name', default='nanomanus-sandbox',
                        help='Docker容器名称 (默认: nanomanus-sandbox)')
    args = parser.parse_args()
    
    # 创建DockerManus代理实例
    print(f"🐳 初始化Docker沙箱模式...")
    agent = DockerManus(
        max_steps=args.max_steps,
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url,
        container_name=args.container_name
    )
    
    print("🚀 NanoOpenManus Docker沙箱模式已启动!")
    print("📝 这是一个简化版的OpenManus实现，专为学习和理解AI代理设计。")
    print("🔧 可用工具: python_execute, file_saver, environment_check, terminate")
    print("⌨️  输入'exit'或'quit'退出程序\n")
    
    # 主循环
    while True:
        try:
            # 获取用户输入
            prompt = input("🙋 请输入您的请求: ")
            
            # 检查是否退出
            if prompt.lower() in ["exit", "quit"]:
                print("👋 再见!")
                break
            
            # 跳过空输入
            if not prompt.strip():
                print("⚠️ 跳过空输入")
                continue
            
            # 处理请求
            print("⏳ 正在处理您的请求...")
            result = await agent.run(prompt)
            
            # 显示结果
            print(f"\n✅ 结果:\n{result}\n")
            
        except KeyboardInterrupt:
            print("\n👋 程序被用户中断，再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 