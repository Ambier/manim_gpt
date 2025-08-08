"""
应用日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

def setup_logger():
    """设置应用日志配置"""
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 添加文件日志处理器 - 应用日志
    logger.add(
        "logs/app.log",
        format=file_format,
        level="DEBUG",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # 添加错误日志文件
    logger.add(
        "logs/error.log",
        format=file_format,
        level="ERROR",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # 添加API访问日志
    logger.add(
        "logs/api.log",
        format=file_format,
        level="INFO",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["extra"].get("component") == "api"
    )
    
    # 添加LLM服务日志
    logger.add(
        "logs/llm.log",
        format=file_format,
        level="DEBUG",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["extra"].get("component") == "llm"
    )
    
    # 添加Manim服务日志
    logger.add(
        "logs/manim.log",
        format=file_format,
        level="DEBUG",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["extra"].get("component") == "manim"
    )
    
    # 添加Voice服务日志
    logger.add(
        "logs/voice.log",
        format=file_format,
        level="DEBUG",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["extra"].get("component") == "voice"
    )

# 初始化日志系统
setup_logger()

# 为不同组件创建专用的logger
api_logger = logger.bind(component="api")
llm_logger = logger.bind(component="llm") 
manim_logger = logger.bind(component="manim")
voice_logger = logger.bind(component="voice")
app_logger = logger.bind(component="app") 
