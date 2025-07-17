<template>
  <div class="interview-practice-container">
    <!-- 未开始状态 -->
    <div v-if="!hasStarted" class="start-section">
      <div class="page-header">
        <h2 class="page-title">面试练习模式</h2>
        <p class="page-subtitle">AI陪练模式，可随时暂停思考，获得实时指导</p>
      </div>

      <!-- 设置面板 -->
      <div class="settings-panel glass-card">
        <h3>面试设置</h3>

        <el-form label-width="120px">
          <el-form-item label="选择岗位">
            <el-select v-model="settings.position" placeholder="请选择面试岗位" style="width: 100%">
              <el-option label="前端开发" value="frontend" />
              <el-option label="后端开发" value="backend" />
              <el-option label="产品经理" value="product" />
              <el-option label="UI设计师" value="design" />
              <el-option label="数据分析" value="data" />
              <el-option label="算法工程师" value="algorithm" />
            </el-select>
          </el-form-item>

          <el-form-item label="难度等级">
            <el-radio-group v-model="settings.difficulty">
              <el-radio label="junior">初级 - 适合0-2年经验</el-radio>
              <el-radio label="medium">中级 - 适合2-5年经验</el-radio>
              <el-radio label="senior">高级 - 适合5年以上经验</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="面试风格">
            <el-select v-model="settings.interviewStyle" placeholder="选择面试官风格" style="width: 100%">
              <el-option label="温和型 - 亲切友好，鼓励式提问" value="gentle" />
              <el-option label="严肃型 - 正式严谨，注重细节" value="serious" />
              <el-option label="挑战型 - 深入追问，压力测试" value="challenging" />
              <el-option label="随机型 - 系统随机选择风格" value="random" />
            </el-select>
          </el-form-item>

          <el-form-item label="虚拟面试官">
            <div class="avatar-selection">
              <div
                v-for="avatar in avatarOptions"
                :key="avatar.id"
                class="avatar-option"
                :class="{ selected: settings.avatarId === avatar.id }"
                @click="settings.avatarId = avatar.id"
              >
                <el-avatar :size="60" :src="avatar.image" />
                <div class="avatar-info">
                  <h5>{{ avatar.name }}</h5>
                  <p>{{ avatar.description }}</p>
                </div>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="练习时长">
            <el-slider
              v-model="settings.duration"
              :min="10"
              :max="60"
              :step="5"
              show-input
              :format-tooltip="(val) => `${val}分钟`"
            />
          </el-form-item>

          <el-form-item label="题目类型">
            <el-checkbox-group v-model="settings.questionTypes">
              <el-checkbox label="behavioral">行为面试题</el-checkbox>
              <el-checkbox label="technical">技术面试题</el-checkbox>
              <el-checkbox label="situational">情景面试题</el-checkbox>
              <el-checkbox label="project">项目经验题</el-checkbox>
              <el-checkbox label="stress">压力面试题</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="特殊设置">
            <el-checkbox-group v-model="settings.specialSettings">
              <el-checkbox label="realtime_hints">启用实时提示</el-checkbox>
              <el-checkbox label="expression_analysis">启用表情分析</el-checkbox>
              <el-checkbox label="voice_analysis">启用语音分析</el-checkbox>
              <el-checkbox label="auto_feedback">自动反馈模式</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>

        <div class="settings-actions">
          <button class="start-btn tech-button" @click="startPractice" :disabled="!canStart">
            <el-icon><VideoPlay /></el-icon>
            开始练习
          </button>
        </div>
      </div>

      <!-- 练习说明 -->
      <div class="practice-tips glass-card">
        <h3>练习模式特点</h3>
        <div class="tips-grid">
          <div class="tip-item">
            <el-icon :size="30" color="#67c23a"><CircleCheck /></el-icon>
            <h4>随时暂停</h4>
            <p>遇到困难可以暂停思考，不计入评分</p>
          </div>
          <div class="tip-item">
            <el-icon :size="30" color="#409eff"><Opportunity /></el-icon>
            <h4>AI提示</h4>
            <p>可以获取AI的回答建议和提示</p>
          </div>
          <div class="tip-item">
            <el-icon :size="30" color="#e6a23c"><ChatLineRound /></el-icon>
            <h4>实时反馈</h4>
            <p>每个问题结束后立即获得反馈</p>
          </div>
          <div class="tip-item">
            <el-icon :size="30" color="#f56c6c"><TrendCharts /></el-icon>
            <h4>进步追踪</h4>
            <p>记录练习数据，追踪能力提升</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 面试进行中 -->
    <div v-else class="interview-section">
      <!-- 顶部控制栏 -->
      <div class="control-bar glass-card">
        <div class="control-left">
          <el-tag type="success">练习模式</el-tag>
          <span class="question-progress">
            第 {{ currentQuestionIndex + 1 }} / {{ totalQuestions }} 题
          </span>
        </div>

        <div class="control-center">
          <div class="timer" :class="{ paused: isPaused }">
            <el-icon><Timer /></el-icon>
            <span>{{ formatTime(elapsedTime) }}</span>
          </div>
        </div>

        <div class="control-right">
          <el-button
            :type="isPaused ? 'success' : 'warning'"
            @click="togglePause"
          >
            <el-icon>
              <VideoPlay v-if="isPaused" />
              <VideoPause v-else />
            </el-icon>
            {{ isPaused ? '继续' : '暂停' }}
          </el-button>
          <el-button type="danger" @click="endPractice">
            结束练习
          </el-button>
        </div>
      </div>

      <!-- 视频区域 -->
      <div class="video-section">
        <div class="video-container glass-card">
          <video ref="videoRef" autoplay muted playsinline></video>
          <div v-if="!cameraEnabled" class="video-placeholder">
            <el-icon :size="60"><VideoCamera /></el-icon>
            <p>摄像头未开启</p>
            <el-button type="primary" size="small" @click="enableCamera">
              开启摄像头
            </el-button>
          </div>
        </div>

        <!-- AI面试官 -->
        <div class="interviewer-container glass-card">
          <div class="interviewer-avatar">
            <div class="avatar-3d" ref="avatarContainer"></div>
            <span class="interviewer-name">{{ currentAvatar.name }}</span>
            <span class="interview-style">{{ getStyleName(settings.interviewStyle) }}</span>
          </div>

          <div class="current-question">
            <h3>当前问题：</h3>
            <p>{{ currentQuestion.text }}</p>
            <div class="question-meta">
              <el-tag size="small" type="info">{{ currentQuestion.type }}</el-tag>
              <el-tag size="small" :type="getDifficultyType(currentQuestion.difficulty)">
                {{ currentQuestion.difficulty }}
              </el-tag>
            </div>
          </div>

          <!-- AI助手 -->
          <div v-if="showHint" class="ai-hint animate__animated animate__fadeIn">
            <h4><el-icon><Star /></el-icon> AI提示</h4>
            <p>{{ currentQuestion.hint }}</p>
          </div>

          <!-- 实时分析 -->
          <div v-if="settings.specialSettings.includes('realtime_hints') && isRecording" class="realtime-analysis">
            <h4>实时分析</h4>
            <div class="analysis-items">
              <div class="analysis-item" v-if="settings.specialSettings.includes('voice_analysis')">
                <span class="label">语速：</span>
                <span class="value" :class="voiceAnalysis.speed">{{ voiceAnalysis.speedText }}</span>
              </div>
              <div class="analysis-item" v-if="settings.specialSettings.includes('expression_analysis')">
                <span class="label">表情：</span>
                <span class="value" :class="expressionAnalysis.mood">{{ expressionAnalysis.moodText }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 回答控制 -->
      <div class="answer-controls glass-card">
        <div class="controls-main">
          <el-button
            v-if="!isRecording"
            type="primary"
            size="large"
            @click="startRecording"
          >
            <el-icon><Microphone /></el-icon>
            开始回答
          </el-button>
          <el-button
            v-else
            type="danger"
            size="large"
            @click="stopRecording"
          >
            <el-icon><VideoPause /></el-icon>
            结束回答
          </el-button>

          <el-button
            type="info"
            size="large"
            @click="getHint"
            :disabled="hintUsed"
          >
            <el-icon><Star /></el-icon>
            获取提示
          </el-button>

          <el-button
            size="large"
            @click="skipQuestion"
          >
            <el-icon><Right /></el-icon>
            跳过问题
          </el-button>
        </div>

        <!-- 录音状态 -->
        <div v-if="isRecording" class="recording-status">
          <span class="recording-dot"></span>
          正在录音...
        </div>
      </div>

      <!-- 实时反馈 -->
      <div v-if="currentFeedback" class="feedback-section glass-card animate__animated animate__fadeIn">
        <h3>AI反馈</h3>
        <div class="feedback-content">
          <div class="feedback-score">
            <el-rate
              v-model="currentFeedback.score"
              disabled
              show-score
              text-color="#ff9900"
            />
          </div>
          <div class="feedback-text">
            <div class="feedback-item">
              <strong>优点：</strong>
              <p>{{ currentFeedback.pros }}</p>
            </div>
            <div class="feedback-item">
              <strong>建议：</strong>
              <p>{{ currentFeedback.cons }}</p>
            </div>
            <div class="feedback-item">
              <strong>参考答案：</strong>
              <p>{{ currentFeedback.reference }}</p>
            </div>
          </div>
        </div>
        <div class="feedback-actions">
          <el-button type="primary" @click="nextQuestion">
            下一题
          </el-button>
          <el-button @click="repeatQuestion">
            重新回答
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as THREE from 'three'
import {
  CircleCheck,
  Opportunity,
  ChatLineRound,
  TrendCharts,
  Timer,
  VideoPlay,
  VideoPause,
  VideoCamera,
  User,
  Microphone,
  Right,
  Star
} from '@element-plus/icons-vue'
import apiService from '@/api/service.js'

const router = useRouter()

// ================================================================================================
// 🎯 第一部分：基础状态管理
// ================================================================================================

const hasStarted = ref(false)
const isPaused = ref(false)
const isRecording = ref(false)
const cameraEnabled = ref(false)
const showHint = ref(false)
const hintUsed = ref(false)

// 面试数据状态
const currentInterviewId = ref(null)
const currentQuestionData = ref(null)
const recordedAudioBlob = ref(null)
const recordedTranscript = ref('')
const recordingDuration = ref(0)

// 媒体相关状态
const mediaStream = ref(null)
const mediaRecorder = ref(null)
const audioChunks = ref([])

// ================================================================================================
// 🎮 第二部分：面试设置和配置
// ================================================================================================

const settings = ref({
  position: 'frontend',
  difficulty: 'medium',
  interviewStyle: 'gentle',
  avatarId: 1,
  duration: 30,
  questionTypes: ['behavioral', 'technical'],
  specialSettings: ['realtime_hints']
})

const avatarOptions = ref([
  {
    id: 1,
    name: '李面试官',
    description: '亲和力强，善于引导',
    image: '/avatars/interviewer-1.jpg',
    model: '/models/avatar-1.glb'
  },
  {
    id: 2,
    name: '张面试官',
    description: '经验丰富，专业严谨',
    image: '/avatars/interviewer-2.jpg',
    model: '/models/avatar-2.glb'
  },
  {
    id: 3,
    name: '王面试官',
    description: '技术专家，深度挖掘',
    image: '/avatars/interviewer-3.jpg',
    model: '/models/avatar-3.glb'
  }
])

// ================================================================================================
// 📊 第三部分：面试进度和状态
// ================================================================================================

const currentQuestionIndex = ref(0)
const totalQuestions = ref(5)
const currentQuestion = ref({
  text: '请做一下自我介绍，包括您的教育背景、工作经验和技能特长。',
  hint: '建议按照"个人信息-教育背景-项目经验-技能特长-职业规划"的结构来组织回答，时间控制在2-3分钟。',
  type: 'behavioral',
  difficulty: 'medium'
})
const currentFeedback = ref(null)

// 计时器相关
const elapsedTime = ref(0)
let timerInterval = null
let realtimeInterval = null

// ================================================================================================
// 🤖 第四部分：AI实时分析接口区域
// ================================================================================================

const voiceAnalysis = ref({
  speed: 'normal',
  speedText: '适中'
})

const expressionAnalysis = ref({
  mood: 'neutral',
  moodText: '自然'
})

/**
 * 实时语音分析处理
 *
 * 🤖 AI接口对接位置 - 语音质量分析
 * TODO: 队友在这里对接AI API，处理实时语音分析：
 * - 分析语速、音量、流畅度
 * - 识别语音中的停顿和语气
 * - 提供实时语音质量反馈
 */
const analyzeVoiceQuality = (audioData) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const analysis = await aiService.analyzeVoiceQuality({
  //     audioData: audioData,
  //     language: 'zh-CN',
  //     analysisType: 'realtime'
  //   })
  //   return {
  //     speed: analysis.speechRate,
  //     volume: analysis.volumeLevel,
  //     fluency: analysis.fluencyScore
  //   }
  // } catch (error) {
  //   return getDefaultVoiceAnalysis()
  // }

  // 当前使用模拟数据（AI对接后可删除）
  const speeds = ['slow', 'normal', 'fast']
  const speedTexts = ['偏慢', '适中', '偏快']
  const randomIndex = Math.floor(Math.random() * 3)

  return {
    speed: speeds[randomIndex],
    speedText: speedTexts[randomIndex]
  }
}

/**
 * 实时表情分析处理
 *
 * 🤖 AI接口对接位置 - 表情识别分析
 * TODO: 队友在这里对接AI API，处理实时表情分析：
 * - 分析面部表情和情绪状态
 * - 识别自信度和紧张程度
 * - 提供实时表情反馈
 */
const analyzeExpression = (videoFrame) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const analysis = await aiService.analyzeFacialExpression({
  //     videoFrame: videoFrame,
  //     analysisType: 'emotion',
  //     confidence: true
  //   })
  //   return {
  //     emotion: analysis.primaryEmotion,
  //     confidence: analysis.confidenceLevel
  //   }
  // } catch (error) {
  //   return getDefaultExpressionAnalysis()
  // }

  // 当前使用模拟数据（AI对接后可删除）
  const moods = ['confident', 'neutral', 'nervous']
  const moodTexts = ['自信', '自然', '紧张']
  const randomIndex = Math.floor(Math.random() * 3)

  return {
    mood: moods[randomIndex],
    moodText: moodTexts[randomIndex]
  }
}

/**
 * 语音转文字处理
 *
 * 🤖 AI接口对接位置 - 语音识别转换
 * TODO: 队友在这里对接AI API，将录音转换为文字：
 * - 支持中文语音识别
 * - 处理不同口音和语速
 * - 返回准确的文字转录
 */
const transcribeAudio = async (audioBlob) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const transcript = await aiService.speechToText({
  //     audioBlob: audioBlob,
  //     language: 'zh-CN',
  //     format: 'webm'
  //   })
  //   return transcript.text
  // } catch (error) {
  //   console.error('语音转文字失败:', error)
  //   return ''
  // }

  // 当前使用模拟数据（AI对接后可删除）
  return '这是模拟的语音转文字结果，用于测试。'
}

// ================================================================================================
// 🎥 第五部分：媒体设备管理
// ================================================================================================

const videoRef = ref(null)
const avatarContainer = ref(null)
let scene, camera, renderer, avatarMesh

const initMediaRecorder = async () => {
  try {
    if (mediaRecorder.value) {
      try {
        if (mediaRecorder.value.state === 'recording') {
          mediaRecorder.value.stop()
        }
        await new Promise(resolve => {
          const checkState = () => {
            if (mediaRecorder.value.state === 'inactive') {
              resolve()
            } else {
              setTimeout(checkState, 100)
            }
          }
          checkState()
        })
      } catch (e) {
        console.warn('清理录音器失败:', e)
      }
      mediaRecorder.value = null
    }

    let audioStream
    try {
      audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
    } catch (error) {
      throw error
    }

    let mimeType = null
    const supportedTypes = [
      'audio/webm',
      'audio/mp4',
      'audio/ogg',
      'audio/wav'
    ]

    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type
        break
      }
    }

    const options = mimeType ? { mimeType } : {}
    mediaRecorder.value = new MediaRecorder(audioStream, options)

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = async () => {
      if (audioChunks.value.length > 0) {
        const audioBlob = new Blob(audioChunks.value, {
          type: mimeType || 'audio/webm'
        })
        recordedAudioBlob.value = audioBlob

        // 🤖 AI接口调用：语音转文字
        recordedTranscript.value = await transcribeAudio(audioBlob)
      }
      audioChunks.value = []

      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop())
      }
    }

    mediaRecorder.value.onerror = (event) => {
      isRecording.value = false
      ElMessage.error('录音过程中出现错误：' + event.error.message)
    }

    return true

  } catch (error) {
    ElMessage.error('无法访问麦克风，请检查权限设置')
    return false
  }
}

const enableCamera = async () => {
  try {
    const videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      },
      audio: false
    })

    mediaStream.value = videoStream

    if (videoRef.value) {
      videoRef.value.srcObject = videoStream
      videoRef.value.onloadedmetadata = () => {
        cameraEnabled.value = true
      }
    }

    cameraEnabled.value = true
    ElMessage.success('摄像头已开启')

  } catch (error) {
    cameraEnabled.value = false

    if (error.name === 'NotAllowedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头')
    } else if (error.name === 'NotFoundError') {
      ElMessage.error('未找到摄像头设备')
    } else {
      ElMessage.error('无法访问摄像头：' + error.message)
    }
  }
}

// ================================================================================================
// 🎬 第六部分：3D虚拟人渲染
// ================================================================================================

const init3DAvatar = () => {
  if (!avatarContainer.value) return

  try {
    scene = new THREE.Scene()
    camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000)
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })

    const container = avatarContainer.value
    const size = Math.min(container.clientWidth, container.clientHeight)
    renderer.setSize(size, size)
    container.appendChild(renderer.domElement)

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(0, 1, 1)
    scene.add(directionalLight)

    const geometry = new THREE.CylinderGeometry(0.6, 0.8, 2, 8)
    const material = new THREE.MeshPhongMaterial({
      color: 0x4a90e2,
      transparent: true,
      opacity: 0.8
    })
    avatarMesh = new THREE.Mesh(geometry, material)
    scene.add(avatarMesh)

    camera.position.set(0, 0, 4)

    const animate = () => {
      requestAnimationFrame(animate)

      if (avatarMesh) {
        if (isRecording.value) {
          avatarMesh.scale.y = 1 + Math.sin(Date.now() * 0.01) * 0.05
          avatarMesh.rotation.y += 0.005
        } else {
          avatarMesh.scale.y = 1
          avatarMesh.rotation.y += 0.002
        }
      }

      renderer.render(scene, camera)
    }
    animate()

  } catch (error) {
    console.error('3D Avatar initialization failed:', error)
  }
}

// ================================================================================================
// 🎤 第七部分：录音控制功能
// ================================================================================================

const startRecording = async () => {
  try {
    if (isRecording.value) {
      return
    }

    const success = await initMediaRecorder()
    if (!success) {
      throw new Error('录音器初始化失败')
    }

    await new Promise(resolve => setTimeout(resolve, 100))

    if (mediaRecorder.value.state !== 'inactive') {
      throw new Error(`录音器状态异常: ${mediaRecorder.value.state}`)
    }

    recordedAudioBlob.value = null
    recordingDuration.value = 0
    audioChunks.value = []

    try {
      mediaRecorder.value.start(1000)
      isRecording.value = true
    } catch (startError) {
      throw startError
    }

    const recordingStartTime = Date.now()
    const recordingTimer = setInterval(() => {
      if (!isRecording.value) {
        clearInterval(recordingTimer)
        return
      }
      recordingDuration.value = Math.floor((Date.now() - recordingStartTime) / 1000)
    }, 1000)

    if (settings.value.specialSettings.includes('realtime_hints')) {
      startRealtimeAnalysis()
    }

    ElMessage.success('开始录音，请回答问题')

  } catch (error) {
    isRecording.value = false
    ElMessage.error('开始录音失败：' + error.message)
  }
}

const stopRecording = async () => {
  try {
    if (!isRecording.value) {
      return
    }

    if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
      mediaRecorder.value.stop()
    }

    isRecording.value = false
    stopRealtimeAnalysis()

    setTimeout(async () => {
      if (recordedAudioBlob.value && currentQuestionData.value) {
        await submitAnswer()
      }
    }, 500)

  } catch (error) {
    isRecording.value = false
    ElMessage.error('停止录音失败：' + error.message)
  }
}

// ================================================================================================
// 🤖 第八部分：实时分析处理接口区域
// ================================================================================================

/**
 * 开始实时分析
 *
 * 🤖 AI接口对接位置 - 实时音视频分析
 * TODO: 队友在这里对接AI API，进行实时分析：
 * - 实时语音质量分析
 * - 实时表情识别分析
 * - 将分析结果发送到后端保存
 */
const startRealtimeAnalysis = () => {
  realtimeInterval = setInterval(async () => {
    if (isRecording.value) {
      try {
        // 🤖 AI接口调用：获取实时音频数据进行分析
        const audioData = getCurrentAudioData()
        const voiceResult = analyzeVoiceQuality(audioData)
        voiceAnalysis.value = voiceResult

        // 🤖 AI接口调用：获取实时视频帧进行分析
        if (settings.value.specialSettings.includes('expression_analysis')) {
          const videoFrame = getCurrentVideoFrame()
          const expressionResult = analyzeExpression(videoFrame)
          expressionAnalysis.value = expressionResult
        }

        // 🤖 AI接口调用：发送实时分析数据到后端
        if (currentInterviewId.value) {
          await apiService.interview.submitRealtimeAnalysis(currentInterviewId.value, {
            audioLevel: getAudioLevel(),
            emotionType: expressionAnalysis.value.mood,
            eyeContactScore: getEyeContactScore(),
            speechSpeed: getSpeechSpeed(),
            voiceQuality: voiceResult,
            facialExpression: expressionAnalysis.value,
            timestamp: new Date().toISOString()
          })
        }

      } catch (error) {
        console.error('实时分析处理失败:', error)
      }
    }
  }, 2000)
}

const stopRealtimeAnalysis = () => {
  if (realtimeInterval) {
    clearInterval(realtimeInterval)
    realtimeInterval = null
  }
  voiceAnalysis.value = { speed: 'normal', speedText: '适中' }
  expressionAnalysis.value = { mood: 'neutral', moodText: '自然' }
}

// 辅助方法：获取当前音频数据
const getCurrentAudioData = () => {
  // TODO: 实现获取当前音频数据的逻辑
  return null
}

// 辅助方法：获取当前视频帧
const getCurrentVideoFrame = () => {
  // TODO: 实现获取当前视频帧的逻辑
  return null
}

const getAudioLevel = () => {
  return Math.random() * 100
}

const getCurrentEmotion = () => {
  return Math.random() > 0.5 ? 'confident' : 'neutral'
}

const getEyeContactScore = () => {
  return Math.random() * 100
}

const getSpeechSpeed = () => {
  return Math.random() * 200 + 100
}

// ================================================================================================
// 📋 第九部分：面试流程控制
// ================================================================================================

const startPractice = async () => {
  try {
    const hasResume = localStorage.getItem('userResume')
    if (!hasResume) {
      const confirm = await ElMessageBox.confirm(
        '检测到您还未上传简历，建议先上传简历以获得个性化的面试题目。是否继续？',
        '提示',
        {
          confirmButtonText: '继续练习',
          cancelButtonText: '去上传简历',
          type: 'warning'
        }
      ).catch(() => false)

      if (!confirm) {
        router.push('/dashboard/resume-manage')
        return
      }
    }

    const response = await apiService.interview.start({
      position: settings.value.position,
      difficulty: settings.value.difficulty,
      interviewStyle: settings.value.interviewStyle,
      avatarId: settings.value.avatarId,
      duration: settings.value.duration,
      questionTypes: settings.value.questionTypes,
      specialSettings: settings.value.specialSettings
    })

    currentInterviewId.value = response.data.interview_id
    currentQuestionData.value = response.data.first_question
    totalQuestions.value = response.data.total_questions

    if (currentQuestionData.value) {
      currentQuestion.value = {
        text: currentQuestionData.value.text,
        type: currentQuestionData.value.type,
        difficulty: currentQuestionData.value.difficulty,
        hint: currentQuestionData.value.hint || '建议按照结构化的方式来组织回答'
      }
    }

    hasStarted.value = true
    startTimer()

    nextTick(async () => {
      init3DAvatar()
      try {
        await enableCamera()
      } catch (error) {
        ElMessage.warning('媒体设备初始化失败，但面试可以继续')
      }
    })

    ElMessage.success('面试练习开始！')

  } catch (error) {
    ElMessage.error('开始练习失败：' + (error.response?.data?.detail || error.message))
  }
}

const submitAnswer = async () => {
  try {
    const answerData = {
      answerText: recordedTranscript.value || '',
      timeSpent: recordingDuration.value,
      usedHint: hintUsed.value
    }

    if (recordedAudioBlob.value && currentInterviewId.value && currentQuestionData.value) {
      const uploadResponse = await apiService.interview.uploadAudio(
        currentInterviewId.value,
        currentQuestionData.value.id,
        recordedAudioBlob.value
      )
      answerData.audioPath = uploadResponse.data.file_path
    }

    const answerResponse = await apiService.interview.submitAnswer(
      currentQuestionData.value.id,
      answerData
    )

    currentFeedback.value = {
      score: answerResponse.data.score,
      pros: answerResponse.data.ai_feedback,
      cons: answerResponse.data.improvement_tips?.join('；') || '',
      reference: '继续保持这种状态'
    }

    ElMessage.success('回答已提交，正在分析...')

  } catch (error) {
    ElMessage.error('提交答案失败：' + (error.response?.data?.detail || error.message))
  }
}

const togglePause = async () => {
  if (!currentInterviewId.value) return

  try {
    if (isPaused.value) {
      await apiService.interview.resumeInterview(currentInterviewId.value)
      isPaused.value = false
      ElMessage.success('面试已继续')
    } else {
      await apiService.interview.pauseInterview(currentInterviewId.value)
      isPaused.value = true
      ElMessage.info('面试已暂停，点击继续按钮恢复')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
  }
}

const getHint = async () => {
  if (!currentQuestionData.value) return

  try {
    const hintResponse = await apiService.interview.getQuestionHint(currentQuestionData.value.id)

    currentQuestion.value.hint = hintResponse.data.hint
    showHint.value = true
    hintUsed.value = true

    await apiService.interview.markHintUsed(currentQuestionData.value.id)

    ElMessage.info('已显示AI提示，本题将不计入综合评分')
  } catch (error) {
    ElMessage.error('获取提示失败：' + (error.response?.data?.detail || error.message))
  }
}

const skipQuestion = async () => {
  if (!currentInterviewId.value || !currentQuestionData.value) {
    ElMessage.error('缺少面试或题目数据')
    return
  }

  try {
    const response = await apiService.interview.skipQuestion(
      currentInterviewId.value,
      currentQuestionData.value.id
    )

    if (response.data && response.data.next_question) {
      currentQuestionData.value = response.data.next_question

      currentQuestion.value = {
        text: response.data.next_question.text,
        type: response.data.next_question.type,
        difficulty: response.data.next_question.difficulty,
        hint: response.data.next_question.hint || '建议按照结构化的方式来组织回答'
      }

      currentQuestionIndex.value++
      resetQuestionState()

      ElMessage.success('已跳过当前问题')
    } else {
      ElMessage.info('已是最后一题，面试即将结束')
      await endPractice()
    }
  } catch (error) {
    let errorMessage = '跳过问题失败'
    if (error.response?.data?.detail) {
      errorMessage += '：' + error.response.data.detail
    } else if (error.message) {
      errorMessage += '：' + error.message
    }
    ElMessage.error(errorMessage)
  }
}

const nextQuestion = async () => {
  if (!currentQuestionData.value) return

  try {
    const response = await apiService.interview.getNextQuestion(currentQuestionData.value.id)

    if (response.data) {
      currentQuestionData.value = response.data
      currentQuestionIndex.value++
      resetQuestionState()
      ElMessage.success('下一题已准备好')
    } else {
      await endPractice()
    }
  } catch (error) {
    ElMessage.error('获取下一题失败：' + (error.response?.data?.detail || error.message))
  }
}

const repeatQuestion = () => {
  resetQuestionState()
  ElMessage.info('可以重新回答当前问题')
}

const endPractice = async () => {
  const confirm = await ElMessageBox.confirm(
    '确定要结束本次练习吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)

  if (confirm) {
    try {
      if (currentInterviewId.value) {
        let response = null

        try {
          response = await apiService.interview.completeInterview(
            currentInterviewId.value,
            'normal'
          )
        } catch (primaryError) {
          try {
            response = await apiService.interview.endInterview(currentInterviewId.value)
          } catch (fallbackError) {
            throw primaryError
          }
        }

        ElMessage.success('练习结束，正在生成报告...')
        cleanupResources()
        router.push('/dashboard/interview-performance')
      } else {
        cleanupResources()
        router.push('/dashboard/interview-performance')
      }
    } catch (error) {
      cleanupResources()
      ElMessage.error('结束练习失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// ================================================================================================
// 🛠️ 第十部分：工具函数和资源管理
// ================================================================================================

const resetQuestionState = () => {
  currentFeedback.value = null
  showHint.value = false
  hintUsed.value = false
  recordedAudioBlob.value = null
  recordingDuration.value = 0

  if (isRecording.value) {
    stopRecording()
  }
}

const cleanupResources = () => {
  if (mediaRecorder.value) {
    if (mediaRecorder.value.state === 'recording') {
      try {
        mediaRecorder.value.stop()
      } catch (error) {
        console.error('停止录音器失败:', error)
      }
    }
    mediaRecorder.value = null
  }

  if (mediaStream.value) {
    try {
      mediaStream.value.getTracks().forEach(track => {
        track.stop()
      })
    } catch (error) {
      console.error('停止媒体轨道失败:', error)
    }
    mediaStream.value = null
  }

  if (videoRef.value) {
    videoRef.value.srcObject = null
  }

  cameraEnabled.value = false
  isRecording.value = false

  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  if (realtimeInterval) {
    clearInterval(realtimeInterval)
    realtimeInterval = null
  }

  if (renderer) {
    renderer.dispose()
    renderer = null
  }
}

const startTimer = () => {
  timerInterval = setInterval(() => {
    if (!isPaused.value) {
      elapsedTime.value++
    }
  }, 1000)
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// ================================================================================================
// 💫 第十一部分：计算属性和辅助函数
// ================================================================================================

const canStart = computed(() => {
  return settings.value.position &&
         settings.value.questionTypes.length > 0 &&
         settings.value.avatarId
})

const currentAvatar = computed(() => {
  return avatarOptions.value.find(avatar => avatar.id === settings.value.avatarId) || avatarOptions.value[0]
})

const getStyleName = (style) => {
  const styleMap = {
    gentle: '温和型',
    serious: '严肃型',
    challenging: '挑战型',
    random: '随机型'
  }
  return styleMap[style] || '温和型'
}

const getDifficultyType = (difficulty) => {
  const difficultyMap = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return difficultyMap[difficulty] || 'info'
}

// ================================================================================================
// 🔄 第十二部分：生命周期管理
// ================================================================================================

onUnmounted(() => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
  }
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  if (renderer) {
    renderer.dispose()
  }
})
</script>

<style scoped>
.interview-practice-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 开始页面样式 */
.start-section {
  max-width: 800px;
  margin: 0 auto;
}

.settings-panel {
  padding: 30px;
  margin-bottom: 30px;
}

.settings-panel h3 {
  font-size: 1.3rem;
  margin-bottom: 25px;
  color: var(--text-primary);
}

.avatar-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.avatar-option {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-option:hover {
  background: rgba(255, 255, 255, 0.08);
}

.avatar-option.selected {
  border-color: var(--primary-color);
  background: rgba(64, 158, 255, 0.1);
}

.avatar-info h5 {
  color: var(--text-primary);
  margin: 0 0 5px 0;
}

.avatar-info p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 13px;
}

.settings-actions {
  text-align: center;
  margin-top: 30px;
}

.start-btn {
  padding: 15px 50px;
  font-size: 1.1rem;
  background: var(--gradient-tech);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 练习说明 */
.practice-tips {
  padding: 30px;
}

.practice-tips h3 {
  font-size: 1.3rem;
  margin-bottom: 25px;
  color: var(--text-primary);
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
}

.tip-item {
  text-align: center;
}

.tip-item h4 {
  margin: 15px 0 10px;
  color: var(--text-primary);
}

.tip-item p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 面试进行中样式 */
.interview-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 控制栏 */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
}

.control-left,
.control-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.question-progress {
  color: var(--text-secondary);
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.timer.paused {
  color: var(--warning-color);
}

/* 视频区域 */
.video-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: 400px;
}

.video-container,
.interviewer-container {
  position: relative;
  overflow: hidden;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.video-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.video-placeholder p {
  margin: 15px 0;
}

/* AI面试官 */
.interviewer-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.interviewer-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
}

.avatar-3d {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
}

.interviewer-name {
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 600;
}

.interview-style {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.current-question h3 {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.current-question p {
  font-size: 1.1rem;
  color: var(--text-primary);
  line-height: 1.6;
  margin-bottom: 10px;
}

.question-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.ai-hint {
  margin-top: 20px;
  padding: 15px;
  background: rgba(103, 194, 58, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.ai-hint h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--secondary-color);
  margin-bottom: 10px;
}

.ai-hint p {
  color: var(--text-primary);
  line-height: 1.6;
}

.realtime-analysis {
  margin-top: 20px;
  padding: 15px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.realtime-analysis h4 {
  color: var(--primary-color);
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.analysis-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.analysis-item .label {
  color: var(--text-secondary);
}

.analysis-item .value {
  font-weight: 600;
}

.analysis-item .value.normal,
.analysis-item .value.neutral {
  color: var(--success-color);
}

.analysis-item .value.fast,
.analysis-item .value.slow,
.analysis-item .value.nervous {
  color: var(--warning-color);
}

.analysis-item .value.confident {
  color: var(--primary-color);
}

/* 回答控制 */
.answer-controls {
  padding: 25px;
  text-align: center;
}

.controls-main {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.recording-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--danger-color);
}

.recording-dot {
  width: 10px;
  height: 10px;
  background: var(--danger-color);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 反馈区域 */
.feedback-section {
  padding: 30px;
}

.feedback-section h3 {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.feedback-content {
  margin-bottom: 25px;
}

.feedback-score {
  margin-bottom: 20px;
}

.feedback-item {
  margin-bottom: 20px;
}

.feedback-item strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 8px;
}

.feedback-item p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.feedback-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .video-section {
    grid-template-columns: 1fr;
    height: auto;
  }

  .tips-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .avatar-selection {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .control-bar {
    flex-wrap: wrap;
    gap: 15px;
  }

  .controls-main {
    flex-wrap: wrap;
  }

  .tips-grid {
    grid-template-columns: 1fr;
  }

  .feedback-actions {
    flex-direction: column;
  }
}
</style>
