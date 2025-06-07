"""
Animation generation API routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any
import asyncio
import time

from app.models.schemas import (
    GenerationRequest, 
    GenerationResponse, 
    PreviewRequest, 
    PreviewResponse,
    SaveRequest,
    SaveResponse
)
from app.services.llm_service import llm_service
from app.services.manim_service import manim_service
from app.core.logger import api_logger

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_animation(request: GenerationRequest, req: Request) -> GenerationResponse:
    """生成Manim动画"""
    
    client_ip = req.client.host if req.client else "unknown"
    api_logger.info(f"收到动画生成请求 - 客户端: {client_ip}")
    api_logger.debug(f"请求参数 - 模型: {request.model.value}, 质量: {request.quality.value}, 温度: {request.temperature}")
    api_logger.debug(f"提示词长度: {len(request.prompt)}字符")
    
    start_time = time.time()
    
    try:
        # 1. 使用LLM生成Manim代码
        api_logger.info("开始调用LLM服务生成代码")
        llm_start = time.time()
        
        llm_result = await llm_service.generate_manim_code(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        llm_duration = time.time() - llm_start
        api_logger.info(f"LLM服务调用完成 - 耗时: {llm_duration:.2f}秒, 成功: {llm_result['success']}")
        
        if not llm_result["success"]:
            api_logger.error(f"LLM代码生成失败: {llm_result['error']}")
            return GenerationResponse(
                success=False,
                message="代码生成失败",
                error=llm_result["error"]
            )
        
        generated_code = llm_result["code"]
        api_logger.debug(f"生成代码长度: {len(generated_code)}字符")
        
        # 2. 验证生成的代码
        api_logger.info("开始验证生成的代码")
        validation_result = manim_service.validate_code(generated_code)
        
        if not validation_result["valid"]:
            api_logger.warning(f"代码验证失败: {validation_result['error']}")
            return GenerationResponse(
                success=False,
                message="生成的代码无效",
                code=generated_code,
                error=validation_result["error"]
            )
        
        api_logger.info("代码验证通过")
        
        # 3. 执行Manim代码生成视频
        api_logger.info("开始调用Manim服务生成视频")
        manim_start = time.time()
        
        manim_result = await manim_service.execute_manim_code(
            code=generated_code,
            quality=request.quality
        )
        
        manim_duration = time.time() - manim_start
        total_duration = time.time() - start_time
        
        api_logger.info(f"Manim服务调用完成 - 耗时: {manim_duration:.2f}秒, 成功: {manim_result['success']}")
        api_logger.info(f"整个生成流程完成 - 总耗时: {total_duration:.2f}秒")
        
        if manim_result["success"]:
            api_logger.success(f"动画生成成功 - 输出文件: {manim_result['video_path']}")
            return GenerationResponse(
                success=True,
                message=manim_result["message"],
                code=generated_code,
                video_path=manim_result["video_path"]
            )
        else:
            api_logger.error(f"Manim执行失败: {manim_result['error']}")
            return GenerationResponse(
                success=False,
                message=manim_result["message"],
                code=generated_code,
                error=manim_result["error"]
            )
    
    except Exception as e:
        total_duration = time.time() - start_time
        api_logger.error(f"动画生成过程异常 - 耗时: {total_duration:.2f}秒, 错误: {str(e)}", exc_info=True)
        return GenerationResponse(
            success=False,
            message="生成过程中发生错误",
            error=str(e)
        )

@router.post("/preview", response_model=PreviewResponse)
async def preview_animation(request: PreviewRequest, req: Request) -> PreviewResponse:
    """预览Manim动画"""
    
    client_ip = req.client.host if req.client else "unknown"
    api_logger.info(f"收到动画预览请求 - 客户端: {client_ip}")
    api_logger.debug(f"预览参数 - 质量: {request.quality.value}")
    api_logger.debug(f"代码长度: {len(request.code)}字符")
    
    start_time = time.time()
    
    try:
        # 验证代码
        api_logger.info("开始验证用户提供的代码")
        validation_result = manim_service.validate_code(request.code)
        
        if not validation_result["valid"]:
            api_logger.warning(f"代码验证失败: {validation_result['error']}")
            return PreviewResponse(
                success=False,
                error=validation_result["error"]
            )
        
        api_logger.info("代码验证通过")
        
        # 执行代码生成预览
        api_logger.info("开始执行代码生成预览")
        result = await manim_service.execute_manim_code(
            code=request.code,
            quality=request.quality
        )
        
        duration = time.time() - start_time
        api_logger.info(f"预览生成完成 - 耗时: {duration:.2f}秒, 成功: {result['success']}")
        
        if result["success"]:
            api_logger.success(f"预览生成成功 - 输出文件: {result['video_path']}")
            return PreviewResponse(
                success=True,
                video_path=result["video_path"]
            )
        else:
            api_logger.error(f"预览生成失败: {result['error']}")
            return PreviewResponse(
                success=False,
                error=result["error"]
            )
    
    except Exception as e:
        duration = time.time() - start_time
        api_logger.error(f"预览生成过程异常 - 耗时: {duration:.2f}秒, 错误: {str(e)}", exc_info=True)
        return PreviewResponse(
            success=False,  
            error=str(e)
        )

@router.post("/save", response_model=SaveResponse)
async def save_animation(request: SaveRequest, req: Request) -> SaveResponse:
    """保存动画视频"""
    
    client_ip = req.client.host if req.client else "unknown"
    api_logger.info(f"收到视频保存请求 - 客户端: {client_ip}")
    api_logger.debug(f"保存参数 - 源路径: {request.video_path}, 文件名: {request.filename}, 目标目录: {request.target_dir}")
    
    start_time = time.time()
    
    try:
        api_logger.info("开始调用Manim服务保存视频")
        result = await manim_service.save_video(
            video_path=request.video_path,
            filename=request.filename,
            target_dir=request.target_dir
        )
        
        duration = time.time() - start_time
        api_logger.info(f"视频保存完成 - 耗时: {duration:.2f}秒, 成功: {result['success']}")
        
        if result["success"]:
            api_logger.success(f"视频保存成功 - 目标路径: {result['target_path']}")
            return SaveResponse(
                success=True,
                saved_path=result["target_path"]
            )
        else:
            api_logger.error(f"视频保存失败: {result['error']}")
            return SaveResponse(
                success=False,
                error=result["error"]
            )
    
    except Exception as e:
        duration = time.time() - start_time
        api_logger.error(f"视频保存过程异常 - 耗时: {duration:.2f}秒, 错误: {str(e)}", exc_info=True)
        return SaveResponse(
            success=False,
            error=str(e)
        )

@router.post("/validate-code")
async def validate_manim_code(code: str, req: Request) -> Dict[str, Any]:
    """验证Manim代码"""
    
    client_ip = req.client.host if req.client else "unknown"
    api_logger.info(f"收到代码验证请求 - 客户端: {client_ip}")
    api_logger.debug(f"代码长度: {len(code)}字符")
    
    start_time = time.time()
    
    try:
        api_logger.info("开始验证Manim代码")
        result = manim_service.validate_code(code)
        
        duration = time.time() - start_time
        api_logger.info(f"代码验证完成 - 耗时: {duration:.2f}秒, 有效: {result['valid']}")
        
        if result["valid"]:
            api_logger.success("代码验证通过")
            return {
                "valid": result["valid"],
                "error": result.get("error")
            }
        else:
            api_logger.warning(f"代码验证失败: {result['error']}")
            return {
                "valid": result["valid"],
                "error": result["error"]
            }
    
    except Exception as e:
        duration = time.time() - start_time
        api_logger.error(f"代码验证过程异常 - 耗时: {duration:.2f}秒, 错误: {str(e)}", exc_info=True)
        return {
            "valid": False,
            "error": str(e)
        } 