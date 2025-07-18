/**
 * API服务层 - 统一管理所有API请求
 * 使用RESTful风格，方便后续与后端对接
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router' // 引入 router

// API基础配置, 从环境变量获取，方便部署
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 统一添加认证token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  // 对2xx范围内的状态码触发该函数
  (response) => {
    // 后端返回的数据结构如果是 { code, data, message }，可以这样处理
    // 直接返回 data，简化后续操作
    return response.data
  },
  // 超出2xx范围的状态码触发该函数
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token过期或无效
          ElMessage.error('登录已过期，请重新登录')
          localStorage.clear() // 清除所有本地存储
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
        default:
          // 从后端返回的错误信息中取 detail
          ElMessage.error(error.response.data.detail || '请求失败')
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      ElMessage.error('网络连接失败，请检查您的网络')
    } else {
      // 发送请求时出了点问题
      ElMessage.error('请求发送失败')
    }
    return Promise.reject(error)
  },
)

/**
 * API服务类 - 封装所有API请求
 * 注意：这里我们定义了真实的API调用，你需要确保后端有对应的接口。
 */
class ApiService {
  auth = {
    /**
     * 用户登录
     * @param {Object} credentials - {username, password}
     */
    login: (credentials) => apiClient.post('/auth/login', credentials),

    /**
     * 用户注册
     * @param {Object} userData - {username, password, email}
     */
    register: (userData) => apiClient.post('/auth/register', userData),
  }

  user = {
    /**
     * 获取当前登录用户的资料
     * GET /users/me
     */
    getProfile: () => apiClient.get('/users/me'),

    /**
     * 更新当前登录用户的资料
     * PUT /users/me
     * @param {Object} profileData - 用户资料
     */
    updateProfile: (profileData) => apiClient.put('/users/me', profileData),
  }

  /**
   * 简历相关API
   */
  resume = {
    /**
     * 获取简历列表
     * GET /resumes
     * @returns {Promise} - 简历列表
     */
    getList: () => {
      // TODO: 后端实现后启用
      // return apiClient.get('/resumes')

      // 返回模拟数据
      return Promise.resolve([
        {
          id: 1,
          name: '张三_前端开发_简历.pdf',
          size: 262144,
          uploadTime: '2024-01-15',
          isActive: true,
          parsed: {
            name: '张三',
            position: '前端开发工程师',
            skills: ['Vue.js', 'React', 'Node.js'],
          },
        },
      ])
    },

    /**
     * 上传简历
     * POST /resumes
     * @param {FormData} formData - 包含简历文件
     * @returns {Promise}
     */
    upload: (formData) => {
      return apiClient.post('/resumes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    },

    /**
     * 删除简历
     * DELETE /resumes/{id}
     * @param {Number} id - 简历ID
     * @returns {Promise}
     */
    delete: (id) => {
      return apiClient.delete(`/resumes/${id}`)
    },

    /**
     * 设置默认简历
     * PUT /resumes/{id}/activate
     * @param {Number} id - 简历ID
     * @returns {Promise}
     */
    setActive: (id) => {
      return apiClient.put(`/resumes/${id}/activate`)
    },
  }

  /**
   * 面试练习相关API - 完整版本
   */
  interview = {
    /**
     * 开始面试练习
     * POST /interviews/start
     */
    start: (config) => {
      return apiClient.post('/interviews/start', {
        type: 'practice',  // 练习模式
        position: config.position,
        difficulty: config.difficulty,
        interview_style: config.interviewStyle,
        interviewer_id: config.avatarId,
        duration: config.duration,
        question_types: config.questionTypes,
        special_settings: config.specialSettings
      })
    },

    /**
     * 提交答案
     * POST /interviews/questions/{questionId}/answer
     */
    submitAnswer: (questionId, answerData) => {
      return apiClient.post(`/interviews/questions/${questionId}/answer`, {
        answer_text: answerData.answerText,
        audio_file_path: answerData.audioPath,
        video_file_path: answerData.videoPath,
        time_spent: answerData.timeSpent,
        used_hint: answerData.usedHint
      })
    },

    /**
     * 获取下一题
     * GET /interviews/questions/{questionId}/next
     */
    getNextQuestion: (questionId) => {
      return apiClient.get(`/interviews/questions/${questionId}/next`)
    },

    /**
     * 暂停面试
     * POST /interviews/{interviewId}/pause
     */
    pauseInterview: (interviewId) => {
      return apiClient.post(`/interviews/${interviewId}/pause`)
    },

    /**
     * 继续面试
     * POST /interviews/{interviewId}/resume
     */
    resumeInterview: (interviewId) => {
      return apiClient.post(`/interviews/${interviewId}/resume`)
    },

    /**
     * 跳过问题
     * POST /interviews/{interviewId}/skip-question?question_id={questionId}
     */
    skipQuestion: (interviewId, questionId) => {
      return apiClient.post(`/interviews/${interviewId}/skip-question?question_id=${questionId}`)
    },

    /**
     * 获取题目提示
     * GET /interviews/questions/{questionId}/hint
     */
    getQuestionHint: (questionId) => {
      return apiClient.get(`/interviews/questions/${questionId}/hint`)
    },

    /**
     * 标记使用提示
     * POST /interviews/questions/{questionId}/use-hint
     */
    markHintUsed: (questionId) => {
      return apiClient.post(`/interviews/questions/${questionId}/use-hint`)
    },

    /**
     * 获取面试状态
     * GET /interviews/{interviewId}/status
     */
    getInterviewStatus: (interviewId) => {
      return apiClient.get(`/interviews/${interviewId}/status`)
    },

    /**
     * 上传音频文件
     * POST /interviews/{interviewId}/upload-audio
     */
    uploadAudio: (interviewId, questionId, audioFile) => {
      const formData = new FormData()
      formData.append('audio_file', audioFile)

      return apiClient.post(
        `/interviews/${interviewId}/upload-audio?question_id=${questionId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      )
    },

    /**
     * 上传视频文件
     * POST /interviews/{interviewId}/upload-video
     */
    uploadVideo: (interviewId, questionId, videoFile) => {
      const formData = new FormData()
      formData.append('video_file', videoFile)

      return apiClient.post(
        `/interviews/${interviewId}/upload-video?question_id=${questionId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      )
    },

    /**
     * 提交实时分析数据
     * POST /interviews/{interviewId}/realtime-analysis
     */
    submitRealtimeData: (interviewId, analysisData) => {
      return apiClient.post(`/interviews/${interviewId}/realtime-analysis`, analysisData)
    },

    /**
     * 获取实时状态
     * GET /interviews/{interviewId}/realtime-status
     */
    getRealtimeStatus: (interviewId) => {
      return apiClient.get(`/interviews/${interviewId}/realtime-status`)
    },

    /**
     * 完成面试
     * POST /interviews/{interviewId}/complete
     */
    completeInterview: (interviewId, completionType = 'normal') => {
        console.log('📡 API调用: completeInterview')
        console.log('面试ID:', interviewId, '类型:', typeof interviewId)
        console.log('完成类型:', completionType)

        // 🔥 确保参数类型正确
        const requestData = {
          interview_id: parseInt(interviewId), // 确保是数字
          completion_type: completionType || 'normal'
        }

        console.log('请求数据:', requestData)

        return apiClient.post(`/interviews/${interviewId}/complete`, requestData)
      },

    endInterview: (interviewId) => {
        console.log('📡 API调用: endInterview (兼容性接口)')
        console.log('面试ID:', interviewId)

        return apiClient.post(`/interviews/${interviewId}/end`)
      },

    /**
     * 紧急退出
     * POST /interviews/{interviewId}/emergency-exit
     */
    emergencyExit: (interviewId, reason = null) => {
      return apiClient.post(
        `/interviews/${interviewId}/emergency-exit?exit_reason=${encodeURIComponent(reason || '')}`
      )
    },

    /**
     * 获取虚拟面试官列表
     * GET /interviews/interviewers
     */
    getInterviewers: () => {
      return apiClient.get('/interviews/interviewers')
    },


    // 兼容现有代码的旧接口
    end: (interviewId) => {
      return apiClient.post(`/interviews/${interviewId}/end`)
    },
    /**
   * 开始模拟面试（新增）
   * POST /interviews/start-simulation
   */
  startSimulation: (config) => {
    return apiClient.post('/interviews/start-simulation', {
      type: 'simulation',
      company: config.company,
      position: config.position,
      round: config.round,
      interview_style: config.interviewStyle,
      interviewer_id: config.interviewerId,
      duration: config.duration,
      evaluation_focus: config.evaluationFocus
    })
  },


  /**
   * 更新面试官状态（新增）
   * POST /interviews/{interviewId}/interviewer-status
   */
  updateInterviewerStatus: (interviewId, statusData) => {
    return apiClient.post(`/interviews/${interviewId}/interviewer-status`, {
      is_speaking: statusData.isSpeaking,
      is_listening: statusData.isListening,
      current_phase: statusData.currentPhase
    })
  },

  /**
   * 获取面试阶段信息（已存在，确保正常工作）
   * GET /interviews/{interviewId}/phases
   */
  getInterviewPhases: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/phases`)
  },

  /**
   * 更新面试阶段（新增）
   * POST /interviews/{interviewId}/update-phase
   */
  updateInterviewPhase: (interviewId, phaseData) => {
    return apiClient.post(`/interviews/${interviewId}/update-phase`, {
      current_phase: phaseData.currentPhase,
      phase_index: phaseData.phaseIndex
    })
  },

  /**
   * 完成模拟面试（新增）
   * POST /interviews/{interviewId}/complete-simulation
   */
  completeSimulation: (interviewId, completionData) => {
    return apiClient.post(`/interviews/${interviewId}/complete-simulation`, {
      completion_type: completionData.completionType || 'normal',
      emergency_reason: completionData.emergencyReason
    })
  },

  /**
   * 获取面试官配置（增强版）
   * GET /interviews/interviewers/{interviewerId}/config
   */
  getInterviewerConfig: (interviewerId) => {
    return apiClient.get(`/interviews/interviewers/${interviewerId}/config`)
  },

  /**
   * 开始回答（模拟面试专用）
   * POST /interviews/{interviewId}/start-answer
   */
  startAnswerSimulation: (interviewId, questionId) => {
    return apiClient.post(`/interviews/${interviewId}/start-answer`, {
      question_id: questionId,
      started_at: new Date().toISOString()
    })
  },

  /**
   * 完成回答（模拟面试专用）
   * POST /interviews/{interviewId}/finish-answer
   */
  finishAnswerSimulation: (interviewId, questionId, answerData) => {
    return apiClient.post(`/interviews/${interviewId}/finish-answer`, {
      question_id: questionId,
      answer_text: answerData.answerText,
      audio_file_path: answerData.audioPath,
      video_file_path: answerData.videoPath,
      time_spent: answerData.timeSpent,
      completed_at: new Date().toISOString()
    })
  },

  /**
   * 获取实时面试状态（模拟面试专用）
   * GET /interviews/{interviewId}/simulation-status
   */
  getSimulationStatus: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/simulation-status`)
  },

  /**
   * 提交实时分析数据（模拟面试专用）
   * POST /interviews/{interviewId}/simulation-analysis
   */
  submitSimulationAnalysis: (interviewId, analysisData) => {
    return apiClient.post(`/interviews/${interviewId}/simulation-analysis`, {
      audio_level: analysisData.audioLevel,
      emotion_type: analysisData.emotionType,
      eye_contact_score: analysisData.eyeContactScore,
      speech_speed: analysisData.speechSpeed,
      timestamp: new Date().toISOString()
    })
  },

 /**
   * 获取面试表现分析
   * GET /interviews/performance
   */
  getPerformance: () => {
    return apiClient.get('/interviews/performance')
  },

  /**
   * 获取趋势数据
   * GET /interviews/trend
   */
  getTrend: (params) => {
    return apiClient.get('/interviews/trend', { params })
  },

  /**
   * 获取面试历史记录
   * GET /interviews/history
   */
  getHistory: (params) => {
    return apiClient.get('/interviews/history', { params })
  },

  /**
   * 获取个性化建议
   * GET /interviews/personal-advice
   */
  getPersonalAdvice: () => {
    return apiClient.get('/interviews/personal-advice')
  },

  /**
   * 获取面试详细分析
   * GET /interviews/{interviewId}/detailed-analysis
   */
  getDetailedAnalysis: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/detailed-analysis`)
  },

  /**
   * 获取问答记录
   * GET /interviews/{interviewId}/qa-records
   */
  getQARecords: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/qa-records`)
  },

  /**
   * 获取回放信息
   * GET /interviews/{interviewId}/replay-info
   */
  getReplayInfo: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/replay-info`)
  },

  /**
   * 创建针对性练习计划
   * POST /interviews/targeted-practice
   */
  createTargetedPractice: (practiceRequest) => {
    return apiClient.post('/interviews/targeted-practice', practiceRequest)
  },

  /**
   * 获取能力洞察
   * GET /interviews/ability-insights
   */
  getAbilityInsights: () => {
    return apiClient.get('/interviews/ability-insights')
  },

  /**
   * 获取历史统计数据
   * GET /interviews/history/statistics
   */
  getHistoryStatistics: () => {
    return apiClient.get('/interviews/history/statistics')
  },

  /**
   * 获取面试详情
   * GET /interviews/{interviewId}/detail
   */
  getInterviewDetail: (interviewId) => {
    return apiClient.get(`/interviews/${interviewId}/detail`)
  },

  /**
   * 删除面试记录
   * DELETE /interviews/{interviewId}
   */
  deleteInterview: (interviewId) => {
    return apiClient.delete(`/interviews/${interviewId}`)
  },

  /**
   * 批量删除面试记录
   * POST /interviews/batch-delete
   */
  batchDeleteInterviews: (interviewIds) => {
    console.log('🗑️ API调用: batchDeleteInterviews', interviewIds)
    return apiClient.post('/interviews/batch-delete', { interview_ids: interviewIds })
  },

  /**
   * 导出面试记录
   * GET /interviews/export
   */
  exportInterviews: (params) => {
    console.log('📤 API调用: exportInterviews', params)
    return apiClient.get('/interviews/export', {
      params,
      responseType: 'blob'  // 用于文件下载
    })
  },
  /**
   * 获取面试统计图表数据
   * GET /interviews/statistics/charts
   */
  getStatisticsCharts: (params) => {
    console.log('📊 API调用: getStatisticsCharts', params)
    return apiClient.get('/interviews/statistics/charts', { params })
  },

  /**
   * 复制面试设置
   * POST /interviews/{interviewId}/copy-settings
   */
  copyInterviewSettings: (interviewId) => {
    return apiClient.post(`/interviews/${interviewId}/copy-settings`)
  }
  }



  /**
   * 分析报告相关API
   */
  analysis = {
    /**
     * 获取面试报告
     * GET /analysis/report/{interviewId}
     * @param {String} interviewId - 面试ID
     * @returns {Promise} - 详细报告
     */
    getReport: () => {
      // TODO: 后端实现后启用
      // return apiClient.get(`/analysis/report/${interviewId}`)

      // 返回模拟数据
      return Promise.resolve({
        overall: 85,
        dimensions: {
          professional: 90,
          expression: 85,
          logic: 88,
          adaptability: 82,
          attitude: 80,
        },
        feedback: {
          pros: ['表达清晰', '逻辑性强'],
          cons: ['需要更多实际案例'],
          suggestions: ['建议补充项目经验'],
        },
      })
    },

    /**
     * 获取能力趋势
     * GET /analysis/trends
     * @returns {Promise} - 能力变化趋势
     */
    getTrends: () => {
      return apiClient.get('/analysis/trends')
    },
  }

  /**
   * 题库相关API
   */
  question = {
    /**
     * 获取题目列表
     * GET /questions
     * @param {Object} params - {position, type, difficulty}
     * @returns {Promise} - 题目列表
     */
    getList: () => {
      // TODO: 后端实现后启用
      // return apiClient.get('/questions', { params })

      // 返回模拟数据
      return Promise.resolve([
        {
          id: 1,
          category: '技术基础',
          question: '请解释一下Vue3的Composition API',
          difficulty: 'medium',
          tags: ['Vue.js', '前端框架'],
        },
      ])
    },

    /**
     * 获取岗位要求
     * GET /questions/positions/{type}
     * @param {String} type - 岗位类型
     * @returns {Promise} - 岗位详情
     */
    getPositionInfo: (type) => {
      // TODO: 后端实现后启用
      // return apiClient.get(`/questions/positions/${type}`)

      // 返回模拟数据
      const positions = {
        it: {
          title: '互联网IT岗位',
          description: '包括前端、后端、算法等技术岗位',
          requirements: ['扎实的编程基础', '良好的学习能力', '团队协作精神'],
          skills: ['编程语言', '数据结构', '网络协议', '数据库'],
        },
        finance: {
          title: '金融行业岗位',
          description: '包括投资、风控、数据分析等岗位',
          requirements: ['金融专业知识', '数据分析能力', '风险意识'],
          skills: ['财务分析', '数据建模', 'Excel/Python', '行业研究'],
        },
        education: {
          title: '教育行业岗位',
          description: '包括教师、教研、运营等岗位',
          requirements: ['教育理念', '沟通能力', '耐心细致'],
          skills: ['学科知识', '教学设计', '班级管理', '家长沟通'],
        },
      }
      return Promise.resolve(positions[type] || {})
    },
  }

  /**
   * WebSocket连接管理
   */
  websocket = {
    /**
     * 建立WebSocket连接
     * @param {String} interviewId - 面试ID
     * @returns {WebSocket}
     */
    connect: (interviewId) => {
      const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/interview/${interviewId}`
      return new WebSocket(wsUrl)
    },
  }
}

// 导出单例
export default new ApiService()
