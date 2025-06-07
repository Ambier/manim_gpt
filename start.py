#!/usr/bin/env python3
"""
启动脚本：Manim-GPT应用
"""

import uvicorn
import os
from pathlib import Path

def main():
    """启动应用程序"""
    # 确保输出目录存在
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting Manim-GPT Application...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📝 API documentation at: http://localhost:8000/docs")
    
    # 启动FastAPI服务器
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app", "."],
        log_level="info"
    )

if __name__ == "__main__":
    main() 