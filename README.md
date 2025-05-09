# nanoManus
[Manus is a famous general AI agent that bridges minds and actions](https://manus.im/)  
this project is a  simple implementation of OpenManus for beginner learners

## Project Structure

### `/doc` Directory
The `doc` directory contains technical analysis documents of OpenManus, including:
- [`architecture.md`](doc/architecture.md) - Architectural overview of OpenManus
- [`system_design.md`](doc/system_design.md) - Detailed system design documentation
- [`api_reference.md`](doc/api_reference.md) - API reference documentation
- [`tools_reference.md`](doc/tools_reference.md) - Tools reference and usage guide

### `/nanoOpenManus` Directory
`nanoOpenManus` is a minimal implementation of OpenManus designed for beginners. It provides a simplified version of the original project to help learners understand the core concepts and functionality.

## About This Project
This project aims to provide a simplified implementation of Manus with educational purposes. It is intended for those who want to learn about AI agent frameworks and understand how systems like OpenManus work.

### Implemented Features
- **基础代理框架**: 实现了完整的AI代理系统基础架构，包括代理、工具集合和工具调用机制
- **核心工具**: 提供了多种基础工具，包括Python代码执行、文件保存、环境检查和终止工具
- **Docker沙箱环境**: 实现了将工具执行隔离在Docker容器中的安全机制，保护主机系统
- **LLM集成**: 支持与OpenAI GPT等大语言模型的集成，提供智能分析和响应能力
- **灵活配置**: 支持多种配置方式，包括环境变量、配置文件和命令行参数
- **安全增强**: 为Python执行和文件操作提供了安全限制和资源控制
- **多种启动模式**: 支持标准模式和Docker沙箱模式两种启动方式

### Unimplemented Features
- **前端界面资源展示**: 目前仅支持命令行界面，未实现图形用户界面和资源可视化
- **Docker资源的自动创建与销毁**: Docker容器需要手动管理，未实现基于任务的自动生命周期管理
- **Web浏览和搜索工具**: 未实现Web浏览和在线搜索功能
- **多代理协作**: 未实现多个代理之间的协作机制
- **长期记忆**: 未实现会话之间的记忆保存和恢复功能
- **自定义工具市场**: 未提供工具的发布、共享和安装平台

## Acknowledgments
Special thanks to the OpenManus project ([GitHub Repository](https://github.com/mannaandpoem/OpenManus)) for their open-source contribution. This project draws inspiration from and is based on their work.

This project was entirely generated using [Cursor](https://cursor.sh/) IDE powered by [Claude-3.7-sonnet](https://www.anthropic.com/), showcasing the capabilities of modern AI assistants in code generation and project development.