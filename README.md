# 🎬 Manim-GPT

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Manim](https://img.shields.io/badge/Manim-0.19+-orange.svg)](https://www.manim.community/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Black-000000.svg)](https://github.com/psf/black)

**🚀 AI驱动的数学动画生成器 | 语音识别 + LLM + Manim**

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [演示](#-演示) • [文档](#-文档) • [贡献](#-贡献)

</div>

## 📖 项目简介

**Manim-GPT** 是一个创新的开源项目，结合了**大语言模型(LLM)**、**语音识别**和**Manim动画引擎**，让用户能够通过自然语言描述或语音输入，快速生成精美的数学动画。

![image](https://github.com/user-attachments/assets/2e56793b-33e7-4b39-9900-680c122b2ada)

### 🎯 项目愿景

- **零门槛创作**：无需学习Manim语法，用自然语言即可创建动画
- **语音交互**：支持语音输入，解放双手，提升创作效率  
- **AI驱动**：集成多种LLM模型，智能生成高质量代码
- **现代化UI**：美观直观的Web界面，流畅的用户体验

## ✨ 功能特性
![image](https://github.com/user-attachments/assets/5eaa73a0-ff92-4461-b4ff-6600bf3b7687)

### 🤖 智能代码生成
- **多模型支持**：DeepSeek、OpenAI GPT、阿里云通义千问
- **智能优化**：自动代码验证和错误修复
- **即时预览**：实时生成并播放动画视频

### 🎤 先进语音识别
- **通义千问-Omni**：高精度中英文语音识别
- **实时转换**：语音直接转换为动画描述
- **多格式支持**：WebM、WAV、OGG等音频格式

![image](https://github.com/user-attachments/assets/b92489a6-08c3-42e4-8e82-c9729d40b6ef)

### 🎨 丰富动画效果
- **数学图形**：函数、几何、代数等
- **物理仿真**：自由落体、波动、碰撞等  
- **自定义动画**：支持复杂的动画逻辑

### 🌐 现代化界面
- **响应式设计**：完美适配桌面和移动设备
- **深色主题**：护眼的现代化设计风格
- **快捷操作**：键盘快捷键，提升效率

## 🛠️ 技术架构

### 核心技术栈

- **后端框架**：FastAPI + Python 3.12+
- **前端技术**：原生JavaScript + Bootstrap 5
- **AI模型**：DeepSeek/GPT/Qwen + 通义千问-Omni
- **动画引擎**：Manim Community Edition
- **音频处理**：MediaRecorder API + FFmpeg

## 🚀 快速开始

### 环境要求

- **Python**: 3.12 或更高版本
- **操作系统**: Windows, macOS, Linux
- **浏览器**: Chrome/Edge/Firefox (支持MediaRecorder)

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/manim-gpt.git
cd manim-gpt
```

### 2. 安装依赖

使用 [uv](https://github.com/astral-sh/uv) (推荐):
```bash
uv sync
```

或使用 pip:
```bash
pip install -e .
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# === 必需配置 ===
# LLM API密钥 (至少配置一个)
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
QWEN_API_KEY=sk-your-qwen-key

# 语音识别API密钥 (可选，用于语音功能)
DASHSCOPE_API_KEY=sk-your-dashscope-key

# === 可选配置 ===
# 默认模型设置
DEFAULT_MODEL=deepseek-chat
MAX_TOKENS=4000
TEMPERATURE=0.7

# 语音识别设置
QWEN_OMNI_MODEL=qwen2.5-omni-7b
QWEN_OMNI_VOICE=Cherry
VOICE_NETWORK_TIMEOUT=15

# 服务器设置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 代理设置 (如需要)
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=https://your-proxy:port
```

### 4. 启动应用

```bash
python start.py
```

### 5. 开始使用

打开浏览器访问：
- **主页面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 💡 使用指南

### 文本输入模式

1. 在输入框中描述您想要的动画
   ```
   绘制一个红色圆形从左侧移动到右侧
   ```

2. 选择LLM模型和参数

3. 点击"生成动画"按钮

### 语音输入模式

1. 点击🎤按钮开始录音

2. 清晰说出动画描述

3. 再次点击🎤停止录音

4. 系统自动识别语音并生成动画

### 高级功能

- **Ctrl/Cmd + Enter**: 快速生成动画
- **Ctrl/Cmd + R**: 启动语音录音
- **实时预览**: 代码生成后立即播放
- **视频下载**: 保存动画到本地
- **代码复制**: 获取生成的Manim代码

## 📚 API文档

### 生成动画

```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "绘制一个弹跳的球",
  "model": "deepseek-chat",
  "quality": "medium_quality",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

### 语音识别

```http
POST /api/speech-to-text
Content-Type: application/json

{
  "audio_data": "base64_encoded_audio"
}
```

更多API详情请访问: http://localhost:8000/docs

## 🔧 配置说明

### LLM模型配置

| 模型 | API Key | 特点 |
|------|---------|------|
| DeepSeek | `DEEPSEEK_API_KEY` | 数学专业，成本低 |
| OpenAI GPT | `OPENAI_API_KEY` | 通用性强，质量高 |
| 通义千问 | `QWEN_API_KEY` | 中文优化，响应快 |

### 语音识别配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼API密钥 | - |
| `QWEN_OMNI_MODEL` | 语音识别模型 | `qwen2.5-omni-7b` |
| `QWEN_OMNI_VOICE` | 音色设置 | `Cherry` |
| `VOICE_NETWORK_TIMEOUT` | 网络超时(秒) | `15` |

### 视频质量设置

- `low_quality`: 480p, 15fps
- `medium_quality`: 720p, 30fps (默认)
- `high_quality`: 1080p, 60fps
- `production_quality`: 1440p, 60fps

## 🏗️ 项目结构

```
manim-gpt/
├── app/                    # 应用核心
│   ├── api/               # API路由
│   │   ├── routes/        # 路由定义
│   │   └── main.py        # FastAPI应用
│   ├── core/              # 核心配置
│   │   └── config.py      # 环境配置
│   ├── models/            # 数据模型
│   │   └── schemas.py     # Pydantic模型
│   ├── services/          # 业务服务
│   │   ├── llm_service.py      # LLM集成
│   │   ├── voice_service.py    # 语音处理
│   │   ├── manim_service.py    # Manim引擎
│   │   └── qwen_omni_service.py # 语音识别
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript
│   │   └── images/       # 图片资源
│   └── templates/         # HTML模板
├── outputs/               # 生成的视频
├── temp/                  # 临时文件
├── tests/                 # 测试文件
├── start.py              # 启动脚本
├── pyproject.toml        # 项目配置
└── README.md             # 项目文档
```

## 🧪 开发指南

### 开发环境设置

```bash
# 安装开发依赖
uv sync --dev

# 代码格式化
black app/

# 代码检查
flake8 app/

# 运行测试
pytest tests/
```

### 添加新的LLM模型

1. 在 `app/services/llm_service.py` 中添加模型适配器
2. 更新 `app/models/schemas.py` 中的模型枚举
3. 在配置文件中添加相关环境变量

### 自定义动画模板

在 `app/services/manim_service.py` 中可以：
- 添加新的动画模板
- 自定义渲染参数
- 扩展视频格式支持

## 📊 性能优化

### 缓存策略
- **代码缓存**: 相同提示词复用生成结果
- **视频缓存**: 避免重复渲染
- **模型预热**: 提升响应速度

### 资源管理
- **临时文件清理**: 自动清理过期文件
- **内存优化**: 流式处理大文件
- **并发控制**: 限制同时处理任务数

## 🔐 安全考虑

- **API密钥保护**: 环境变量管理，避免泄露
- **输入验证**: 严格校验用户输入
- **沙箱执行**: Manim代码安全隔离
- **速率限制**: 防止API滥用

## 🚀 部署指南

### Docker部署

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --no-dev

EXPOSE 8000
CMD ["python", "start.py"]
```

### 生产环境

```bash
# 使用gunicorn部署
gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 贡献

我们欢迎各种形式的贡献！

### 贡献方式

- 🐛 **报告Bug**: 通过Issue报告问题
- 💡 **功能建议**: 提出新功能想法
- 📝 **文档改进**: 完善文档和注释
- 🔧 **代码贡献**: 提交Pull Request

### 开发流程

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 代码规范

- 遵循 **PEP 8** Python代码规范
- 使用 **Black** 进行代码格式化
- 添加适当的**类型注释**
- 编写**单元测试**

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

- [Manim Community](https://www.manim.community/) - 优秀的数学动画引擎
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [OpenAI](https://openai.com/) - 强大的语言模型
- [DeepSeek](https://www.deepseek.com/) - 高效的数学推理模型
- [阿里云](https://www.aliyun.com/) - 通义千问语音识别服务

## 📞 联系我们

- **GitHub Issues**: [项目Issues](https://github.com/your-repo/manim-gpt/issues)
- **Email**: your-email@example.com
- **讨论**: [GitHub Discussions](https://github.com/your-repo/manim-gpt/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个⭐️！**

Made with ❤️ by the Manim-GPT Team

</div>
