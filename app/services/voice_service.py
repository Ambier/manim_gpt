"""
Basic voice recognition service using Qwen-Omni
"""

import base64
import tempfile
import os
import io
from typing import Dict, Any, Optional
import logging
from pathlib import Path

# 尝试导入音频处理库
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# 导入通义千问-Omni服务
from app.services.qwen_omni_service import qwen_omni_service

logger = logging.getLogger(__name__)

class VoiceService:
    """基于通义千问-Omni的语音识别服务"""
    
    def __init__(self):
        logger.info("初始化语音识别服务...")
        
        # 检查通义千问-Omni服务是否可用
        if qwen_omni_service.available:
            logger.info("通义千问-Omni语音识别服务已准备就绪")
            self.primary_service = "qwen_omni"
        else:
            logger.warning("通义千问-Omni服务不可用，请检查DASHSCOPE_API_KEY配置")
            self.primary_service = None
        
        logger.info("语音识别服务初始化完成")
    
    def _convert_audio_to_wav(self, audio_data: bytes) -> Optional[bytes]:
        """将音频数据转换为WAV格式"""
        if not PYDUB_AVAILABLE:
            logger.warning("pydub不可用，无法进行音频格式转换")
            return audio_data
        
        try:
            # 尝试不同的音频格式
            audio_formats = ['webm', 'ogg', 'mp3', 'mp4', 'm4a', 'wav']
            
            for fmt in audio_formats:
                try:
                    # 尝试使用当前格式加载音频
                    audio_segment = AudioSegment.from_file(
                        io.BytesIO(audio_data), 
                        format=fmt
                    )
                    
                    # 转换为WAV格式
                    wav_io = io.BytesIO()
                    audio_segment.export(
                        wav_io, 
                        format="wav",
                        parameters=["-ac", "1", "-ar", "16000"]  # 单声道，16kHz采样率
                    )
                    wav_data = wav_io.getvalue()
                    
                    logger.info(f"成功将{fmt}格式转换为WAV")
                    return wav_data
                    
                except Exception as e:
                    logger.debug(f"尝试{fmt}格式失败: {e}")
                    continue
            
            logger.error("无法识别音频格式")
            return None
            
        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            return None
    
    def _prepare_audio_data(self, audio_data: bytes) -> Optional[str]:
        """准备音频数据，转换格式并编码为base64"""
        try:
            # 尝试转换音频格式
            wav_data = self._convert_audio_to_wav(audio_data)
            if wav_data is None:
                wav_data = audio_data  # 如果转换失败，使用原始数据
            
            # 编码为base64
            audio_base64 = base64.b64encode(wav_data).decode('utf-8')
            return audio_base64
            
        except Exception as e:
            logger.error(f"准备音频数据失败: {e}")
            return None
    
    async def speech_to_text(self, audio_data_base64: str) -> Dict[str, Any]:
        """将语音转换为文本"""
        
        if not audio_data_base64:
            return {
                "success": False,
                "text": None,
                "error": "音频数据为空"
            }
        
        try:
            # 解码base64音频数据验证
            try:
                audio_data = base64.b64decode(audio_data_base64)
            except Exception as e:
                return {
                    "success": False,
                    "text": None,
                    "error": f"无法解码音频数据: {str(e)}"
                }
            
            if len(audio_data) == 0:
                return {
                    "success": False,
                    "text": None,
                    "error": "音频数据为空"
                }
            
            # 准备音频数据（可选的格式转换）
            prepared_audio = self._prepare_audio_data(audio_data)
            if not prepared_audio:
                # 如果格式转换失败，直接使用原始数据
                prepared_audio = audio_data_base64
            
            # 使用通义千问-Omni进行语音识别
            if self.primary_service == "qwen_omni":
                logger.debug("使用通义千问-Omni进行语音识别")
                result = await qwen_omni_service.speech_to_text(prepared_audio)
                
                if result["success"]:
                    logger.info(f"语音识别成功: {result['text']}")
                    return result
                else:
                    logger.warning(f"通义千问-Omni识别失败: {result['error']}")
            
            # 如果主要服务不可用或失败
            return {
                "success": False,
                "text": None,
                "error": "语音识别服务不可用，请检查DASHSCOPE_API_KEY配置"
            }
        
        except Exception as e:
            logger.error(f"语音处理异常: {e}")
            return {
                "success": False,
                "text": None,
                "error": f"语音处理失败: {str(e)}"
            }
    
    def is_audio_valid(self, audio_data_base64: str) -> bool:
        """验证音频数据是否有效"""
        try:
            if not audio_data_base64:
                return False
            
            audio_data = base64.b64decode(audio_data_base64)
            if len(audio_data) < 100:  # 音频数据太小
                return False
            
            # 基本的数据完整性检查
            return True
            
        except Exception:
            return False
    
    async def test_service(self) -> Dict[str, Any]:
        """测试语音识别服务"""
        if self.primary_service == "qwen_omni":
            is_available = await qwen_omni_service.test_connection()
            return {
                "service": "Qwen-Omni", 
                "available": is_available,
                "model": qwen_omni_service.model if is_available else None
            }
        else:
            return {
                "service": "None",
                "available": False,
                "error": "没有可用的语音识别服务"
            }

# 创建全局实例
voice_service = VoiceService() 
