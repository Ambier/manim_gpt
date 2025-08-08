"""
Manim animation generation service
"""

import os
import sys
import subprocess
import tempfile
import time
import shutil
import concurrent.futures
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

from app.core.config import settings
from app.models.schemas import QualityType
from app.core.logger import manim_logger

class ManimService:
    """Manim服务管理类"""
    
    def __init__(self):
        manim_logger.info("初始化 Manim 服务...")
        
        self.temp_dir = settings.temp_dir
        self.output_dir = settings.output_dir
        
        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        manim_logger.info(f"临时目录: {self.temp_dir}")
        manim_logger.info(f"输出目录: {self.output_dir}")
        
        # 检查Manim是否可用
        self.manim_available = self._check_manim_availability()
        
        if self.manim_available:
            manim_logger.success("Manim环境检查通过，真实模式可用")
        else:
            manim_logger.warning("Manim未安装，将使用演示模式")
            
        manim_logger.success("Manim服务初始化完成")
    
    def _check_manim_availability(self) -> bool:
        """检查Manim是否可用"""
        manim_logger.debug("检查Manim可用性...")
        
        try:
            import manim
            manim_logger.info(f"Manim已安装，版本信息: {manim.__version__ if hasattr(manim, '__version__') else '未知'}")
            return True
        except ImportError:
            manim_logger.warning("Manim未安装")
            return False
    
    async def execute_manim_code(
        self,
        code: str,
        quality: QualityType = QualityType.MEDIUM,
        scene_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行Manim代码并生成视频"""
        
        manim_logger.info(f"开始执行Manim代码 - 质量: {quality.value}, 场景: {scene_name or '自动检测'}")
        manim_logger.debug(f"代码长度: {len(code)}字符")
        
        if not self.manim_available:
            manim_logger.info("使用演示模式执行")
            # 模拟模式：创建一个示例视频文件
            return await self._simulate_manim_execution(code, quality, scene_name)
        
        try:
            start_time = time.time()
            
            # 创建临时文件
            temp_file = self._create_temp_file(code)
            manim_logger.info(f"创建临时文件: {temp_file}")
            
            # 如果没有指定场景名称，尝试从代码中提取
            if not scene_name:
                scene_name = self._extract_scene_name(code)
                manim_logger.info(f"自动检测场景名称: {scene_name}")
            
            # 执行Manim命令
            manim_logger.info(f"开始执行Manim渲染 - 场景: {scene_name}, 质量: {quality.value}")
            result = await self._run_manim_command(temp_file, scene_name, quality)
            
            # 清理临时文件
            self._cleanup_temp_file(temp_file)
            
            duration = time.time() - start_time
            
            if result["success"]:
                manim_logger.success(f"Manim代码执行成功 - 耗时: {duration:.2f}秒, 输出: {result['video_path']}")
                return {
                    "success": True,
                    "video_path": result["video_path"],
                    "message": "动画生成成功",
                    "error": None
                }
            else:
                manim_logger.error(f"Manim代码执行失败 - 耗时: {duration:.2f}秒, 错误: {result['error']}")
                return {
                    "success": False,
                    "video_path": None,
                    "message": "动画生成失败",
                    "error": result["error"]
                }
                
        except Exception as e:
            manim_logger.error(f"Manim代码执行异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "video_path": None,
                "message": "动画生成失败",
                "error": f"执行错误: {str(e)}"
            }
    
    def _create_temp_file(self, code: str) -> Path:
        """创建临时Python文件"""
        # 生成唯一的临时文件名
        timestamp = int(time.time() * 1000)
        temp_filename = f"manim_temp_{timestamp}.py"
        temp_file = self.temp_dir / temp_filename
        
        manim_logger.debug(f"创建临时文件: {temp_file}")
        
        # 写入代码
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        manim_logger.debug(f"代码已写入临时文件，大小: {temp_file.stat().st_size}字节")
        return temp_file
    
    def _extract_scene_name(self, code: str) -> str:
        """从代码中提取场景类名"""
        manim_logger.debug("开始提取场景类名")
        
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('class ') and '(Scene)' in line:
                # 提取类名
                class_def = line.split('class ')[1].split('(')[0].strip()
                manim_logger.debug(f"找到场景类: {class_def}")
                return class_def
        
        # 如果没有找到，返回默认名称
        default_name = "MyScene"
        manim_logger.warning(f"未找到场景类定义，使用默认名称: {default_name}")
        return default_name
    
    async def _run_manim_command(
        self,
        temp_file: Path,
        scene_name: str,
        quality: QualityType
    ) -> Dict[str, Any]:
        """运行Manim命令"""
        
        # 质量映射
        quality_map = {
            QualityType.LOW: "-ql",
            QualityType.MEDIUM: "-qm", 
            QualityType.HIGH: "-qh",
            QualityType.PRODUCTION: "-qp"
        }
        
        # 构建命令
        output_filename = f"{scene_name}_{int(time.time())}"
        cmd = [
            sys.executable, "-m", "manim",
            quality_map[quality],
            "--output_file", output_filename,
            str(temp_file.absolute()),
            scene_name
        ]
        
        manim_logger.info(f"执行Manim命令: {' '.join(cmd)}")
        manim_logger.debug(f"工作目录: {self.output_dir}")
        
        try:
            # 在Windows下使用ProactorEventLoop来避免NotImplementedError
            if sys.platform == "win32":
                # 使用concurrent.futures在线程池中执行同步子进程
                def run_sync_command():
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=str(self.output_dir),
                        text=True,
                        timeout=300  # 5分钟超时
                    )
                    return result
                
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    result = await loop.run_in_executor(executor, run_sync_command)
                    
                stdout = result.stdout.encode('utf-8') if result.stdout else b''
                stderr = result.stderr.encode('utf-8') if result.stderr else b''
                returncode = result.returncode
                
            else:
                # 在非Windows系统上使用原来的异步方法
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.output_dir)
                )
                
                stdout, stderr = await process.communicate()
                returncode = process.returncode
            
            # 记录命令输出
            if stdout:
                manim_logger.debug(f"Manim标准输出: {stdout.decode('utf-8')}")
            if stderr:
                manim_logger.debug(f"Manim错误输出: {stderr.decode('utf-8')}")
            
            manim_logger.info(f"Manim命令执行完成，退出码: {returncode}")
            
            if returncode == 0:
                # 查找生成的视频文件
                video_path = self._find_generated_video(scene_name)
                
                if video_path:
                    manim_logger.success(f"找到生成的视频文件: {video_path}")
                    # 将Windows路径转换为Web兼容的路径格式（使用正斜杠）
                    web_compatible_path = str(video_path).replace('\\', '/')
                    return {
                        "success": True,
                        "video_path": web_compatible_path,
                        "error": None
                    }
                else:
                    manim_logger.error("Manim命令执行成功但未找到输出视频文件")
                    return {
                        "success": False,
                        "video_path": None,
                        "error": "无法找到生成的视频文件"
                    }
            else:
                error_message = stderr.decode('utf-8') if stderr else "Unknown error"
                manim_logger.error(f"Manim命令执行失败: {error_message}")
                return {
                    "success": False,
                    "video_path": None,
                    "error": f"Manim命令执行失败: {error_message}"
                }
                
        except Exception as e:
            manim_logger.error(f"执行Manim命令时出现异常: {str(e)}", exc_info=True)
            # 记录更多调试信息
            manim_logger.error(f"命令详情: {cmd}")
            manim_logger.error(f"工作目录: {self.output_dir}")
            manim_logger.error(f"临时文件: {temp_file}")
            manim_logger.error(f"异常类型: {type(e).__name__}")
            
            return {
                "success": False,
                "video_path": None,
                "error": f"执行命令时出错: {type(e).__name__}: {str(e)}"
            }
    
    def _find_generated_video(self, scene_name: str) -> Optional[Path]:
        """查找生成的视频文件"""
        manim_logger.debug(f"查找生成的视频文件，场景名: {scene_name}")
        
        # 在输出目录中查找视频文件
        possible_extensions = ['.mp4', '.mov', '.avi']
        
        # 查找媒体目录
        media_dirs = list(self.output_dir.glob("media/**"))
        manim_logger.debug(f"找到 {len(media_dirs)} 个媒体目录")
        
        for media_dir in media_dirs:
            if media_dir.is_dir():
                manim_logger.debug(f"搜索媒体目录: {media_dir}")
                for ext in possible_extensions:
                    # 查找包含场景名称的视频文件
                    video_files = list(media_dir.glob(f"*{scene_name}*{ext}"))
                    if video_files:
                        manim_logger.info(f"在媒体目录中找到视频文件: {video_files[0]}")
                        return video_files[0]  # 返回第一个匹配的文件
        
        # 如果在媒体目录没找到，直接在输出目录查找
        manim_logger.debug("在输出根目录中搜索视频文件")
        for ext in possible_extensions:
            video_files = list(self.output_dir.glob(f"*{scene_name}*{ext}"))
            if video_files:
                manim_logger.info(f"在输出目录中找到视频文件: {video_files[0]}")
                return video_files[0]
        
        manim_logger.warning(f"未找到包含场景名 '{scene_name}' 的视频文件")
        return None
    
    def _cleanup_temp_file(self, temp_file: Path):
        """清理临时文件"""
        try:
            if temp_file.exists():
                temp_file.unlink()
                manim_logger.debug(f"成功清理临时文件: {temp_file}")
            else:
                manim_logger.debug(f"临时文件不存在，无需清理: {temp_file}")
        except Exception as e:
            manim_logger.warning(f"清理临时文件失败: {temp_file}, 错误: {str(e)}")
    
    async def save_video(
        self,
        video_path: str,
        filename: Optional[str] = None,
        target_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """保存视频到指定位置"""
        
        manim_logger.info(f"开始保存视频 - 源路径: {video_path}, 目标文件名: {filename}, 目标目录: {target_dir}")
        
        try:
            source_path = Path(video_path)
            if not source_path.exists():
                manim_logger.error(f"源视频文件不存在: {source_path}")
                return {
                    "success": False,
                    "error": "源视频文件不存在"
                }
            
            # 确定目标目录
            if target_dir:
                target_directory = Path(target_dir)
            else:
                target_directory = self.output_dir
            
            target_directory.mkdir(parents=True, exist_ok=True)
            manim_logger.debug(f"目标目录: {target_directory}")
            
            # 确定文件名
            if not filename:
                filename = source_path.name
            
            target_path = target_directory / filename
            manim_logger.info(f"目标路径: {target_path}")
            
            # 复制文件
            file_size = source_path.stat().st_size
            shutil.copy2(source_path, target_path)
            
            manim_logger.success(f"视频保存成功 - 大小: {file_size}字节, 路径: {target_path}")
            
            return {
                "success": True,
                "target_path": str(target_path),
                "error": None
            }
            
        except Exception as e:
            manim_logger.error(f"保存视频失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"保存视频失败: {str(e)}"
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """验证Manim代码"""
        manim_logger.info("开始验证Manim代码")
        manim_logger.debug(f"代码长度: {len(code)}字符")
        
        try:
            # 基本语法检查
            manim_logger.debug("执行语法检查...")
            compile(code, '<string>', 'exec')
            manim_logger.debug("语法检查通过")
            
            # 检查是否包含Scene类
            if 'class ' not in code or '(Scene)' not in code:
                manim_logger.warning("代码验证失败: 缺少Scene类")
                return {
                    "valid": False,
                    "error": "代码必须包含继承自Scene的类"
                }
            
            # 检查是否有construct方法
            if 'def construct(self):' not in code:
                manim_logger.warning("代码验证失败: 缺少construct方法")
                return {
                    "valid": False,
                    "error": "Scene类必须包含construct方法"
                }
            
            manim_logger.success("代码验证通过")
            return {
                "valid": True,
                "error": None
            }
            
        except SyntaxError as e:
            manim_logger.error(f"代码语法错误: {str(e)}")
            return {
                "valid": False,
                "error": f"语法错误: {str(e)}"
            }
        except Exception as e:
            manim_logger.error(f"代码验证异常: {str(e)}", exc_info=True)
            return {
                "valid": False,
                "error": f"验证失败: {str(e)}"
            }

    async def _simulate_manim_execution(
        self,
        code: str,
        quality: QualityType,
        scene_name: Optional[str]
    ) -> Dict[str, Any]:
        """模拟Manim执行（用于演示）"""
        
        manim_logger.info(f"开始演示模式执行 - 质量: {quality.value}")
        
        # 模拟处理时间
        await asyncio.sleep(2)
        
        # 创建一个示例"视频"文件（实际上是文本文件）
        if not scene_name:
            scene_name = self._extract_scene_name(code)
        
        timestamp = int(time.time())
        demo_filename = f"{scene_name}_{timestamp}_demo.txt"
        demo_path = self.output_dir / demo_filename
        
        manim_logger.info(f"创建演示文件: {demo_path}")
        
        # 创建演示文件
        demo_content = f"""
=== Manim-GPT 演示模式 ===

生成的代码:
{code}

场景名称: {scene_name}
质量设置: {quality.value}
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

注意: 这是演示模式。要生成真实的视频，请安装Manim:
pip install manim

演示视频路径: {demo_path}
"""
        
        with open(demo_path, 'w', encoding='utf-8') as f:
            f.write(demo_content)
        
        file_size = demo_path.stat().st_size
        manim_logger.success(f"演示文件创建成功 - 大小: {file_size}字节")
        
        # 将Windows路径转换为Web兼容的路径格式
        web_compatible_path = str(demo_path).replace('\\', '/')
        
        return {
            "success": True,
            "video_path": web_compatible_path,
            "message": "演示模式：动画代码已生成（需要安装Manim来生成真实视频）",
            "error": None
        }

# 全局Manim服务实例
manim_logger.info("创建全局Manim服务实例")
manim_service = ManimService() 
