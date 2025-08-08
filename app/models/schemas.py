"""
Pydantic models for API request/response schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ModelType(str, Enum):
    """支持的LLM模型类型"""
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    QWEN_TURBO = "qwen-turbo"
    QWEN_PLUS = "qwen-plus"
    QWEN_MAX = "qwen-max"

class QualityType(str, Enum):
    """视频质量类型"""
    LOW = "low_quality"
    MEDIUM = "medium_quality"
    HIGH = "high_quality"
    PRODUCTION = "production_quality"

class GenerationRequest(BaseModel):
    """生成动画请求"""
    prompt: str = Field(..., description="用户输入的描述")
    model: ModelType = Field(ModelType.DEEPSEEK_CHAT, description="使用的LLM模型")
    quality: QualityType = Field(QualityType.MEDIUM, description="视频质量")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="生成温度")
    max_tokens: int = Field(4000, ge=100, le=8000, description="最大token数")

class GenerationResponse(BaseModel):
    """生成动画响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    code: Optional[str] = Field(None, description="生成的Manim代码")
    video_path: Optional[str] = Field(None, description="生成的视频路径")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    error: Optional[str] = Field(None, description="错误信息")

class PreviewRequest(BaseModel):
    """预览请求"""
    code: str = Field(..., description="Manim代码")
    quality: QualityType = Field(QualityType.MEDIUM, description="视频质量")

class PreviewResponse(BaseModel):
    """预览响应"""
    success: bool = Field(..., description="是否成功")
    video_path: Optional[str] = Field(None, description="预览视频路径")
    error: Optional[str] = Field(None, description="错误信息")

class SaveRequest(BaseModel):
    """保存请求"""
    video_path: str = Field(..., description="视频路径")
    filename: Optional[str] = Field(None, description="保存的文件名")
    target_dir: Optional[str] = Field(None, description="目标目录")

class SaveResponse(BaseModel):
    """保存响应"""
    success: bool = Field(..., description="是否成功")
    saved_path: Optional[str] = Field(None, description="保存的路径")
    error: Optional[str] = Field(None, description="错误信息")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本信息")
    models_available: List[str] = Field(..., description="可用的模型列表")
    
class VoiceRequest(BaseModel):
    """语音识别请求"""
    audio_data: str = Field(..., description="Base64编码的音频数据")
    
class VoiceResponse(BaseModel):
    """语音识别响应"""
    success: bool = Field(..., description="是否成功")
    text: Optional[str] = Field(None, description="识别的文本")
    error: Optional[str] = Field(None, description="错误信息")
    method: Optional[str] = Field(None, description="使用的识别方法")
    model: Optional[str] = Field(None, description="使用的模型") 
