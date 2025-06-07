# 🚀 快速安装指南

## 系统要求

- Python 3.12+
- 支持MediaRecorder的现代浏览器

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd manim-gpt
```

### 2. 安装依赖
```bash
# 推荐使用uv
uv sync

# 或使用pip
pip install -e .
```

### 3. 配置API密钥
创建 `.env` 文件：
```env
# 至少配置一个LLM API密钥
DEEPSEEK_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-your-key-here
QWEN_API_KEY=sk-your-key-here

# 可选：语音识别功能
DASHSCOPE_API_KEY=sk-your-key-here
```

### 4. 启动服务
```bash
python start.py
```

### 5. 访问应用
打开浏览器访问: http://localhost:8000

## 常见问题

### Q: 语音识别不工作？
A: 确保配置了 `DASHSCOPE_API_KEY` 并在HTTPS环境下使用

### Q: 视频生成失败？
A: 检查Manim是否正确安装，尝试重新安装依赖

### Q: API密钥错误？
A: 验证 `.env` 文件中的API密钥格式和有效性

## 获取帮助

- 查看完整文档: [README.md](README.md)
- 报告问题: [GitHub Issues]
- API文档: http://localhost:8000/docs 