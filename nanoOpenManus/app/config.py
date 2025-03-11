import os
from pathlib import Path
from typing import Optional

# 尝试导入dotenv，如果不可用则提供降级方案
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Config:
    """配置管理类，用于管理LLM API密钥和其他设置"""
    
    def __init__(self):
        # 尝试加载.env文件
        self._load_dotenv()
        
        # LLM 配置
        self.llm_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
        self.llm_model: str = os.environ.get("LLM_MODEL", "gpt-4o")
        self.llm_base_url: str = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        
        # 代理配置
        self.max_steps: int = int(os.environ.get("MAX_STEPS", "15"))
        
        # 调试配置
        self.debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    
    def _load_dotenv(self):
        """尝试加载.env文件中的环境变量"""
        if not DOTENV_AVAILABLE:
            print("提示: 未安装python-dotenv包，无法从.env文件加载配置。")
            print("如需使用.env文件，请运行: pip install python-dotenv")
            return
        
        # 查找.env文件
        project_root = self._find_project_root()
        env_file = project_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ 已从 {env_file} 加载配置")
        else:
            print(f"提示: 未找到.env文件，使用系统环境变量。")
            print(f"您可以在 {project_root} 目录创建.env文件来配置环境变量。")
    
    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        current_dir = Path(__file__).resolve().parent
        
        # 向上查找直到找到项目根目录（包含main.py或.env文件）
        while current_dir != current_dir.parent:
            if (current_dir / "main.py").exists() or (current_dir / ".env").exists():
                return current_dir
            current_dir = current_dir.parent
        
        # 如果找不到，返回app的父目录
        return Path(__file__).resolve().parent.parent
    
    def __str__(self):
        """返回当前配置的字符串表示"""
        return (
            f"Config:\n"
            f"  LLM API 密钥: {'已设置' if self.llm_api_key else '未设置'}\n"
            f"  LLM 模型: {self.llm_model}\n"
            f"  LLM API URL: {self.llm_base_url}\n"
            f"  最大步骤数: {self.max_steps}\n"
            f"  调试模式: {'开启' if self.debug else '关闭'}"
        )
    
    @classmethod
    def from_env(cls):
        """从环境变量创建配置"""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict):
        """从字典创建配置"""
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


# 创建全局配置实例
config = Config() 