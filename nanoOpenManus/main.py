import sys
import os

# --- Start of code to fix Python path ---
# This ensures that the project root directory (containing the 'nanoOpenManus' package)
# is on the Python path, allowing imports like 'from nanoOpenManus.app...'
_current_script_path = os.path.abspath(__file__)
_current_script_dir = os.path.dirname(_current_script_path)
_project_root = os.path.dirname(_current_script_dir) 

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# --- End of code to fix Python path ---

import argparse
import asyncio

# 导入Docker版本的Manus
from nanoOpenManus.app.docker_manus import DockerManus
# 保留原始Manus作为后备选项
from nanoOpenManus.app.manus import Manus


async def main():
    """
    NanoOpenManus 的主入口函数
    
    创建一个Manus代理实例并处理用户输入
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='NanoOpenManus - 一个简化版的OpenManus实现')
    parser.add_argument('--api-key',default=os.getenv('DEEPSEEK_API_KEY'), help='deepseek-chat密钥')
    parser.add_argument('--model', default='deepseek-chat', help='LLM模型名称 (默认: deepseek-chat)')
    parser.add_argument('--base-url', default='https://api.deepseek.com', 
                        help='API基础URL (默认: https://api.deepseek.com)')
    parser.add_argument('--max-steps', type=int, default=15, help='最大执行步骤数 (默认: 15)')
    # 添加Docker相关选项
    parser.add_argument('--use-docker', action='store_true',  default=True,
                        help='在Docker容器中执行工具 (默认: 开启)')
    parser.add_argument('--container-name', default='nanomanus-sandbox',
                        help='Docker容器名称 (默认: nanomanus-sandbox)')
    parser.add_argument('--local', action='store_true',
                        help='使用本地环境执行工具，不使用Docker')
    args = parser.parse_args()
    
    # 创建代理实例
    if args.local or not args.use_docker:
        print("🖥️ 使用本地环境执行工具")
        agent = Manus(
            max_steps=args.max_steps,
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url
        )
    else:
        print(f"🐳 使用Docker容器 '{args.container_name}' 执行工具")
        agent = DockerManus(
            max_steps=args.max_steps,
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url,
            container_name=args.container_name
        )
    
    print("🚀 NanoOpenManus 已启动!")
    print("📝 这是一个简化版的OpenManus实现，专为学习和理解AI代理设计。")
    print("🔧 可用工具: python_execute, file_saver, terminate")
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