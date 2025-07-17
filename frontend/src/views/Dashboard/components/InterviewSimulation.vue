<template>
  <div class="interview-simulation-container">
    <!-- 未开始状态 -->
    <div v-if="!hasStarted" class="start-section">
      <div class="page-header">
        <h2 class="page-title">面试模拟模式</h2>
        <p class="page-subtitle">完全模拟真实面试场景，全程无中断，获得综合评测报告</p>
      </div>

      <!-- 设置面板 -->
      <div class="settings-panel glass-card">
        <h3>面试设置</h3>

        <el-form label-width="120px">
          <el-form-item label="面试公司">
            <el-select v-model="settings.company" placeholder="选择模拟的公司类型" style="width: 100%">
              <el-option label="互联网大厂" value="tech">
                <span style="float: left">互联网大厂</span>
                <span style="float: right; color: var(--text-secondary); font-size: 13px">
                  偏技术深度，节奏较快
                </span>
              </el-option>
              <el-option label="外企" value="foreign">
                <span style="float: left">外企</span>
                <span style="float: right; color: var(--text-secondary); font-size: 13px">
                  重视英语表达，注重软技能
                </span>
              </el-option>
              <el-option label="国企/事业单位" value="state">
                <span style="float: left">国企/事业单位</span>
                <span style="float: right; color: var(--text-secondary); font-size: 13px">
                  偏综合素质，稳重为主
                </span>
              </el-option>
              <el-option label="创业公司" value="startup">
                <span style="float: left">创业公司</span>
                <span style="float: right; color: var(--text-secondary); font-size: 13px">
                  看重潜力，灵活多变
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="面试岗位">
            <el-select v-model="settings.position" placeholder="请选择面试岗位" style="width: 100%">
              <el-option label="前端开发" value="frontend" />
              <el-option label="后端开发" value="backend" />
              <el-option label="算法工程师" value="algorithm" />
              <el-option label="产品经理" value="product" />
              <el-option label="UI设计师" value="design" />
              <el-option label="数据分析师" value="data" />
            </el-select>
          </el-form-item>

          <el-form-item label="面试轮次">
            <el-radio-group v-model="settings.round">
              <el-radio label="first">初试 - 基础能力考察</el-radio>
              <el-radio label="second">复试 - 深度技术面试</el-radio>
              <el-radio label="final">终面 - 综合素质评估</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="面试风格">
            <el-select v-model="settings.interviewStyle" placeholder="选择面试风格" style="width: 100%">
              <el-option label="标准模式 - 按公司惯例进行" value="standard" />
              <el-option label="压力模式 - 高强度快节奏" value="stress" />
              <el-option label="友好模式 - 轻松愉快氛围" value="friendly" />
              <el-option label="技术深挖 - 专注技术细节" value="technical" />
              <el-option label="行为面试 - 重点考察软技能" value="behavioral" />
            </el-select>
          </el-form-item>

          <el-form-item label="面试官配置">
            <div class="interviewer-config">
              <div
                v-for="interviewer in interviewerOptions"
                :key="interviewer.id"
                class="interviewer-option"
                :class="{ selected: settings.interviewerId === interviewer.id }"
                @click="settings.interviewerId = interviewer.id"
              >
                <el-avatar :size="50" :src="interviewer.avatar" />
                <div class="interviewer-details">
                  <h5>{{ interviewer.name }}</h5>
                  <p>{{ interviewer.role }}</p>
                  <div class="interviewer-tags">
                    <el-tag
                      v-for="tag in interviewer.specialties"
                      :key="tag"
                      size="small"
                      type="info"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="面试时长">
            <el-select v-model="settings.duration" style="width: 100%">
              <el-option :label="'30分钟 - 快速评估'" :value="30" />
              <el-option :label="'45分钟 - 标准面试'" :value="45" />
              <el-option :label="'60分钟 - 深度面试'" :value="60" />
              <el-option :label="'90分钟 - 全面评估'" :value="90" />
            </el-select>
          </el-form-item>

          <el-form-item label="评估重点">
            <el-checkbox-group v-model="settings.evaluationFocus">
              <el-checkbox label="technical">技术能力</el-checkbox>
              <el-checkbox label="communication">沟通表达</el-checkbox>
              <el-checkbox label="problem_solving">问题解决</el-checkbox>
              <el-checkbox label="leadership">领导力</el-checkbox>
              <el-checkbox label="cultural_fit">文化匹配</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>

        <div class="simulation-warning">
          <el-alert type="warning" :closable="false" show-icon>
            <template #title>
              模拟模式注意事项
            </template>
            <template #default>
              <ul>
                <li>面试过程不可暂停，请确保有充足时间和良好环境</li>
                <li>全程录音录像，用于后续详细分析</li>
                <li>系统将严格按照真实面试标准进行评估</li>
                <li>结束后生成专业的面试评测报告</li>
              </ul>
            </template>
          </el-alert>
        </div>

        <div class="settings-actions">
          <button
            class="start-btn tech-button"
            @click="startSimulation"
            :disabled="!canStart"
          >
            <el-icon><VideoPlay /></el-icon>
            开始模拟面试
          </button>
        </div>
      </div>
    </div>

    <!-- 面试进行中 -->
    <div v-else class="interview-main">
      <!-- 顶部状态栏 -->
      <div class="status-bar glass-card">
        <div class="interview-info">
          <el-tag type="danger">模拟面试</el-tag>
          <span class="company-info">{{ getCompanyName(settings.company) }} - {{ settings.position }}</span>
          <span class="round-info">{{ getRoundName(settings.round) }}</span>
        </div>

        <div class="time-display">
          <el-icon><Timer /></el-icon>
          <span class="time-text">{{ formatTime(elapsedTime) }} / {{ formatTime(totalTime) }}</span>
          <el-progress
            :percentage="timeProgress"
            :color="getTimeColor(timeProgress)"
            :show-text="false"
            style="width: 200px; margin-left: 15px;"
          />
        </div>

        <div class="emergency-controls">
          <el-button type="danger" size="small" @click="emergencyExit">
            紧急退出
          </el-button>
        </div>
      </div>

      <!-- 主要面试区域 -->
      <div class="interview-area">
        <!-- 左侧：虚拟面试官 -->
        <div class="interviewer-section">
          <!-- 3D虚拟人容器 -->
          <div class="virtual-interviewer glass-card">
            <div ref="virtualHumanContainer" class="virtual-human-canvas"></div>
            <div class="interviewer-info-bar">
              <div class="interviewer-status">
                <div class="status-indicator" :class="{ speaking: isSpeaking, listening: isListening }"></div>
                <span>{{ currentInterviewer.name }}</span>
              </div>
              <div class="interview-phase">
                <el-tag size="small" :type="getPhaseType(currentPhase)">
                  {{ getPhaseTitle(currentPhase) }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 当前问题显示 -->
          <div class="question-display glass-card">
            <div class="question-header">
              <el-icon><QuestionFilled /></el-icon>
              <span>面试问题 {{ currentQuestionIndex + 1 }}/{{ totalQuestions }}</span>
            </div>
            <div class="question-content">
              <p class="question-text">{{ currentQuestion.text }}</p>
              <div class="question-context" v-if="currentQuestion.context">
                <el-tag size="small" type="info">{{ currentQuestion.context }}</el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：用户视频和控制 -->
        <div class="candidate-section">
          <!-- 用户视频 -->
          <div class="user-video-container glass-card">
            <video ref="userVideoRef" autoplay muted playsinline></video>
            <div v-if="!cameraReady" class="video-setup">
              <el-icon :size="60"><VideoCamera /></el-icon>
              <p>请开启摄像头和麦克风</p>
              <el-button type="primary" @click="setupCamera">
                设置设备
              </el-button>
            </div>

            <!-- 录制状态指示 -->
            <div v-if="isRecording" class="recording-indicator">
              <div class="rec-dot"></div>
              <span>REC</span>
            </div>
          </div>

          <!-- 回答控制区 -->
          <div class="answer-control glass-card">
            <div v-if="!isAnswering" class="waiting-state">
              <h4>{{ waitingMessage }}</h4>
              <p>{{ waitingDescription }}</p>
              <el-button
                v-if="canStartAnswer"
                type="primary"
                size="large"
                @click="startAnswer"
              >
                <el-icon><Microphone /></el-icon>
                开始回答
              </el-button>
            </div>

            <div v-else class="answering-state">
              <div class="answer-timer">
                <el-progress
                  type="circle"
                  :percentage="answerProgress"
                  :width="80"
                  :stroke-width="6"
                  :color="getAnswerProgressColor(answerProgress)"
                >
                  <template #default="{ percentage }">
                    <span class="timer-text">{{ formatTime(answerTime) }}</span>
                  </template>
                </el-progress>
              </div>

              <div class="answer-controls">
                <el-button
                  type="success"
                  @click="finishAnswer"
                  :disabled="answerTime < 10"
                >
                  <el-icon><Check /></el-icon>
                  完成回答
                </el-button>
                <p class="answer-hint">
                  {{ answerTime < 10 ? '请至少回答10秒' : '点击完成回答或继续表达' }}
                </p>
              </div>
            </div>
          </div>

          <!-- 实时反馈 -->
          <div class="realtime-feedback glass-card">
            <h4>实时状态</h4>
            <div class="feedback-items">
              <div class="feedback-item">
                <span class="label">语音音量：</span>
                <el-progress
                  :percentage="audioLevel"
                  :show-text="false"
                  :stroke-width="8"
                  :color="audioLevel > 20 ? '#67c23a' : '#f56c6c'"
                />
              </div>
              <div class="feedback-item">
                <span class="label">表情状态：</span>
                <span class="status-text" :class="emotionAnalysis.type">
                  {{ emotionAnalysis.text }}
                </span>
              </div>
              <div class="feedback-item">
                <span class="label">眼神接触：</span>
                <span class="status-text" :class="eyeContactStatus.type">
                  {{ eyeContactStatus.text }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 面试进度条 -->
      <div class="progress-tracker glass-card">
        <div class="progress-steps">
          <div
            v-for="(phase, index) in interviewPhases"
            :key="phase.id"
            class="progress-step"
            :class="{
              completed: index < currentPhaseIndex,
              active: index === currentPhaseIndex,
              upcoming: index > currentPhaseIndex
            }"
          >
            <div class="step-circle">
              <el-icon v-if="index < currentPhaseIndex"><Check /></el-icon>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span class="step-label">{{ phase.title }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 面试结束弹窗 -->
    <el-dialog
      v-model="showEndDialog"
      title="面试已结束"
      width="600px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <div class="end-dialog-content">
        <el-result icon="success">
          <template #title>
            <p>恭喜您完成本次模拟面试！</p>
          </template>
          <template #sub-title>
            <div class="interview-summary">
              <p>面试时长：{{ formatTime(elapsedTime) }}</p>
              <p>回答问题：{{ answeredQuestions }}/{{ totalQuestions }} 个</p>
              <p>AI正在为您生成详细的面试评测报告...</p>
            </div>
          </template>
          <template #extra>
            <div class="end-actions">
              <el-button type="primary" @click="viewReport" :loading="generatingReport">
                {{ generatingReport ? '生成报告中...' : '查看报告' }}
              </el-button>
              <el-button @click="backToSettings">
                重新设置
              </el-button>
              <el-button @click="backToList">
                返回主页
              </el-button>
            </div>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as THREE from 'three'
import {
  VideoPlay, Timer, VideoCamera, QuestionFilled,
  Microphone, Check
} from '@element-plus/icons-vue'

import apiService from '@/api/service.js'

const router = useRouter()

// ================================================================================================
// 🎯 第一部分：基础状态管理
// ================================================================================================

const hasStarted = ref(false)
const isRecording = ref(false)
const isAnswering = ref(false)
const isSpeaking = ref(false)
const isListening = ref(false)
const cameraReady = ref(false)
const showEndDialog = ref(false)
const generatingReport = ref(false)
const isEmergencyExiting = ref(false)

// 面试数据状态
const currentInterviewId = ref(null)
const currentQuestionData = ref(null)
const recordedTranscript = ref('')
const recordedAudioBlob = ref(null)
const answerTime = ref(0)

// 媒体相关状态
const mediaStream = ref(null)
const mediaRecorder = ref(null)

// 定时器管理器
const timeoutManager = {
  timeouts: new Set(),
  intervals: new Set(),

  addTimeout(timeoutId) {
    this.timeouts.add(timeoutId)
    return timeoutId
  },

  addInterval(intervalId) {
    this.intervals.add(intervalId)
    return intervalId
  },

  clearTimeout(timeoutId) {
    if (timeoutId) {
      clearTimeout(timeoutId)
      this.timeouts.delete(timeoutId)
    }
  },

  clearInterval(intervalId) {
    if (intervalId) {
      clearInterval(intervalId)
      this.intervals.delete(intervalId)
    }
  },

  clearAll() {
    this.timeouts.forEach(timeoutId => {
      try {
        clearTimeout(timeoutId)
      } catch (e) {
        console.warn('清除超时失败:', e)
      }
    })
    this.timeouts.clear()

    this.intervals.forEach(intervalId => {
      try {
        clearInterval(intervalId)
      } catch (e) {
        console.warn('清除定时器失败:', e)
      }
    })
    this.intervals.clear()
  }
}

// ================================================================================================
// 🎮 第二部分：面试设置和配置
// ================================================================================================

const settings = ref({
  company: 'tech',
  position: 'frontend',
  round: 'first',
  interviewStyle: 'standard',
  interviewerId: 1,
  duration: 45,
  evaluationFocus: ['technical', 'communication']
})

const interviewerOptions = ref([
  {
    id: 1,
    name: '张技术总监',
    role: '技术总监',
    avatar: '/avatars/tech-director.jpg',
    specialties: ['技术深度', '架构设计', '团队管理'],
    model: '/models/tech-director.glb'
  },
  {
    id: 2,
    name: '李HR经理',
    role: 'HR经理',
    avatar: '/avatars/hr-manager.jpg',
    specialties: ['行为面试', '文化匹配', '综合素质'],
    model: '/models/hr-manager.glb'
  },
  {
    id: 3,
    name: '王产品总监',
    role: '产品总监',
    avatar: '/avatars/product-director.jpg',
    specialties: ['产品思维', '用户体验', '商业逻辑'],
    model: '/models/product-director.glb'
  }
])

const interviewPhases = ref([
  { id: 'intro', title: '开场介绍' },
  { id: 'self', title: '自我介绍' },
  { id: 'technical', title: '技术问答' },
  { id: 'project', title: '项目经历' },
  { id: 'behavioral', title: '行为面试' },
  { id: 'questions', title: '提问环节' }
])

// ================================================================================================
// 📊 第三部分：面试进度和状态
// ================================================================================================

const elapsedTime = ref(0)
const totalTime = computed(() => {
  const duration = settings.value?.duration
  return (duration && typeof duration === 'number') ? duration * 60 : 1800
})

const timeProgress = computed(() => {
  const elapsed = elapsedTime.value || 0
  const total = totalTime.value || 1
  const progress = Math.round((elapsed / total) * 100)
  return Math.max(0, Math.min(100, progress))
})

const currentPhaseIndex = ref(0)
const currentPhase = computed(() => {
  const phases = interviewPhases.value
  const index = currentPhaseIndex.value
  if (phases && Array.isArray(phases) && phases[index]) {
    return phases[index].id || 'intro'
  }
  return 'intro'
})

const currentQuestionIndex = ref(0)
const totalQuestions = ref(8)
const answeredQuestions = ref(0)

const currentQuestion = ref({
  text: '您好，欢迎参加我们的面试。请先做一个简单的自我介绍。',
  context: '请在2-3分钟内完成',
  type: 'self-introduction',
  expectedDuration: 180
})

const currentInterviewer = computed(() => {
  try {
    const options = interviewerOptions.value
    const id = settings.value?.interviewerId

    if (!options || !Array.isArray(options) || options.length === 0) {
      return {
        id: 1,
        name: '默认面试官',
        role: '面试官',
        avatar: '/avatars/default.jpg',
        specialties: ['通用']
      }
    }

    if (id && typeof id === 'number') {
      const found = options.find(i => i && i.id === id)
      if (found) return found
    }

    return options[0] || {
      id: 1,
      name: '默认面试官',
      role: '面试官',
      avatar: '/avatars/default.jpg',
      specialties: ['通用']
    }
  } catch (error) {
    return {
      id: 1,
      name: '默认面试官',
      role: '面试官',
      avatar: '/avatars/default.jpg',
      specialties: ['通用']
    }
  }
})

// ================================================================================================
// 🤖 第四部分：AI实时分析接口区域
// ================================================================================================

const audioLevel = ref(0)
const emotionAnalysis = ref({ type: 'neutral', text: '自然' })
const eyeContactStatus = ref({ type: 'good', text: '良好' })

/**
 * 模拟面试语音转文字处理（严格标准）
 *
 * 🤖 AI接口对接位置 - 高精度语音识别
 * TODO: 队友在这里对接AI API，模拟面试需要更高精度：
 * - 支持专业术语识别
 * - 更严格的语音质量评估
 * - 识别语言表达的专业性
 * - 分析回答的逻辑结构
 */
const transcribeAudioForSimulation = async (audioBlob) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const transcript = await aiService.speechToTextAdvanced({
  //     audioBlob: audioBlob,
  //     language: 'zh-CN',
  //     mode: 'interview_simulation',
  //     analysisLevel: 'professional',
  //     includeQualityMetrics: true
  //   })
  //   return {
  //     text: transcript.text,
  //     quality: transcript.qualityScore,
  //     professionalism: transcript.professionalismScore
  //   }
  // } catch (error) {
  //   console.error('高精度语音转文字失败:', error)
  //   return { text: '', quality: 0, professionalism: 0 }
  // }

  // 当前使用模拟数据（AI对接后可删除）
  return {
    text: '这是模拟面试的语音转文字结果，精度更高。',
    quality: 85,
    professionalism: 78
  }
}

/**
 * 模拟面试压力测试分析
 *
 * 🤖 AI接口对接位置 - 压力环境表现分析
 * TODO: 队友在这里对接AI API，分析压力环境下的表现：
 * - 分析在压力问题下的反应速度
 * - 评估逻辑思维的清晰度
 * - 识别紧张情绪对表现的影响
 * - 提供抗压能力评估
 */
const analyzeStressPerformance = (behaviorData) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const analysis = await aiService.analyzeStressResponse({
  //     audioData: behaviorData.audio,
  //     videoData: behaviorData.video,
  //     responseTime: behaviorData.responseTime,
  //     questionDifficulty: behaviorData.difficulty,
  //     stressLevel: behaviorData.stressLevel
  //   })
  //   return {
  //     stressResistance: analysis.stressResistanceScore,
  //     logicalClarity: analysis.logicalClarityScore,
  //     emotionalControl: analysis.emotionalControlScore
  //   }
  // } catch (error) {
  //   return getDefaultStressAnalysis()
  // }

  // 当前使用模拟数据（AI对接后可删除）
  return {
    stressResistance: Math.random() * 40 + 60,
    logicalClarity: Math.random() * 30 + 70,
    emotionalControl: Math.random() * 35 + 65
  }
}

/**
 * 综合表现评估分析
 *
 * 🤖 AI接口对接位置 - 多维度综合评估
 * TODO: 队友在这里对接AI API，进行综合表现分析：
 * - 技术能力深度评估
 * - 沟通表达专业性分析
 * - 问题解决思路评估
 * - 文化匹配度分析
 * - 领导力潜质评估
 */
const analyzeComprehensivePerformance = async (interviewData) => {
  // 🤖 AI接口调用示例代码位置：
  // try {
  //   const analysis = await aiService.comprehensivePerformanceAnalysis({
  //     interviewType: 'simulation',
  //     company: interviewData.company,
  //     position: interviewData.position,
  //     round: interviewData.round,
  //     answers: interviewData.answers,
  //     behaviorMetrics: interviewData.behaviorMetrics,
  //     evaluationFocus: interviewData.evaluationFocus
  //   })
  //   return {
  //     technicalScore: analysis.technical,
  //     communicationScore: analysis.communication,
  //     problemSolvingScore: analysis.problemSolving,
  //     culturalFitScore: analysis.culturalFit,
  //     leadershipScore: analysis.leadership,
  //     overallRecommendation: analysis.recommendation
  //   }
  // } catch (error) {
  //   return getDefaultComprehensiveAnalysis()
  // }

  // 当前使用模拟数据（AI对接后可删除）
  return {
    technicalScore: Math.random() * 30 + 70,
    communicationScore: Math.random() * 25 + 75,
    problemSolvingScore: Math.random() * 30 + 70,
    culturalFitScore: Math.random() * 20 + 80,
    leadershipScore: Math.random() * 40 + 60,
    overallRecommendation: 'qualified'
  }
}

/**
 * 实时表现监控和分析
 *
 * 🤖 AI接口对接位置 - 模拟面试实时监控
 * TODO: 队友在这里对接AI API，进行更严格的实时监控：
 * - 专业表达用词分析
 * - 回答逻辑结构检测
 * - 自信度实时评估
 * - 面试礼仪监控
 */
const updateLocalAnalysisDisplay = () => {
  if (isEmergencyExiting.value) {
    return
  }

  try {
    if (isAnswering.value) {
      // 🤖 AI接口调用：实时专业表现分析
      const professionalAnalysis = analyzeProfessionalExpression()
      emotionAnalysis.value = Object.assign({}, professionalAnalysis.emotion)

      // 🤖 AI接口调用：实时面试礼仪分析
      const etiquetteAnalysis = analyzeInterviewEtiquette()
      eyeContactStatus.value = Object.assign({}, etiquetteAnalysis.eyeContact)

      audioLevel.value = Math.random() * 80 + 20
    } else {
      audioLevel.value = Math.random() * 20
    }
  } catch (error) {
    if (!isEmergencyExiting.value) {
      emotionAnalysis.value = Object.assign({}, { type: 'neutral', text: '自然' })
      eyeContactStatus.value = Object.assign({}, { type: 'good', text: '良好' })
      audioLevel.value = 0
    }
  }
}

// 辅助AI分析方法
const analyzeProfessionalExpression = () => {
  // TODO: 实现专业表达分析
  const emotions = ['confident', 'professional', 'thoughtful']
  const emotionTexts = { confident: '自信', professional: '专业', thoughtful: '深思' }
  const emotion = emotions[Math.floor(Math.random() * 3)]

  return {
    emotion: { type: emotion, text: emotionTexts[emotion] }
  }
}

const analyzeInterviewEtiquette = () => {
  // TODO: 实现面试礼仪分析
  const etiquetteTypes = ['excellent', 'good', 'needs_improvement']
  const etiquetteTexts = { excellent: '优秀', good: '良好', needs_improvement: '待改善' }
  const type = etiquetteTypes[Math.floor(Math.random() * 3)]

  return {
    eyeContact: { type: type, text: etiquetteTexts[type] }
  }
}

// ================================================================================================
// 🎥 第五部分：媒体设备和3D渲染
// ================================================================================================

const waitingMessage = ref('请认真听题')
const waitingDescription = ref('面试官正在提问，请仔细听完问题后开始回答')
const canStartAnswer = ref(false)

let scene, camera, renderer, avatarMesh
const virtualHumanContainer = ref(null)
const userVideoRef = ref(null)

const answerProgress = computed(() => {
  try {
    const expectedDuration = currentQuestion.value?.expectedDuration || 120
    const currentTime = answerTime.value || 0
    if (expectedDuration <= 0) return 0
    const progress = Math.min(100, (currentTime / expectedDuration) * 100)
    return Math.max(0, Math.round(progress))
  } catch (error) {
    return 0
  }
})

const initVirtualHuman = () => {
  if (!virtualHumanContainer.value) return

  try {
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0e27)

    camera = new THREE.PerspectiveCamera(
      45,
      virtualHumanContainer.value.clientWidth / virtualHumanContainer.value.clientHeight,
      0.1,
      1000
    )
    camera.position.set(0, 0, 5)

    renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(
      virtualHumanContainer.value.clientWidth,
      virtualHumanContainer.value.clientHeight
    )
    virtualHumanContainer.value.appendChild(renderer.domElement)

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5)
    directionalLight.position.set(0, 1, 1)
    scene.add(directionalLight)

    const geometry = new THREE.CylinderGeometry(0.4, 0.5, 1.5, 8)
    const material = new THREE.MeshPhongMaterial({
      color: 0x4a90e2,
      transparent: true,
      opacity: 0.8
    })
    avatarMesh = new THREE.Mesh(geometry, material)
    scene.add(avatarMesh)

    animate()

  } catch (error) {
    createSimplePlaceholder()
  }
}

const createSimplePlaceholder = () => {
  try {
    if (!virtualHumanContainer.value) return

    virtualHumanContainer.value.innerHTML = `
      <div style="
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        font-size: 48px;
      ">
        <div style="text-align: center;">
          <div style="font-size: 64px; margin-bottom: 10px;">👨‍💼</div>
          <div style="font-size: 16px;">${currentInterviewer.value.name}</div>
        </div>
      </div>
    `
  } catch (error) {
    console.error('创建占位符失败:', error)
  }
}

const animate = () => {
  requestAnimationFrame(animate)

  if (avatarMesh) {
    avatarMesh.rotation.y += 0.005
    if (isSpeaking.value) {
      avatarMesh.scale.y = 1 + Math.sin(Date.now() * 0.005) * 0.05
    }
  }

  renderer?.render(scene, camera)
}

const setupCamera = async () => {
  try {
    if (!mediaStream.value) {
      mediaStream.value = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      })
    }

    if (userVideoRef.value && mediaStream.value) {
      userVideoRef.value.srcObject = mediaStream.value
    }

    cameraReady.value = true
    startAudioMonitoring()
    ElMessage.success('设备设置完成')

  } catch (error) {
    ElMessage.error('无法访问摄像头或麦克风，请检查权限设置')
    cameraReady.value = false
    mediaStream.value = null
  }
}

// ================================================================================================
// 🎤 第六部分：录音和回答控制
// ================================================================================================

const initMediaRecorder = async () => {
  try {
    if (!mediaStream.value) {
      mediaStream.value = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false
      })
    }

    if (!mediaStream.value || typeof mediaStream.value.getAudioTracks !== 'function') {
      throw new Error('无效的媒体流')
    }

    mediaRecorder.value = new MediaRecorder(mediaStream.value, {
      mimeType: 'audio/webm;codecs=opus'
    })

    let audioChunks = []

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      recordedAudioBlob.value = audioBlob
      audioChunks = []

      // 🤖 AI接口调用：模拟面试高精度语音转文字
      const transcriptionResult = await transcribeAudioForSimulation(audioBlob)
      recordedTranscript.value = transcriptionResult.text
    }

    return true

  } catch (error) {
    ElMessage.error('无法访问麦克风，请检查权限设置')
    mediaRecorder.value = null
    return false
  }
}

const startRecording = async () => {
  try {
    if (!mediaRecorder.value) {
      const success = await initMediaRecorder()
      if (!success) return false
    }

    recordedAudioBlob.value = null
    recordedTranscript.value = ''

    if (mediaRecorder.value.state === 'inactive') {
      mediaRecorder.value.start(1000)
      isRecording.value = true
      return true
    }

  } catch (error) {
    ElMessage.error('开始录音失败：' + error.message)
    return false
  }
}

const stopRecording = async () => {
  try {
    if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
      mediaRecorder.value.stop()
    }

    isRecording.value = false

    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(recordedAudioBlob.value)
      }, 500)
    })

  } catch (error) {
    ElMessage.error('停止录音失败：' + error.message)
    return null
  }
}

// ================================================================================================
// 📋 第七部分：面试流程控制
// ================================================================================================

const startSimulation = async () => {
  try {
    const hasResume = localStorage.getItem('userResume')
    if (!hasResume) {
      const confirm = await ElMessageBox.confirm(
        '检测到您还未上传简历，建议先上传简历以获得个性化的面试题目。是否继续？',
        '提示',
        {
          confirmButtonText: '继续模拟',
          cancelButtonText: '去上传简历',
          type: 'warning'
        }
      ).catch(() => false)

      if (!confirm) {
        router.push('/dashboard/resume-manage')
        return
      }
    }

    const response = await apiService.interview.startSimulation({
      company: settings.value.company,
      position: settings.value.position,
      round: settings.value.round,
      interviewStyle: settings.value.interviewStyle,
      interviewerId: settings.value.interviewerId,
      duration: settings.value.duration,
      evaluationFocus: settings.value.evaluationFocus
    })

    currentInterviewId.value = response.data.interview_id
    currentQuestionData.value = response.data.first_question
    totalQuestions.value = response.data.total_questions

    if (currentQuestionData.value) {
      currentQuestion.value = {
        text: currentQuestionData.value.text,
        type: currentQuestionData.value.type,
        difficulty: currentQuestionData.value.difficulty,
        context: `请在${Math.floor(currentQuestionData.value.time_limit / 60)}分钟内完成`,
        expectedDuration: currentQuestionData.value.time_limit
      }
    }

    hasStarted.value = true

    nextTick(() => {
      initVirtualHuman()
      setupCamera()
    })

    startTimer()

    setTimeout(() => {
      startInterviewFlow()
    }, 2000)

    ElMessage.success('模拟面试开始！')

  } catch (error) {
    ElMessage.error('开始模拟面试失败：' + (error.response?.data?.detail || error.message))
  }
}

const startInterviewFlow = async () => {
  try {
    if (isEmergencyExiting.value) {
      return
    }

    await apiService.interview.updateInterviewerStatus(currentInterviewId.value, {
      isSpeaking: true,
      isListening: false,
      currentPhase: 'intro'
    })

    isSpeaking.value = true
    waitingMessage.value = '面试官正在介绍'
    waitingDescription.value = `欢迎参加${getCompanyName(settings.value.company)}的面试`

    const speakingTimeoutId = setTimeout(async () => {
      try {
        if (isEmergencyExiting.value) {
          return
        }

        if (!currentInterviewId.value) {
          return
        }

        if (!currentQuestion.value) {
          return
        }

        await apiService.interview.updateInterviewerStatus(currentInterviewId.value, {
          isSpeaking: false,
          isListening: true,
          currentPhase: 'self'
        })

        if (!isEmergencyExiting.value) {
          isSpeaking.value = false
          isListening.value = true
          waitingMessage.value = '请开始回答'

          const context = currentQuestion.value?.context || '请开始您的回答'
          waitingDescription.value = context
          canStartAnswer.value = true
        }

        timeoutManager.clearTimeout(speakingTimeoutId)

      } catch (error) {
        timeoutManager.clearTimeout(speakingTimeoutId)
      }
    }, 5000)

    timeoutManager.addTimeout(speakingTimeoutId)

  } catch (error) {
    console.error('启动面试流程失败:', error)
  }
}

const startAnswer = async () => {
  try {
    await apiService.interview.startAnswerSimulation(
      currentInterviewId.value,
      currentQuestionData.value.id
    )

    isAnswering.value = true
    answerTime.value = 0
    canStartAnswer.value = false

    let answerTimer = setInterval(() => {
      answerTime.value++
    }, 1000)

    timeoutManager.addInterval(answerTimer)
    startRealtimeAnalysis()

    ElMessage.success('开始回答，请自然表达')

  } catch (error) {
    ElMessage.error('开始回答失败：' + (error.response?.data?.detail || error.message))
  }
}

const finishAnswer = async () => {
  try {
    const response = await apiService.interview.finishAnswerSimulation(
      currentInterviewId.value,
      currentQuestionData.value.id,
      {
        answerText: recordedTranscript.value || '',
        audioPath: recordedAudioBlob.value ? 'temp_audio_path' : null,
        videoPath: null,
        timeSpent: answerTime.value
      }
    )

    isAnswering.value = false
    answeredQuestions.value++

    stopRealtimeAnalysis()

    ElMessage.success(`回答已提交，评分：${response.data.score}`)

    if (response.data.next_question) {
      currentQuestionData.value = response.data.next_question
      currentQuestionIndex.value++

      currentQuestion.value = {
        text: response.data.next_question.text,
        type: response.data.next_question.type,
        difficulty: response.data.next_question.difficulty,
        context: `请在${Math.floor(response.data.next_question.time_limit / 60)}分钟内完成`,
        expectedDuration: response.data.next_question.time_limit
      }

      setTimeout(() => {
        nextQuestion()
      }, 2000)
    } else {
      setTimeout(() => {
        endInterview()
      }, 3000)
    }

  } catch (error) {
    ElMessage.error('完成回答失败：' + (error.response?.data?.detail || error.message))
  }
}

const nextQuestion = async () => {
  try {
    if (isEmergencyExiting.value) {
      return
    }

    const phaseIndex = currentQuestionIndex.value
    let currentPhase = 'general'

    if (phaseIndex <= 1) currentPhase = 'self'
    else if (phaseIndex <= 3) currentPhase = 'technical'
    else if (phaseIndex <= 5) currentPhase = 'project'
    else if (phaseIndex <= 6) currentPhase = 'behavioral'
    else currentPhase = 'questions'

    await apiService.interview.updateInterviewPhase(currentInterviewId.value, {
      currentPhase: currentPhase,
      phaseIndex: phaseIndex
    })

    currentPhaseIndex.value = phaseIndex

    await apiService.interview.updateInterviewerStatus(currentInterviewId.value, {
      isSpeaking: true,
      isListening: false,
      currentPhase: currentPhase
    })

    isSpeaking.value = true
    waitingMessage.value = '面试官正在提问'
    waitingDescription.value = '请认真听题，准备回答'
    canStartAnswer.value = false

    const questionTimeoutId = setTimeout(async () => {
      try {
        if (isEmergencyExiting.value) {
          return
        }

        if (!currentInterviewId.value) {
          return
        }

        await apiService.interview.updateInterviewerStatus(currentInterviewId.value, {
          isSpeaking: false,
          isListening: true,
          currentPhase: currentPhase
        })

        if (!isEmergencyExiting.value) {
          isSpeaking.value = false
          isListening.value = true
          waitingMessage.value = '请开始回答'

          const context = currentQuestion.value?.context || '请开始您的回答'
          waitingDescription.value = context
          canStartAnswer.value = true
        }

        timeoutManager.clearTimeout(questionTimeoutId)

      } catch (error) {
        timeoutManager.clearTimeout(questionTimeoutId)
      }
    }, 3000)

    timeoutManager.addTimeout(questionTimeoutId)

  } catch (error) {
    console.error('切换下一题失败:', error)
  }
}

// ================================================================================================
// 🤖 第八部分：实时分析处理接口区域
// ================================================================================================

/**
 * 开始模拟面试实时分析
 *
 * 🤖 AI接口对接位置 - 模拟面试实时监控
 * TODO: 队友在这里对接AI API，进行更严格的实时分析：
 * - 专业表现实时监控
 * - 压力测试反应分析
 * - 面试礼仪实时评估
 * - 综合表现动态跟踪
 */
const startRealtimeAnalysis = () => {
  const analysisId = setInterval(async () => {
    if (isEmergencyExiting.value) {
      timeoutManager.clearInterval(analysisId)
      return
    }

    if (isAnswering.value && currentInterviewId.value) {
      try {
        // 🤖 AI接口调用：模拟面试实时分析
        const realtimeData = {
          audioLevel: Math.random() * 100,
          emotionType: ['confident', 'professional', 'thoughtful'][Math.floor(Math.random() * 3)],
          eyeContactScore: Math.random() * 100,
          speechSpeed: Math.random() * 200 + 100,
          professionalismScore: Math.random() * 40 + 60,
          stressLevel: settings.value.interviewStyle === 'stress' ? Math.random() * 30 + 70 : Math.random() * 20 + 40,
          timestamp: new Date().toISOString()
        }

        await apiService.interview.submitSimulationAnalysis(currentInterviewId.value, realtimeData)

        if (!isEmergencyExiting.value) {
          updateLocalAnalysisDisplay()
        }

      } catch (error) {
        console.error('提交实时分析数据失败:', error)
      }
    }
  }, 2000)

  timeoutManager.addInterval(analysisId)
}

const stopRealtimeAnalysis = () => {
  if (!isEmergencyExiting.value) {
    try {
      emotionAnalysis.value = Object.assign({}, { type: 'neutral', text: '自然' })
      eyeContactStatus.value = Object.assign({}, { type: 'good', text: '良好' })
      audioLevel.value = 0
    } catch (error) {
      console.error('重置分析状态失败:', error)
    }
  }
}

const startAudioMonitoring = () => {
  const audioMonitorInterval = setInterval(() => {
    if (isAnswering.value) {
      audioLevel.value = Math.random() * 100
    } else {
      audioLevel.value = Math.random() * 20
    }

    if (!isRecording.value && !isAnswering.value) {
      clearInterval(audioMonitorInterval)
    }
  }, 100)
}

// ================================================================================================
// 🚨 第九部分：紧急退出和资源管理
// ================================================================================================

const emergencyExit = async () => {
  if (isEmergencyExiting.value) {
    return
  }

  isEmergencyExiting.value = true

  try {
    timeoutManager.clearAll()

    await nextTick()

    try {
      if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
        mediaRecorder.value.stop()
      }
      mediaRecorder.value = null

      if (mediaStream.value && typeof mediaStream.value.getTracks === 'function') {
        mediaStream.value.getTracks().forEach(track => {
          try { track.stop() } catch (e) { /* 忽略 */ }
        })
      }
      mediaStream.value = null
    } catch (mediaError) {
      console.warn('停止媒体设备失败:', mediaError)
    }

    await nextTick()

    try {
      emotionAnalysis.value = Object.assign({}, { type: 'neutral', text: '自然' })
      eyeContactStatus.value = Object.assign({}, { type: 'good', text: '良好' })
    } catch (objError) {
      emotionAnalysis.value = { type: 'neutral', text: '自然' }
      eyeContactStatus.value = { type: 'good', text: '良好' }
    }

    await nextTick()

    isRecording.value = false
    isAnswering.value = false
    isSpeaking.value = false
    isListening.value = false
    cameraReady.value = false

    audioLevel.value = 0
    answerTime.value = 0
    elapsedTime.value = 0

    currentInterviewId.value = null
    currentQuestionData.value = null
    recordedAudioBlob.value = null
    recordedTranscript.value = ''

    const confirmed = await ElMessageBox.confirm(
      '确定要紧急退出面试吗？这将结束当前面试并生成部分报告。',
      '紧急退出',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '继续面试',
        type: 'warning'
      }
    ).catch(() => false)

    if (!confirmed) {
      isEmergencyExiting.value = false
      return
    }

    try {
      if (currentInterviewId.value) {
        await apiService.interview.completeSimulation(currentInterviewId.value, {
          completionType: 'emergency',
          emergencyReason: '用户主动退出'
        })
      }
    } catch (apiError) {
      console.warn('API调用失败:', apiError)
    }

    const endTimeoutId = setTimeout(() => {
      if (isEmergencyExiting.value) {
        showEndDialog.value = true
        generatingReport.value = false
      }
      timeoutManager.clearTimeout(endTimeoutId)
    }, 300)

    timeoutManager.addTimeout(endTimeoutId)

  } catch (error) {
    timeoutManager.clearAll()
    isEmergencyExiting.value = false

    ElMessage.error('退出过程出现问题，正在返回主页')

    const emergencyTimeoutId = setTimeout(() => {
      router.push('/dashboard')
      timeoutManager.clearTimeout(emergencyTimeoutId)
    }, 1000)

    timeoutManager.addTimeout(emergencyTimeoutId)
  }
}

const startTimer = () => {
  const timerId = setInterval(() => {
    if (isEmergencyExiting.value) {
      timeoutManager.clearInterval(timerId)
      return
    }

    elapsedTime.value++

    if (elapsedTime.value >= totalTime.value) {
      timeoutManager.clearInterval(timerId)
      endInterview()
    }
  }, 1000)

  timeoutManager.addInterval(timerId)
}

const endInterview = async (isEmergency = false) => {
  try {
    cleanupResources()

    if (!isEmergency && currentInterviewId.value) {
      try {
        await apiService.interview.completeSimulation(currentInterviewId.value, {
          completionType: 'normal'
        })
        ElMessage.success('模拟面试已完成')
      } catch (error) {
        ElMessage.warning('面试数据保存可能失败，但本地已清理')
      }
    } else if (isEmergency) {
      ElMessage.warning('面试已中断')
    }

    nextTick(() => {
      showEndDialog.value = true

      generatingReport.value = true
      setTimeout(() => {
        generatingReport.value = false
      }, 3000)
    })

  } catch (error) {
    ElMessage.error('结束面试失败：' + (error.message || '未知错误'))

    nextTick(() => {
      showEndDialog.value = true
    })
  }
}

const cleanupResources = () => {
  try {
    if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
      try {
        mediaRecorder.value.stop()
      } catch (error) {
        console.warn('停止录音器失败:', error)
      }
    }
    mediaRecorder.value = null

    if (mediaStream.value && typeof mediaStream.value.getTracks === 'function') {
      try {
        mediaStream.value.getTracks().forEach(track => {
          try {
            track.stop()
          } catch (error) {
            console.warn('停止媒体轨道失败:', error)
          }
        })
      } catch (error) {
        console.warn('清理媒体流失败:', error)
      }
    }
    mediaStream.value = null

  } catch (error) {
    console.error('清理媒体资源失败:', error)
  }

  try {
    if (renderer) {
      renderer.dispose()
      renderer = null
    }
    if (scene) {
      scene = null
    }
    if (camera) {
      camera = null
    }
    if (avatarMesh) {
      avatarMesh = null
    }

  } catch (error) {
    console.error('清理3D资源失败:', error)
  }

  try {
    isRecording.value = false
    isAnswering.value = false
    isSpeaking.value = false
    isListening.value = false
    cameraReady.value = false

    currentInterviewId.value = null
    currentQuestionData.value = null
    recordedAudioBlob.value = null
    recordedTranscript.value = ''
    answerTime.value = 0
    audioLevel.value = 0

    emotionAnalysis.value = { type: 'neutral', text: '自然' }
    eyeContactStatus.value = { type: 'good', text: '良好' }

  } catch (error) {
    console.error('重置状态失败:', error)
  }
}

// ================================================================================================
// 📊 第十部分：结果处理和导航
// ================================================================================================

const viewReport = () => {
  router.push('/dashboard/interview-performance')
}

const backToSettings = () => {
  hasStarted.value = false
  showEndDialog.value = false
  elapsedTime.value = 0
  currentQuestionIndex.value = 0
  currentPhaseIndex.value = 0
  answeredQuestions.value = 0
}

const backToList = () => {
  router.push('/dashboard')
}

// ================================================================================================
// 💫 第十一部分：计算属性和辅助函数
// ================================================================================================

const canStart = computed(() => {
  try {
    const settingsValue = settings.value
    if (!settingsValue) return false

    return !!(
      settingsValue.company &&
      settingsValue.position &&
      settingsValue.interviewerId &&
      Array.isArray(settingsValue.evaluationFocus) &&
      settingsValue.evaluationFocus.length > 0
    )
  } catch (error) {
    return false
  }
})

const getCompanyName = (type) => {
  const names = {
    tech: '科技有限公司',
    foreign: '外资企业',
    state: '国有企业',
    startup: '创业公司'
  }
  return names[type] || '公司'
}

const getRoundName = (round) => {
  const names = {
    first: '初试',
    second: '复试',
    final: '终面'
  }
  return names[round] || '面试'
}

const getPhaseType = (phase) => {
  const types = {
    intro: 'info',
    self: 'primary',
    technical: 'warning',
    project: 'success',
    behavioral: 'danger',
    questions: 'info'
  }
  return types[phase] || 'info'
}

const getPhaseTitle = (phase) => {
  const titles = {
    intro: '开场阶段',
    self: '自我介绍',
    technical: '技术问答',
    project: '项目经历',
    behavioral: '行为面试',
    questions: '提问环节'
  }
  return titles[phase] || '面试中'
}

const getTimeColor = (percentage) => {
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#409eff'
}

const getAnswerProgressColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#409eff'
  return '#e6a23c'
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// ================================================================================================
// 🔄 第十二部分：生命周期管理
// ================================================================================================

onUnmounted(() => {
  isEmergencyExiting.value = true

  timeoutManager.clearAll()

  try {
    if (mediaRecorder.value) {
      if (mediaRecorder.value.state === 'recording') {
        mediaRecorder.value.stop()
      }
      mediaRecorder.value = null
    }

    if (mediaStream.value && typeof mediaStream.value.getTracks === 'function') {
      mediaStream.value.getTracks().forEach(track => {
        try { track.stop() } catch (e) { /* 忽略 */ }
      })
      mediaStream.value = null
    }
  } catch (error) {
    console.error('清理媒体资源失败:', error)
  }

  try {
    emotionAnalysis.value = { type: 'neutral', text: '自然' }
    eyeContactStatus.value = { type: 'good', text: '良好' }
  } catch (error) {
    console.error('最终状态重置失败:', error)
  }
})

</script>

<style scoped>
.interview-simulation-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

/* 开始页面样式 */
.start-section {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
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

.interviewer-config {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.interviewer-option {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.interviewer-option:hover {
  background: rgba(255, 255, 255, 0.08);
}

.interviewer-option.selected {
  border-color: var(--primary-color);
  background: rgba(64, 158, 255, 0.1);
}

.interviewer-details h5 {
  color: var(--text-primary);
  margin: 0 0 5px 0;
}

.interviewer-details p {
  color: var(--text-secondary);
  margin: 0 0 10px 0;
  font-size: 13px;
}

.interviewer-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.simulation-warning {
  margin: 25px 0;
}

.simulation-warning ul {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
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

/* 面试主界面 */
.interview-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
}

.interview-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.company-info,
.round-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
}

.time-text {
  font-family: monospace;
  font-size: 1.1rem;
  font-weight: bold;
}

/* 面试区域 */
.interview-area {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 面试官区域 */
.interviewer-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.virtual-interviewer {
  flex: 1;
  position: relative;
  min-height: 300px;
}

.virtual-human-canvas {
  width: 100%;
  height: calc(100% - 60px);
}

.interviewer-info-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.interviewer-status {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #666;
  transition: all 0.3s ease;
}

.status-indicator.speaking {
  background: #67c23a;
  animation: pulse 1s ease-in-out infinite;
}

.status-indicator.listening {
  background: #409eff;
}

.question-display {
  padding: 20px;
  min-height: 120px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  color: var(--text-secondary);
  font-size: 14px;
}

.question-text {
  font-size: 1.1rem;
  color: var(--text-primary);
  line-height: 1.6;
  margin-bottom: 10px;
}

.question-context {
  margin-top: 10px;
}

/* 候选人区域 */
.candidate-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-video-container {
  flex: 1;
  position: relative;
  min-height: 250px;
}

.user-video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.video-setup {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.video-setup p {
  margin: 15px 0;
}

.recording-indicator {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(245, 108, 108, 0.9);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
}

.rec-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}

.answer-control {
  padding: 20px;
  text-align: center;
}

.waiting-state h4 {
  color: var(--text-primary);
  margin-bottom: 10px;
}

.waiting-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.answering-state {
  display: flex;
  align-items: center;
  gap: 30px;
}

.answer-timer {
  flex-shrink: 0;
}

.timer-text {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.answer-controls {
  flex: 1;
}

.answer-hint {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 13px;
}

.realtime-feedback {
  padding: 15px;
}

.realtime-feedback h4 {
  color: var(--text-primary);
  margin-bottom: 15px;
  font-size: 1rem;
}

.feedback-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feedback-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.feedback-item .label {
  width: 70px;
  color: var(--text-secondary);
}

.status-text {
  font-weight: 600;
}

.status-text.confident,
.status-text.professional,
.status-text.excellent,
.status-text.good {
  color: #67c23a;
}

.status-text.thoughtful,
.status-text.neutral,
.status-text.average {
  color: #409eff;
}

.status-text.nervous,
.status-text.needs_improvement,
.status-text.poor {
  color: #f56c6c;
}

/* 进度追踪 */
.progress-tracker {
  padding: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.progress-step.active {
  opacity: 1;
  color: var(--primary-color);
}

.progress-step.completed {
  opacity: 1;
  color: var(--success-color);
}

.step-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.progress-step.active .step-circle {
  background: var(--primary-color);
  color: white;
}

.progress-step.completed .step-circle {
  background: var(--success-color);
  color: white;
}

.step-label {
  font-size: 12px;
  text-align: center;
}

/* 结束对话框 */
.end-dialog-content {
  text-align: center;
}

.interview-summary {
  margin: 20px 0;
}

.interview-summary p {
  margin: 8px 0;
  color: var(--text-secondary);
}

.end-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .interview-area {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .answering-state {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .status-bar {
    flex-wrap: wrap;
    gap: 15px;
  }

  .time-display {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .progress-steps {
    flex-wrap: wrap;
    gap: 20px;
  }

  .interviewer-config {
    grid-template-columns: 1fr;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
}
</style>
