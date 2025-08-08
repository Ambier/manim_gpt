"""
Configuration management for Manim-GPT
"""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """应用设置"""
    
    # API Keys
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    qwen_api_key: Optional[str] = Field(None, env="QWEN_API_KEY")
    
    # 通义千问语音识别配置
    dashscope_api_key: Optional[str] = Field(None, env="DASHSCOPE_API_KEY")
    qwen_omni_model: str = Field("qwen2.5-omni-7b", env="QWEN_OMNI_MODEL")
    qwen_omni_voice: str = Field("Cherry", env="QWEN_OMNI_VOICE")
    
    # 语音识别网络配置
    voice_network_timeout: int = Field(15, env="VOICE_NETWORK_TIMEOUT")
    voice_retry_times: int = Field(3, env="VOICE_RETRY_TIMES")
    
    # HTTP代理配置（如果需要）
    http_proxy: Optional[str] = Field(None, env="HTTP_PROXY")
    https_proxy: Optional[str] = Field(None, env="HTTPS_PROXY")
    
    # Paths
    output_dir: Path = Field(Path("outputs"), env="OUTPUT_DIR")
    temp_dir: Path = Field(Path("temp"), env="TEMP_DIR")
    
    # Server settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(True, env="DEBUG")
    
    # LLM settings
    default_model: str = Field("deepseek-chat", env="DEFAULT_MODEL")
    max_tokens: int = Field(4000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    # Manim settings
    manim_quality: str = Field("medium_quality", env="MANIM_QUALITY")
    manim_format: str = Field("mp4", env="MANIM_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # 允许额外的字段，避免pydantic错误
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

# 全局设置实例
settings = Settings()
