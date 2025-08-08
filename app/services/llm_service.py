"""
Large Language Model service integration
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any
import aiohttp
from openai import OpenAI

from app.core.config import settings
from app.models.schemas import ModelType
from app.core.logger import llm_logger

class LLMService:
    """LLM服务管理类"""
    
    def __init__(self):
        llm_logger.info("初始化 LLM 服务...")
        
        self.openai_client = None
        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            llm_logger.info("OpenAI客户端初始化成功")
        else:
            llm_logger.info("未配置OpenAI API密钥")
            
        if settings.deepseek_api_key:
            llm_logger.info("DeepSeek API密钥已配置")
        else:
            llm_logger.info("未配置DeepSeek API密钥")
            
        if settings.qwen_api_key:
            llm_logger.info("Qwen API密钥已配置")
        else:
            llm_logger.info("未配置Qwen API密钥")
            
        llm_logger.success("LLM服务初始化完成")
    
    async def generate_manim_code(
        self, 
        prompt: str, 
        model: ModelType = ModelType.DEEPSEEK_CHAT,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """生成Manim代码"""
        
        llm_logger.info(f"开始生成Manim代码 - 模型: {model.value}, 温度: {temperature}, 最大令牌: {max_tokens}")
        llm_logger.debug(f"用户提示词: {prompt[:100]}..." if len(prompt) > 100 else f"用户提示词: {prompt}")
        
        system_prompt = """你是一个专业的Manim动画代码生成器。请根据用户的描述生成完整的、可执行的Manim代码。

要求：
1. 生成的代码必须是完整的、可运行的Manim Scene类
2. 包含必要的import语句
3. 代码风格清晰，有适当的注释
4. 确保动画逻辑正确，视觉效果良好
5. 只返回Python代码，不要包含任何解释文字

⚠️ 重要限制 - 避免LaTeX依赖：
- 不要使用 Tex() 或 MathTex() 类
- 不要使用 get_axis_labels() 方法
- 不要使用 get_x_axis_label() 或 get_y_axis_label() 方法
- 使用 Text() 类代替 Tex() 来显示文本
- 如果需要坐标轴，创建不带标签的 Axes()
- 如果需要数学符号，使用 Text() 或简单的几何图形

推荐的替代方案：
- 使用 Text("x") 而不是 Tex("x")
- 使用 Axes() 而不是 axes.get_axis_labels()
- 使用简单的几何图形和颜色来表达数学概念

以下是一个示例格式：

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # 使用Text而不是Tex
        title = Text("动画标题", font_size=36)
        
        # 创建不带标签的坐标轴
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            axis_config={"color": BLUE}
        )
        
        # 你的动画代码
        self.play(Write(title))
        self.play(Create(axes))
```

请根据用户的描述生成相应的Manim代码。"""

        user_prompt = f"请为以下描述生成Manim动画代码：\n\n{prompt}"
        
        try:
            start_time = time.time()
            
            if model in [ModelType.DEEPSEEK_CHAT, ModelType.DEEPSEEK_CODER]:
                llm_logger.info(f"使用DeepSeek API生成代码 - 模型: {model.value}")
                result = await self._call_deepseek(system_prompt, user_prompt, model, temperature, max_tokens)
            elif model in [ModelType.QWEN_TURBO, ModelType.QWEN_PLUS, ModelType.QWEN_MAX]:
                llm_logger.info(f"使用Qwen API生成代码 - 模型: {model.value}")
                result = await self._call_qwen(system_prompt, user_prompt, model, temperature, max_tokens)
            else:
                llm_logger.info(f"使用OpenAI API生成代码 - 模型: {model.value}")
                result = await self._call_openai(system_prompt, user_prompt, model, temperature, max_tokens)
            
            duration = time.time() - start_time
            
            if result["success"]:
                code_length = len(result["code"]) if result["code"] else 0
                llm_logger.success(f"代码生成成功 - 耗时: {duration:.2f}秒, 代码长度: {code_length}字符")
                llm_logger.debug(f"生成的代码预览: {result['code'][:200]}..." if code_length > 200 else f"生成的代码: {result['code']}")
            else:
                llm_logger.error(f"代码生成失败 - 耗时: {duration:.2f}秒, 错误: {result['error']}")
            
            return result
            
        except Exception as e:
            llm_logger.error(f"LLM调用异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"LLM调用失败: {str(e)}",
                "code": None
            }
    
    async def _call_deepseek(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model: ModelType,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """调用DeepSeek API"""
        
        if not settings.deepseek_api_key:
            llm_logger.error("DeepSeek API密钥未配置")
            return {
                "success": False,
                "error": "DeepSeek API key not configured",
                "code": None
            }
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model.value,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        llm_logger.debug(f"发送DeepSeek API请求 - URL: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    llm_logger.debug(f"DeepSeek API响应状态: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        code = result["choices"][0]["message"]["content"]
                        
                        llm_logger.info("DeepSeek API调用成功")
                        llm_logger.debug(f"API响应令牌使用情况: {result.get('usage', {})}")
                        
                        return {
                            "success": True,
                            "code": self._extract_code(code),
                            "error": None
                        }
                    else:
                        error_text = await response.text()
                        llm_logger.error(f"DeepSeek API调用失败 - 状态码: {response.status}, 响应: {error_text}")
                        return {
                            "success": False,
                            "error": f"DeepSeek API error: {response.status} - {error_text}",
                            "code": None
                        }
                        
        except Exception as e:
            llm_logger.error(f"DeepSeek API请求异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"DeepSeek API请求失败: {str(e)}",
                "code": None
            }
    
    async def _call_openai(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model: ModelType,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """调用OpenAI API"""
        
        if not self.openai_client:
            llm_logger.error("OpenAI API客户端未初始化")
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "code": None
            }
        
        llm_logger.debug(f"发送OpenAI API请求 - 模型: {model.value}")
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model.value,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            code = response.choices[0].message.content
            
            llm_logger.info("OpenAI API调用成功")
            llm_logger.debug(f"API响应令牌使用情况: {response.usage}")
            
            return {
                "success": True,
                "code": self._extract_code(code),
                "error": None
            }
        except Exception as e:
            llm_logger.error(f"OpenAI API调用异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}",
                "code": None
            }
    
    async def _call_qwen(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model: ModelType,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """调用Qwen API"""
        
        if not settings.qwen_api_key:
            llm_logger.error("Qwen API密钥未配置")
            return {
                "success": False,
                "error": "Qwen API key not configured",
                "code": None
            }
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {settings.qwen_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model.value,
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        
        llm_logger.debug(f"发送Qwen API请求 - URL: {url}")
        llm_logger.debug(f"请求模型: {model.value}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=60) as response:
                    llm_logger.debug(f"Qwen API响应状态: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        llm_logger.debug(f"Qwen API响应结构: {list(result.keys()) if isinstance(result, dict) else str(type(result))}")
                        
                        # Qwen API的标准响应格式: output.text
                        if result.get("output") and result["output"].get("text"):
                            code = result["output"]["text"]
                            
                            llm_logger.info("Qwen API调用成功")
                            llm_logger.debug(f"API响应令牌使用情况: {result.get('usage', {})}")
                            
                            return {
                                "success": True,
                                "code": self._extract_code(code),
                                "error": None
                            }
                        else:
                            # 如果响应格式不匹配，记录详细信息
                            llm_logger.error(f"Qwen API响应格式异常:")
                            llm_logger.error(f"  - 响应键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                            if result.get("output"):
                                llm_logger.error(f"  - output键: {list(result['output'].keys()) if isinstance(result['output'], dict) else 'Not a dict'}")
                            
                            error_msg = result.get("message", f"响应格式错误，缺少output.text字段")
                            return {
                                "success": False,
                                "error": f"Qwen API响应格式错误: {error_msg}",
                                "code": None
                            }
                    else:
                        error_text = await response.text()
                        llm_logger.error(f"Qwen API调用失败 - 状态码: {response.status}")
                        llm_logger.error(f"响应内容: {error_text}")
                        return {
                            "success": False,
                            "error": f"Qwen API HTTP错误: {response.status} - {error_text[:200]}",
                            "code": None
                        }
                        
        except asyncio.TimeoutError:
            llm_logger.error("Qwen API请求超时")
            return {
                "success": False,
                "error": "Qwen API请求超时",
                "code": None
            }
        except Exception as e:
            llm_logger.error(f"Qwen API请求异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Qwen API请求失败: {str(e)}",
                "code": None
            }
    
    def _extract_code(self, content: str) -> str:
        """从LLM响应中提取代码"""
        llm_logger.debug("开始提取代码块")
        
        original_length = len(content)
        
        # 查找代码块
        if "```python" in content:
            start = content.find("```python") + 9
            end = content.find("```", start)
            if end != -1:
                extracted_code = content[start:end].strip()
                llm_logger.debug(f"从python代码块中提取代码 - 原始长度: {original_length}, 提取长度: {len(extracted_code)}")
                return extracted_code
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end != -1:
                extracted_code = content[start:end].strip()
                llm_logger.debug(f"从通用代码块中提取代码 - 原始长度: {original_length}, 提取长度: {len(extracted_code)}")
                return extracted_code
        
        # 如果没有找到代码块，返回整个内容
        llm_logger.debug(f"未找到代码块标记，返回完整内容 - 长度: {original_length}")
        return content.strip()
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        llm_logger.info("获取可用模型列表")
        
        models = []
        
        if settings.deepseek_api_key:
            models.extend([ModelType.DEEPSEEK_CHAT.value, ModelType.DEEPSEEK_CODER.value])
            llm_logger.debug("添加DeepSeek模型到可用列表")
        
        if settings.openai_api_key:
            models.extend([ModelType.GPT_4.value, ModelType.GPT_3_5_TURBO.value])
            llm_logger.debug("添加OpenAI模型到可用列表")
            
        if settings.qwen_api_key:
            models.extend([ModelType.QWEN_TURBO.value, ModelType.QWEN_PLUS.value, ModelType.QWEN_MAX.value])
            llm_logger.debug("添加Qwen模型到可用列表")
        
        llm_logger.info(f"可用模型数量: {len(models)} - {models}")
        return models

# 全局LLM服务实例
llm_logger.info("创建全局LLM服务实例")
llm_service = LLMService() 
