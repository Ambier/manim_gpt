"""
Voice recognition API routes using Qwen-Omni
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import VoiceRequest, VoiceResponse
from app.services.voice_service import voice_service

router = APIRouter()

@router.post("/speech-to-text", response_model=VoiceResponse)
async def speech_to_text(request: VoiceRequest) -> VoiceResponse:
    """语音转文本（使用通义千问-Omni）"""
    
    try:
        # 验证音频数据
        if not voice_service.is_audio_valid(request.audio_data):
            return VoiceResponse(
                success=False,
                error="无效的音频数据"
            )
        
        # 执行语音识别
        result = await voice_service.speech_to_text(request.audio_data)
        
        # 返回结果，包含识别方法信息
        return VoiceResponse(
            success=result["success"],
            text=result.get("text"),
            error=result.get("error"),
            method=result.get("method"),
            model=result.get("model")
        )
    
    except Exception as e:
        return VoiceResponse(
            success=False,
            error=f"语音识别处理异常: {str(e)}"
        )

@router.get("/status")
async def get_voice_service_status():
    """获取语音识别服务状态"""
    try:
        # 测试服务状态
        service_status = await voice_service.test_service()
        
        status = {
            "service": service_status["service"],
            "available": service_status["available"],
            "model": service_status.get("model"),
            "methods": ["Qwen-Omni ASR"] if service_status["available"] else [],
            "error": service_status.get("error")
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")

@router.get("/test")
async def test_voice_service():
    """测试语音识别服务连通性"""
    try:
        service_status = await voice_service.test_service()
        
        if service_status["available"]:
            return {
                "success": True,
                "message": f"语音识别服务正常 - {service_status['service']}",
                "model": service_status.get("model")
            }
        else:
            return {
                "success": False,
                "message": "语音识别服务不可用",
                "error": service_status.get("error")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务测试失败: {str(e)}") 
