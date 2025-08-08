"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.api.routes import generation, voice
from app.core.logger import app_logger, api_logger

# 记录应用启动
app_logger.info("正在启动 Manim-GPT 应用...")

# 创建FastAPI应用
app = FastAPI(
    title="Manim-GPT",
    description="AI-powered mathematical animation generator using Manim",
    version="1.0.0"
)

app_logger.info("FastAPI 应用已创建")

# 设置静态文件
static_dir = Path("app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app_logger.info(f"静态文件目录已挂载: {static_dir}")
else:
    app_logger.warning(f"静态文件目录不存在: {static_dir}")

# 挂载outputs目录为静态文件服务，供前端访问生成的视频
outputs_dir = Path("outputs")
if outputs_dir.exists():
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
    app_logger.info(f"输出文件目录已挂载: {outputs_dir}")
else:
    # 如果outputs目录不存在，创建它
    outputs_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
    app_logger.info(f"输出文件目录已创建并挂载: {outputs_dir}")

# 注册API路由
app.include_router(generation.router, prefix="/api", tags=["generation"])
app.include_router(voice.router, prefix="/api", tags=["voice"])
app_logger.info("API路由已注册: /api (generation, voice)")

@app.get("/")
async def root():
    """主页"""
    api_logger.info("访问主页")
    try:
        index_file = Path("app/templates/index.html")
        if index_file.exists():
            api_logger.debug(f"返回主页文件: {index_file}")
            return FileResponse("app/templates/index.html")
        else:
            api_logger.warning(f"主页文件不存在: {index_file}")
            return {"message": "Manim-GPT API Server", "status": "running"}
    except Exception as e:
        api_logger.error(f"主页访问失败: {str(e)}")
        return {"message": "Manim-GPT API Server", "status": "running", "error": str(e)}

@app.get("/health")
async def health_check():
    """健康检查"""
    api_logger.info("执行健康检查")
    
    try:
        from app.core.config import settings
        
        # 检查各个服务状态
        llm_status = "configured" if settings.deepseek_api_key or settings.openai_api_key or settings.qwen_api_key else "not configured"
        
        health_data = {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "api": "running",
                "llm": llm_status,
                "manim": "available"
            }
        }
        
        api_logger.info(f"健康检查结果: {health_data}")
        return health_data
        
    except Exception as e:
        api_logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "error",
            "version": "1.0.0",
            "error": str(e)
        }

app_logger.success("Manim-GPT 应用初始化完成") 
