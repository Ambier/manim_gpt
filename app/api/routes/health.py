"""
Health check API routes
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.llm_service import llm_service
from app import __version__

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """健康检查"""
    
    try:
        # 获取可用的模型
        available_models = llm_service.get_available_models()
        
        return HealthResponse(
            status="healthy",
            version=__version__,
            models_available=available_models
        )
    
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version=__version__,
            models_available=[]
        ) 
