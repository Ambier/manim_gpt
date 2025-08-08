/**
 * Manim-GPT Frontend Application
 * 现代化的AI数学动画生成器前端应用
 * 语音识别：通义千问-Omni-Turbo
 */

class ManimGPTApp {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentVideoPath = null;
        this.animationSpeed = 0.3;
        
        // 实时语音识别相关
        this.realtimeRecording = false;
        this.realtimeSessionId = null;
        this.realtimeChunks = [];
        this.realtimeTimer = null;
        this.isRealtimeMode = false;
        
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.initElements();
        this.initEventListeners();
        this.initSpeechRecognition();
        this.initAnimations();
        this.updateCharCount();
        
        console.log('🚀 Manim-GPT 应用已初始化 - 通义千问-Omni语音识别');
    }

    /**
     * 初始化DOM元素引用
     */
    initElements() {
        // 输入元素
        this.promptInput = document.getElementById('promptInput');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.voiceBtnText = document.getElementById('voiceBtnText');
        this.modelSelect = document.getElementById('modelSelect');
        this.qualitySelect = document.getElementById('qualitySelect');
        
        // 高级设置
        this.temperatureRange = document.getElementById('temperatureRange');
        this.temperatureValue = document.getElementById('temperatureValue');
        this.maxTokensInput = document.getElementById('maxTokens');
        
        // 按钮和操作
        this.generateBtn = document.getElementById('generateBtn');
        this.generateBtnText = document.getElementById('generateBtnText');
        this.copyCodeBtn = document.getElementById('copyCodeBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.saveBtn = document.getElementById('saveBtn');
        
        // 结果显示
        this.statusCard = document.getElementById('statusCard');
        this.statusTitle = document.getElementById('statusTitle');
        this.statusMessage = document.getElementById('statusMessage');
        this.codeCard = document.getElementById('codeCard');
        this.videoCard = document.getElementById('videoCard');
        this.errorCard = document.getElementById('errorCard');
        this.generatedCode = document.getElementById('generatedCode');
        this.previewVideo = document.getElementById('previewVideo');
        this.videoInfo = document.getElementById('videoInfo');
        this.errorMessage = document.getElementById('errorMessage');
        
        // 模态框和保存
        this.saveModal = document.getElementById('saveModal');
        this.saveFilename = document.getElementById('saveFilename');
        this.saveDirectory = document.getElementById('saveDirectory');
        this.confirmSaveBtn = document.getElementById('confirmSaveBtn');
        
        // Toast通知
        this.toast = document.getElementById('toast');
        this.toastTitle = document.getElementById('toastTitle');
        this.toastMessage = document.getElementById('toastMessage');
        this.toastIcon = document.getElementById('toastIcon');
        
        // 字符计数
        this.charCount = document.getElementById('charCount');
        
        // 状态指示器
        this.panelIndicator = document.querySelector('.panel-indicator');
    }

    /**
     * 初始化事件监听器
     */
    initEventListeners() {
        // 主要按钮事件
        this.generateBtn?.addEventListener('click', () => this.generateAnimation());
        this.voiceBtn?.addEventListener('click', () => this.toggleVoiceRecording());
        this.copyCodeBtn?.addEventListener('click', () => this.copyCode());
        this.downloadBtn?.addEventListener('click', () => this.downloadVideo());
        this.saveBtn?.addEventListener('click', () => this.showSaveModal());
        this.confirmSaveBtn?.addEventListener('click', () => this.saveVideo());

        // 输入变化事件
        this.promptInput?.addEventListener('input', () => this.updateCharCount());
        this.temperatureRange?.addEventListener('input', (e) => {
            this.temperatureValue.textContent = e.target.value;
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.generateAnimation();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.toggleVoiceRecording();
                        break;
                }
            }
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isRecording) {
                this.stopVoiceRecording();
            }
        });
    }

    /**
     * 初始化语音识别
     */
    initSpeechRecognition() {
        // 检查MediaRecorder支持
        const hasMediaRecorder = 'MediaRecorder' in window;
        
        if (!hasMediaRecorder) {
            this.showToast('语音识别不可用', '您的浏览器不支持语音录制功能', 'warning');
            this.voiceBtn.disabled = true;
            return;
        }

        console.log('🎤 使用MediaRecorder + 通义千问-Omni语音识别');
    }

    /**
     * 初始化动画效果
     */
    initAnimations() {
        // 为卡片添加入场动画
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });

        document.querySelectorAll('.control-panel, .result-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'all 0.6s ease-out';
            observer.observe(el);
        });
    }

    /**
     * 更新字符计数
     */
    updateCharCount() {
        if (this.charCount && this.promptInput) {
            const count = this.promptInput.value.length;
            this.charCount.textContent = count;
            
            // 根据字符数量改变颜色
            if (count > 500) {
                this.charCount.style.color = 'var(--warning)';
            } else if (count > 1000) {
                this.charCount.style.color = 'var(--error)';
            } else {
                this.charCount.style.color = 'var(--text-muted)';
            }
        }
    }

    /**
     * 更新面板状态指示器
     */
    updatePanelIndicator(status, text) {
        if (!this.panelIndicator) return;
        
        const dot = this.panelIndicator.querySelector('.indicator-dot');
        const statusText = this.panelIndicator.querySelector('span') || 
                          this.panelIndicator.lastChild;
        
        // 移除所有状态类
        dot.className = 'indicator-dot';
        
        switch (status) {
            case 'ready':
                dot.style.background = 'var(--success)';
                break;
            case 'recording':
                dot.style.background = 'var(--error)';
                break;
            case 'generating':
                dot.style.background = 'var(--warning)';
                break;
            case 'error':
                dot.style.background = 'var(--error)';
                break;
        }
        
        if (statusText) {
            statusText.textContent = text;
        }
    }

    /**
     * 切换语音录制状态
     */
    toggleVoiceRecording() {
        if (this.isRecording || this.realtimeRecording) {
            this.stopVoiceRecording();
        } else {
            // 检查是否按住Shift键启用实时模式
            this.isRealtimeMode = event && (event.shiftKey || event.ctrlKey);
            this.startVoiceRecording();
        }
    }

    /**
     * 开始语音录制
     */
    async startVoiceRecording() {
        if (this.isRealtimeMode) {
            console.log('🎤 启动实时语音识别模式');
            this.showToast('实时识别', '通义千问-Omni实时语音识别已启动', 'info');
            await this.startRealtimeRecording();
        } else {
            await this.startMediaRecorderRecording();
        }
    }

    /**
     * 使用MediaRecorder开始录音
     */
    async startMediaRecorderRecording() {
        try {
            // 获取麦克风权限
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });

            // 配置MediaRecorder - 优化音频格式选择
            let options = {};
            
            // 按优先级尝试音频格式
            const preferredTypes = [
                'audio/wav',
                'audio/webm;codecs=opus',
                'audio/webm',
                'audio/ogg;codecs=opus',
                'audio/mp4',
                'audio/mpeg'
            ];
            
            for (const type of preferredTypes) {
                if (MediaRecorder.isTypeSupported(type)) {
                    options.mimeType = type;
                    console.log(`✅ 使用音频格式: ${type}`);
                    break;
                }
            }
            
            // 设置音频比特率
            if (options.mimeType) {
                options.audioBitsPerSecond = 16000;
            }

            this.mediaRecorder = new MediaRecorder(stream, options);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    console.log(`🎤 收集音频片段: ${event.data.size} bytes`);
                }
            };

            this.mediaRecorder.onstop = async () => {
                console.log('🎤 录音结束，开始处理...');
                await this.processRecordedAudio();
                
                // 停止所有音轨
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.onerror = (event) => {
                console.error('🎤 录音错误:', event.error);
                this.showToast('录音失败', '录音过程中发生错误', 'error');
                this.stopVoiceRecording();
            };

            // 开始录音
            this.mediaRecorder.start(250);
            this.isRecording = true;
            this.voiceBtn.classList.add('recording');
            this.voiceBtnText.textContent = '停止录音';
            this.updatePanelIndicator('recording', '录音中...');
            this.addVoiceWaveAnimation();

            console.log('🎤 通义千问-Omni录音开始，格式:', options.mimeType || 'default');

        } catch (error) {
            console.error('🎤 启动录音失败:', error);
            this.showToast('录音失败', '无法访问麦克风或启动录音', 'error');
        }
    }

    /**
     * 启动实时语音识别
     */
    async startRealtimeRecording() {
        try {
            // 获取麦克风权限
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });

            // 配置MediaRecorder用于实时录制
            let options = {};
            
            const realtimeTypes = [
                'audio/wav',
                'audio/webm;codecs=opus', 
                'audio/webm',
                'audio/ogg;codecs=opus'
            ];
            
            for (const type of realtimeTypes) {
                if (MediaRecorder.isTypeSupported(type)) {
                    options.mimeType = type;
                    console.log(`🎤 实时识别使用格式: ${type}`);
                    break;
                }
            }
            
            if (options.mimeType) {
                options.audioBitsPerSecond = 16000;
            }

            this.mediaRecorder = new MediaRecorder(stream, options);
            this.realtimeChunks = [];
            this.realtimeSessionId = this.generateSessionId();
            
            console.log(`🎤 实时识别会话ID: ${this.realtimeSessionId}`);

            this.mediaRecorder.ondataavailable = async (event) => {
                if (event.data && event.data.size > 0) {
                    this.realtimeChunks.push(event.data);
                    console.log(`🎤 实时音频片段: ${event.data.size} bytes`);
                    
                    // 实时处理音频片段
                    await this.processRealtimeAudioChunk(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                console.log('🎤 实时录音结束');
                await this.finalizeRealtimeRecognition();
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.onerror = (event) => {
                console.error('🎤 实时录音错误:', event.error);
                this.showToast('录音失败', '实时录音过程中发生错误', 'error');
                this.stopVoiceRecording();
            };

            // 开始实时录音
            this.mediaRecorder.start(300);
            this.realtimeRecording = true;
            this.voiceBtn.classList.add('recording', 'realtime');
            this.voiceBtnText.textContent = '实时识别中...';
            this.updatePanelIndicator('realtime', '通义千问-Omni实时识别中...');
            this.addVoiceWaveAnimation();

            console.log('🎤 通义千问-Omni实时语音识别开始');

        } catch (error) {
            console.error('🎤 启动实时录音失败:', error);
            this.showToast('录音失败', '无法访问麦克风或启动实时录音', 'error');
        }
    }

    /**
     * 处理实时音频片段
     */
    async processRealtimeAudioChunk(audioBlob) {
        try {
            if (audioBlob.size < 50) {
                console.debug('跳过过小的音频片段:', audioBlob.size);
                return;
            }

            const base64Audio = await this.blobToBase64(audioBlob);
            
            // 发送到实时语音识别API
            const response = await fetch('/api/realtime-speech-to-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio_chunk: base64Audio,
                    session_id: this.realtimeSessionId,
                    is_final: false
                })
            });

            const result = await response.json();
            console.log('🎤 实时识别结果:', result);

            if (result.success && result.text && result.text.trim()) {
                // 实时更新文本框内容
                this.updateRealtimeText(result);
            }

        } catch (error) {
            console.debug('实时音频处理错误:', error);
        }
    }

    /**
     * 完成实时语音识别
     */
    async finalizeRealtimeRecognition() {
        try {
            if (this.realtimeChunks.length === 0) {
                console.log('🎤 没有音频片段，跳过最终识别');
                return;
            }

            console.log(`🎤 合并 ${this.realtimeChunks.length} 个音频片段进行最终识别`);

            // 合并所有音频片段
            const finalBlob = new Blob(this.realtimeChunks, { 
                type: this.mediaRecorder.mimeType || 'audio/webm' 
            });
            const base64Audio = await this.blobToBase64(finalBlob);

            // 发送最终识别请求
            const response = await fetch('/api/realtime-speech-to-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio_chunk: base64Audio,
                    session_id: this.realtimeSessionId,
                    is_final: true
                })
            });

            const result = await response.json();
            console.log('🎤 最终识别结果:', result);

            if (result.success && result.text && result.text.trim()) {
                // 清理临时标记并使用最终识别结果
                let finalText = result.text.replace(/\[识别中.*?\]/g, '').trim();
                this.promptInput.value = finalText;
                this.updateCharCount();
                
                this.showToast('🤖 通义千问-Omni识别完成', finalText, 'success');
                console.log('🎤 最终文本:', finalText);
            } else {
                console.log('🎤 最终识别失败或无结果');
                // 清理临时标记
                this.promptInput.value = this.promptInput.value.replace(/\[识别中.*?\]/g, '').trim();
                this.updateCharCount();
            }

        } catch (error) {
            console.error('🎤 最终识别处理失败:', error);
            // 清理临时标记
            this.promptInput.value = this.promptInput.value.replace(/\[识别中.*?\]/g, '').trim();
            this.updateCharCount();
        }
    }

    /**
     * 更新实时识别的文本显示
     */
    updateRealtimeText(result) {
        if (result.success && result.text) {
            const recognizedText = result.text.trim();
            
            // 如果是部分结果，显示实时效果
            if (result.partial) {
                // 在原有文本基础上显示实时识别结果
                const currentText = this.promptInput.value.replace(/\[识别中\.\.\.\].*$/, '').trim();
                this.promptInput.value = currentText + (currentText ? ' ' : '') + `[识别中...] ${recognizedText}`;
                
                console.log(`🤖 通义千问-Omni实时识别: ${recognizedText}`);
            } else {
                // 最终结果，清理并设置最终文本
                const currentText = this.promptInput.value.replace(/\[识别中\.\.\.\].*$/, '').trim();
                this.promptInput.value = currentText + (currentText ? ' ' : '') + recognizedText;
                
                // 显示最终结果通知
                const recognizedLength = recognizedText.length;
                const displayText = recognizedLength > 30 ? 
                    recognizedText.substring(0, 30) + '...' : recognizedText;
                
                this.showToast(
                    '🤖 通义千问-Omni识别成功', 
                    `"${displayText}"${result.method ? ` (${result.method})` : ''}`, 
                    'success'
                );
                
                console.log('✅ 通义千问-Omni识别完成:', recognizedText);
            }
            
            this.updateCharCount();
            
            // 自动滚动到输入框末尾
            this.promptInput.scrollTop = this.promptInput.scrollHeight;
            this.promptInput.setSelectionRange(this.promptInput.value.length, this.promptInput.value.length);
        } else if (!result.success) {
            // 显示错误
            const errorMsg = result.error || '实时识别失败';
            console.error('🔴 通义千问-Omni实时识别错误:', errorMsg);
            
            // 清理识别中的标记
            this.promptInput.value = this.promptInput.value.replace(/\[识别中\.\.\.\].*$/, '').trim();
            this.updateCharCount();
        }
    }

    /**
     * 生成会话ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * 处理录制的音频
     */
    async processRecordedAudio() {
        try {
            if (this.audioChunks.length === 0) {
                this.showToast('录音失败', '没有录制到音频数据', 'error');
                return;
            }

            // 创建音频Blob
            const audioBlob = new Blob(this.audioChunks, { 
                type: this.mediaRecorder.mimeType || 'audio/webm' 
            });

            console.log(`🎤 音频大小: ${audioBlob.size} bytes, 类型: ${audioBlob.type}`);

            if (audioBlob.size < 500) {
                this.showToast('录音失败', '录音时间太短，请重新录制', 'warning');
                return;
            }

            // 转换为base64
            const base64Audio = await this.blobToBase64(audioBlob);
            
            // 发送到服务端进行语音识别
            this.showToast('处理中', '通义千问-Omni正在识别语音内容...', 'info');
            
            const response = await fetch('/api/speech-to-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio_data: base64Audio
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('🎤 通义千问-Omni识别结果:', result);

            if (result.success && result.text && result.text.trim()) {
                // 将识别的文本设置到输入框
                const recognizedText = result.text.trim();
                
                // 检查是否需要追加到现有文本
                const currentText = this.promptInput.value.trim();
                let newText;
                
                if (currentText && !currentText.includes(recognizedText)) {
                    // 如果有现有文本且不重复，则追加
                    newText = currentText + ' ' + recognizedText;
                } else {
                    // 否则直接设置
                    newText = recognizedText;
                }
                
                this.promptInput.value = newText;
                this.updateCharCount();
                
                // 显示识别结果
                const recognizedLength = recognizedText.length;
                const displayText = recognizedLength > 30 ? 
                    recognizedText.substring(0, 30) + '...' : recognizedText;
                
                this.showToast(
                    '🤖 通义千问-Omni识别成功', 
                    `"${displayText}"${result.method ? ` (${result.method})` : ''}`, 
                    'success'
                );
                
                // 自动聚焦到输入框末尾
                this.promptInput.focus();
                this.promptInput.setSelectionRange(this.promptInput.value.length, this.promptInput.value.length);
                
            } else {
                const errorMsg = result.error || '语音识别失败';
                this.showToast(
                    '语音识别失败', 
                    `错误: ${errorMsg}`, 
                    'error'
                );
                console.error('通义千问-Omni识别失败:', result);
            }

        } catch (error) {
            console.error('🎤 音频处理失败:', error);
            // 确保错误消息是字符串
            const errorMessage = typeof error === 'string' ? error : 
                                  error.message || 
                                  JSON.stringify(error) || 
                                  '音频处理过程中发生未知错误';
            this.showToast('处理失败', `语音识别处理异常: ${errorMessage}`, 'error');
        }
    }

    /**
     * 将Blob转换为Base64
     */
    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * 停止语音录制
     */
    stopVoiceRecording() {
        this.isRecording = false;
        this.realtimeRecording = false;
        this.voiceBtn.classList.remove('recording', 'realtime');
        this.voiceBtnText.textContent = '语音输入';
        this.updatePanelIndicator('ready', 'Ready');
        
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
        }
        
        // 清理实时识别相关状态
        if (this.realtimeTimer) {
            clearTimeout(this.realtimeTimer);
            this.realtimeTimer = null;
        }
        
        // 清理会话ID
        this.realtimeSessionId = null;
        this.isRealtimeMode = false;
        
        // 移除波浪动画
        const waveContainer = document.querySelector('.voice-wave');
        if (waveContainer) {
            waveContainer.remove();
        }
    }

    /**
     * 添加语音波形动画
     */
    addVoiceWaveAnimation() {
        const waves = this.voiceBtn.querySelectorAll('.voice-wave span');
        waves.forEach((wave, index) => {
            wave.style.animationDelay = `${index * 0.1}s`;
        });
    }

    /**
     * 生成动画
     */
    async generateAnimation() {
        const prompt = this.promptInput.value.trim();
        
        if (!prompt) {
            this.showToast('输入为空', '请输入动画描述', 'warning');
            this.promptInput.focus();
            return;
        }

        this.setGeneratingState(true);
        this.hideAllResults();
        this.showStatus('正在生成代码...', '请稍等片刻，AI正在为您创作代码');
        this.updatePanelIndicator('generating', '生成中...');

        try {
            const requestData = {
                prompt: prompt,
                model: this.modelSelect.value,
                quality: this.qualitySelect.value,
                temperature: parseFloat(this.temperatureRange.value),
                max_tokens: parseInt(this.maxTokensInput.value)
            };

            console.log('📤 发送生成请求:', requestData);

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('📥 收到响应:', result);

            if (result.success) {
                await this.handleSuccessResponse(result);
            } else {
                throw new Error(result.error || '生成失败');
            }

        } catch (error) {
            console.error('❌ 生成失败:', error);
            this.handleError(error.message || '生成过程中发生未知错误');
        } finally {
            this.setGeneratingState(false);
            this.updatePanelIndicator('ready', 'Ready');
        }
    }

    /**
     * 处理成功响应
     */
    async handleSuccessResponse(result) {
        // 显示生成的代码
        this.showCode(result.code);
        this.showToast('代码生成成功', '正在渲染视频...', 'success');
        
        // 更新状态
        this.showStatus('正在渲染视频...', '代码生成完成，正在创建动画视频');

        // 如果有视频路径，显示视频
        if (result.video_path) {
            this.currentVideoPath = result.video_path;
            await this.showVideo(result.video_path, result.video_info);
            this.showToast('动画生成完成', '您的数学动画已准备就绪', 'success');
        }

        this.hideStatus();
    }

    /**
     * 处理错误
     */
    handleError(errorMessage) {
        this.hideStatus();
        this.showError(errorMessage);
        this.showToast('生成失败', errorMessage, 'error');
    }

    /**
     * 设置生成状态
     */
    setGeneratingState(isGenerating) {
        if (isGenerating) {
            this.generateBtn.classList.add('loading');
            this.generateBtn.disabled = true;
            this.generateBtnText.textContent = '生成中...';
        } else {
            this.generateBtn.classList.remove('loading');
            this.generateBtn.disabled = false;
            this.generateBtnText.textContent = '生成动画';
        }
    }

    /**
     * 显示状态卡片
     */
    showStatus(title, message) {
        this.statusTitle.textContent = title;
        this.statusMessage.textContent = message;
        this.statusCard.style.display = 'block';
        
        // 添加入场动画
        setTimeout(() => {
            this.statusCard.style.opacity = '1';
            this.statusCard.style.transform = 'translateY(0)';
        }, 100);
    }

    /**
     * 隐藏状态卡片
     */
    hideStatus() {
        this.statusCard.style.display = 'none';
    }

    /**
     * 显示代码
     */
    showCode(code) {
        this.generatedCode.textContent = code;
        
        // 触发Prism.js语法高亮
        if (window.Prism) {
            Prism.highlightElement(this.generatedCode);
        }
        
        this.codeCard.style.display = 'block';
        
        // 添加入场动画
        setTimeout(() => {
            this.codeCard.style.opacity = '1';
            this.codeCard.style.transform = 'translateY(0)';
        }, 200);
    }

    /**
     * 显示视频
     */
    async showVideo(videoPath, videoInfo = null) {
        // 构建完整的视频URL - 智能处理路径前缀
        let videoUrl;
        if (videoPath.startsWith('http')) {
            // 已经是完整URL
            videoUrl = videoPath;
        } else if (videoPath.startsWith('outputs/')) {
            // 已经包含outputs前缀，直接使用
            videoUrl = `/${videoPath}`;
        } else {
            // 需要添加outputs前缀
            videoUrl = `/outputs/${videoPath}`;
        }
        
        console.log(`📹 视频URL: ${videoUrl}`);
        this.previewVideo.src = videoUrl;
        
        // 设置视频信息
        if (videoInfo) {
            this.videoInfo.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span><i class="bi bi-file-earmark-play me-1"></i>${videoInfo.filename || '动画文件'}</span>
                    <span><i class="bi bi-clock me-1"></i>${videoInfo.duration || '未知'}秒</span>
                </div>
            `;
        }

        this.videoCard.style.display = 'block';
        
        // 添加入场动画
        setTimeout(() => {
            this.videoCard.style.opacity = '1';
            this.videoCard.style.transform = 'translateY(0)';
        }, 400);

        // 等待视频加载
        return new Promise((resolve) => {
            this.previewVideo.onloadeddata = () => {
                console.log('📹 视频加载完成');
                resolve();
            };
        });
    }

    /**
     * 显示错误
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorCard.style.display = 'block';
        
        // 添加入场动画
        setTimeout(() => {
            this.errorCard.style.opacity = '1';
            this.errorCard.style.transform = 'translateY(0)';
        }, 100);
    }

    /**
     * 隐藏所有结果卡片
     */
    hideAllResults() {
        [this.statusCard, this.codeCard, this.videoCard, this.errorCard].forEach(card => {
            if (card) {
                card.style.display = 'none';
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            }
        });
    }

    /**
     * 复制代码到剪贴板
     */
    async copyCode() {
        try {
            const code = this.generatedCode.textContent;
            await navigator.clipboard.writeText(code);
            
            // 更新按钮状态
            const originalContent = this.copyCodeBtn.innerHTML;
            this.copyCodeBtn.innerHTML = '<i class="bi bi-check2"></i><span>已复制</span>';
            this.copyCodeBtn.classList.add('success');
            
            setTimeout(() => {
                this.copyCodeBtn.innerHTML = originalContent;
                this.copyCodeBtn.classList.remove('success');
            }, 2000);
            
            this.showToast('复制成功', '代码已复制到剪贴板', 'success');
        } catch (error) {
            console.error('复制失败:', error);
            this.showToast('复制失败', '无法复制到剪贴板', 'error');
        }
    }

    /**
     * 下载视频
     */
    downloadVideo() {
        if (!this.currentVideoPath) {
            this.showToast('下载失败', '没有可下载的视频', 'error');
            return;
        }

        try {
            const link = document.createElement('a');
            link.href = this.previewVideo.src;
            link.download = `manim_animation_${Date.now()}.mp4`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showToast('下载开始', '视频下载已开始', 'success');
        } catch (error) {
            console.error('下载失败:', error);
            this.showToast('下载失败', '无法下载视频文件', 'error');
        }
    }

    /**
     * 显示保存模态框
     */
    showSaveModal() {
        if (!this.currentVideoPath) {
            this.showToast('保存失败', '没有可保存的视频', 'error');
            return;
        }

        // 设置默认文件名
        const timestamp = new Date().toISOString().slice(0, -8).replace(/[:-]/g, '');
        this.saveFilename.value = `数学动画_${timestamp}`;
        
        const modal = new bootstrap.Modal(this.saveModal);
        modal.show();
    }

    /**
     * 保存视频
     */
    async saveVideo() {
        const filename = this.saveFilename.value.trim();
        const directory = this.saveDirectory.value.trim();

        if (!filename) {
            this.showToast('文件名为空', '请输入文件名', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_path: this.currentVideoPath,
                    filename: filename,
                    directory: directory
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('保存成功', `文件已保存到：${result.saved_path}`, 'success');
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(this.saveModal);
                modal.hide();
            } else {
                throw new Error(result.error || '保存失败');
            }

        } catch (error) {
            console.error('保存失败:', error);
            this.showToast('保存失败', error.message, 'error');
        }
    }

    /**
     * 显示Toast通知
     */
    showToast(title, message, type = 'info') {
        this.toastTitle.textContent = title;
        this.toastMessage.textContent = message;
        
        // 设置图标和样式
        const iconMap = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        
        this.toastIcon.className = `bi ${iconMap[type] || iconMap.info}`;
        
        // 设置Toast颜色
        const toastHeader = this.toast.querySelector('.toast-header');
        const toastIcon = this.toast.querySelector('.toast-icon');
        
        toastHeader.className = 'toast-header border-0';
        toastIcon.className = 'toast-icon me-2';
        
        switch (type) {
            case 'success':
                toastIcon.style.background = 'var(--gradient-secondary)';
                break;
            case 'error':
                toastIcon.style.background = 'linear-gradient(135deg, var(--error), #dc2626)';
                break;
            case 'warning':
                toastIcon.style.background = 'linear-gradient(135deg, var(--warning), #d97706)';
                break;
            default:
                toastIcon.style.background = 'var(--gradient-primary)';
        }

        const toast = new bootstrap.Toast(this.toast);
        toast.show();
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.manimGPTApp = new ManimGPTApp();
    
    // 添加全局快捷键提示
    console.log(`
🚀 Manim-GPT 快捷键:
   Ctrl/Cmd + Enter: 生成动画
   Ctrl/Cmd + R: 语音输入
    `);
});

// 添加一些工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
} 
