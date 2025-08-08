"""
通义千问-Omni语音识别服务
"""

import json
import asyncio  
import aiohttp
from typing import Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class QwenOmniService:
    """通义千问-Omni语音识别服务"""
    
    def __init__(self):
        self.api_key = settings.dashscope_api_key
        self.model = settings.qwen_omni_model
        self.voice_name = settings.qwen_omni_voice
        self.timeout = settings.voice_network_timeout
        self.retry_times = settings.voice_retry_times
        
        # 使用OpenAI兼容的API端点 - 尝试国内端点
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        
        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY未配置，通义千问-Omni服务不可用")
            self.available = False
        else:
            self.available = True
            logger.info(f"通义千问-Omni服务已初始化，模型: {self.model}")

    async def speech_to_text(self, audio_base64: str) -> Dict[str, Any]:
        """
        将音频转换为文本
        """
        if not self.available:
            return {
                "success": False,
                "text": "",
                "error": "通义千问-Omni服务不可用"
            }
        
        # 将base64音频数据包装为正确的数据URI格式
        audio_data_uri = f"data:audio/wav;base64,{audio_base64}"
        
        # 构建API请求数据 - 使用OpenAI兼容格式
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_data_uri,  # 使用正确的数据URI格式
                                "format": "wav"
                            }
                        },
                        {
                            "type": "text", 
                            "text": "请将这段音频转换为文字"
                        }
                    ]
                }
            ],
            "modalities": ["text"],  # 只输出文本
            "stream": True,  # 必须设置为True
            "stream_options": {"include_usage": True}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 执行API调用
        for attempt in range(self.retry_times):
            try:
                logger.info(f"开始语音识别 (尝试 {attempt + 1}/{self.retry_times})")
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(self.api_url, json=request_data, headers=headers) as response:
                        if response.status == 200:
                            # 处理流式响应
                            full_text = ""
                            async for line in response.content:
                                if line:
                                    line_str = line.decode('utf-8').strip()
                                    if line_str.startswith('data: '):
                                        data_part = line_str[6:]  # 去除 'data: ' 前缀
                                        if data_part and data_part != '[DONE]':
                                            try:
                                                chunk_data = json.loads(data_part)
                                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                                    delta = chunk_data['choices'][0].get('delta', {})
                                                    if 'content' in delta and delta['content'] is not None:
                                                        full_text += delta['content']
                                            except json.JSONDecodeError:
                                                continue
                            
                            if full_text.strip():
                                logger.info(f"语音识别成功: {full_text[:50]}...")
                                return {
                                    "success": True,
                                    "text": full_text.strip(),
                                    "method": "qwen_omni",
                                    "model": self.model
                                }
                            else:
                                logger.warning("语音识别返回空结果")
                                return {
                                    "success": False,
                                    "text": "",
                                    "error": "识别结果为空"
                                }
                        else:
                            error_text = await response.text()
                            logger.error(f"API调用失败 (状态码: {response.status}): {error_text}")
                            
                            if response.status == 401:
                                return {
                                    "success": False,
                                    "text": "",
                                    "error": "API密钥无效，请检查DASHSCOPE_API_KEY配置"
                                }
                            elif response.status == 429:
                                if attempt < self.retry_times - 1:
                                    await asyncio.sleep(2 ** attempt)  # 指数退避
                                    continue
                                else:
                                    return {
                                        "success": False,
                                        "text": "",
                                        "error": "API调用频率限制，请稍后重试"
                                    }
                            else:
                                if attempt < self.retry_times - 1:
                                    continue
                                else:
                                    return {
                                        "success": False,
                                        "text": "",
                                        "error": f"API调用失败: {error_text}"
                                    }
                            
            except asyncio.TimeoutError:
                logger.warning(f"语音识别超时 (尝试 {attempt + 1}/{self.retry_times})")
                if attempt < self.retry_times - 1:
                    continue
                else:
                    return {
                        "success": False,
                        "text": "",
                        "error": "网络超时，请检查网络连接"
                    }
                    
            except Exception as e:
                logger.error(f"语音识别异常 (尝试 {attempt + 1}/{self.retry_times}): {str(e)}")
                if attempt < self.retry_times - 1:
                    continue
                else:
                    return {
                        "success": False,
                        "text": "",
                        "error": f"服务异常: {str(e)}"
                    }
        
        return {
            "success": False,
            "text": "",
            "error": f"重试{self.retry_times}次后仍然失败"
        }

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.available

# 创建全局实例
qwen_omni_service = QwenOmniService() 
