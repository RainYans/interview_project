<template>
  <div class="performance-container">
    <div class="page-header">
      <h2 class="page-title">面试表现分析</h2>
      <p class="page-subtitle">全方位评估您的面试能力，追踪进步轨迹</p>
    </div>

    <!-- 综合评分 -->
    <div class="overview-section">
      <div class="score-card glass-card">
        <div class="score-main">
          <div class="score-circle">
            <svg width="200" height="200">
              <circle
                cx="100"
                cy="100"
                r="90"
                stroke="rgba(255, 255, 255, 0.1)"
                stroke-width="20"
                fill="none"
              />
              <circle
                cx="100"
                cy="100"
                r="90"
                :stroke="scoreColor"
                stroke-width="20"
                fill="none"
                :stroke-dasharray="scoreCircumference"
                :stroke-dashoffset="scoreOffset"
                transform="rotate(-90 100 100)"
                style="transition: stroke-dashoffset 1s ease"
              />
            </svg>
            <div class="score-text">
              <span class="score-number">{{ overallScore }}</span>
              <span class="score-label">综合评分</span>
            </div>
          </div>
        </div>
        <div class="score-info">
          <h3>表现评级：{{ scoreLevel }}</h3>
          <p>{{ scoreComment }}</p>
          <div class="score-stats">
            <div class="stat-item">
              <span class="stat-label">超过了</span>
              <span class="stat-value">{{ betterThan }}%</span>
              <span class="stat-label">的用户</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">本月提升</span>
              <span class="stat-value">{{ improvement }}%</span>
              <span class="stat-label">↑</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 能力雷达图 -->
    <div class="radar-section glass-card">
      <div class="section-header">
        <h3>能力维度分析</h3>
        <el-button-group>
          <el-button
            v-for="period in periods"
            :key="period.value"
            :type="selectedPeriod === period.value ? 'primary' : ''"
            @click="changePeriod(period.value)"
            size="small"
          >
            {{ period.label }}
          </el-button>
        </el-button-group>
      </div>
      <div ref="radarChart" class="radar-chart"></div>
    </div>

    <!-- 详细指标 -->
    <div class="metrics-section">
      <h3>详细指标分析</h3>
      <div class="metrics-grid">
        <div
          v-for="metric in detailMetrics"
          :key="metric.name"
          class="metric-card glass-card hover-float"
        >
          <div class="metric-header">
            <el-icon :size="30" :color="metric.color">
              <component :is="metric.icon" />
            </el-icon>
            <span class="metric-name">{{ metric.name }}</span>
          </div>
          <div class="metric-score">
            <span class="score">{{ metric.score }}</span>
            <span class="total">/100</span>
          </div>
          <el-progress
            :percentage="metric.score"
            :color="metric.color"
            :show-text="false"
          />
          <div class="metric-details">
            <p class="metric-desc">{{ metric.description }}</p>
            <div class="metric-tags">
              <el-tag
                v-for="tag in metric.tags"
                :key="tag"
                size="small"
                type="info"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
          <div class="metric-feedback">
            <h5>改进建议</h5>
            <ul>
              <li v-for="(suggestion, index) in metric.suggestions" :key="index">
                {{ suggestion }}
              </li>
            </ul>
          </div>
          <div class="metric-actions">
            <el-button size="small" @click="startTargetedPractice(metric.name)">
              针对练习
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史趋势 -->
    <div class="trend-section glass-card">
      <div class="section-header">
        <h3>能力提升趋势</h3>
        <el-select v-model="trendDimension" size="small" @change="updateTrendChart">
          <el-option label="综合评分" value="overall" />
          <el-option label="专业知识" value="professional" />
          <el-option label="表达能力" value="expression" />
          <el-option label="逻辑思维" value="logic" />
        </el-select>
      </div>
      <div ref="trendChart" class="trend-chart"></div>
    </div>

    <!-- 面试记录 -->
    <div class="records-section glass-card">
      <h3>最近面试记录</h3>
      <el-table :data="recentRecords" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'simulation' ? 'primary' : 'success'">
              {{ scope.row.type === 'simulation' ? '模拟面试' : '练习模式' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="position" label="岗位" />
        <el-table-column prop="duration" label="时长" />
        <el-table-column prop="score" label="得分" width="100">
          <template #default="scope">
            <span class="score-text" :style="{ color: getScoreColor(scope.row.score) }">
              {{ scope.row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">
              查看详情
            </el-button>
            <el-button size="small" type="primary" @click="replay(scope.row)">
              回放
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 个性化建议 -->
    <div class="advice-section glass-card">
      <h3>AI个性化建议</h3>
      <div class="advice-content">
        <el-alert
          v-for="(advice, index) in personalAdvice"
          :key="index"
          :type="advice.type"
          :closable="false"
          show-icon
        >
          <template #title>
            {{ advice.title }}
          </template>
          <template #default>
            <p>{{ advice.content }}</p>
            <el-button
              v-if="advice.action"
              type="text"
              size="small"
              @click="handleAdviceAction(advice.action, advice.actionData)"
            >
              {{ advice.actionText }} →
            </el-button>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="面试详情"
      width="80%"
      top="5vh"
      @close="closeDetailDialog"
      destroy-on-close
    >
      <div class="detail-content" v-if="currentRecord">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="面试类型">
              {{ currentRecord.type === 'simulation' ? '模拟面试' : '练习模式' }}
            </el-descriptions-item>
            <el-descriptions-item label="面试公司">
              {{ currentRecord.company }}
            </el-descriptions-item>
            <el-descriptions-item label="应聘岗位">
              {{ currentRecord.position }}
            </el-descriptions-item>
            <el-descriptions-item label="面试时间">
              {{ formatDate(currentRecord.date) }}
            </el-descriptions-item>
            <el-descriptions-item label="面试时长">
              {{ currentRecord.duration }}
            </el-descriptions-item>
            <el-descriptions-item label="综合评分">
              {{ currentRecord.score }}分
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 详细分析 -->
        <div class="detail-section">
          <h4>详细分析</h4>
          <div class="analysis-charts">
            <div class="chart-container">
              <h5>能力雷达图</h5>
              <div ref="detailRadarChart" class="detail-radar-chart"></div>
            </div>
            <div class="chart-container">
              <h5>表现时间线</h5>
              <div ref="timelineChart" class="timeline-chart"></div>
            </div>
          </div>
        </div>

        <!-- 问答记录 -->
        <div class="detail-section" v-if="currentRecord.qaRecords && currentRecord.qaRecords.length > 0">
          <h4>问答记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(qa, index) in currentRecord.qaRecords"
              :key="index"
              :timestamp="qa.timestamp"
            >
              <div class="qa-item">
                <div class="question">
                  <el-icon><QuestionFilled /></el-icon>
                  <span>{{ qa.question }}</span>
                </div>
                <div class="answer">
                  <el-icon><Comment /></el-icon>
                  <span>{{ qa.answer }}</span>
                </div>
                <div class="qa-feedback" v-if="qa.feedback">
                  <el-tag type="info" size="small">AI反馈</el-tag>
                  <span>{{ qa.feedback }}</span>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDetailDialog">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 回放对话框 -->
    <el-dialog
      v-model="showReplayDialog"
      title="面试回放"
      width="90%"
      top="5vh"
    >
      <div class="replay-content">
        <div class="video-container">
          <video
            ref="replayVideo"
            controls
            class="replay-video"
            @loadedmetadata="onVideoLoaded"
          >
            <source :src="replayVideoSrc" type="video/mp4">
            您的浏览器不支持视频播放
          </video>
        </div>
        <div class="replay-controls">
          <el-button @click="playFromTimestamp('00:05:30')">跳转到自我介绍</el-button>
          <el-button @click="playFromTimestamp('00:12:15')">跳转到技术问答</el-button>
          <el-button @click="playFromTimestamp('00:18:45')">跳转到项目介绍</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Reading,
  ChatLineSquare,
  TrendCharts,
  Timer,
  Trophy,
  QuestionFilled,
  Comment
} from '@element-plus/icons-vue'
import apiService from '@/api/service.js'

const router = useRouter()

// ================================================================================================
// 🎯 第一部分：基础状态管理
// ================================================================================================

const loading = ref({
  performance: false,
  trend: false,
  history: false,
  advice: false,
  detail: false
})

const error = ref({
  performance: null,
  trend: null,
  history: null,
  advice: null
})

// 图表实例管理
let mainRadarChartInstance = null
let mainTrendChartInstance = null
let detailRadarChartInstance = null
let timelineChartInstance = null

// DOM引用
const radarChart = ref(null)
const trendChart = ref(null)
const detailRadarChart = ref(null)
const timelineChart = ref(null)
const replayVideo = ref(null)

// ================================================================================================
// 📊 第二部分：数据状态管理
// ================================================================================================

const performanceData = ref({
  overall_score: 0,
  ability_scores: {
    professional: 0,
    skill_match: 0,
    language_expression: 0,
    logical_thinking: 0,
    comprehensive_quality: 0
  },
  better_than: 0,
  improvement: 0,
  recent_records: []
})

const trendData = ref({
  dates: [],
  scores: [],
  labels: []
})

const personalAdviceData = ref([])

// 界面状态
const overallScore = ref(0)
const selectedPeriod = ref('current')
const trendDimension = ref('overall')
const showDetailDialog = ref(false)
const showReplayDialog = ref(false)
const currentRecord = ref(null)
const replayVideoSrc = ref('')

// 时间周期选项
const periods = [
  { label: '本次', value: 'current' },
  { label: '近一周', value: 'week' },
  { label: '近一月', value: 'month' }
]

// ================================================================================================
// 💫 第三部分：计算属性
// ================================================================================================

const scoreCircumference = computed(() => `${2 * Math.PI * 90}`)
const scoreOffset = computed(() => {
  const percentage = (100 - overallScore.value) / 100
  return percentage * 2 * Math.PI * 90
})

const scoreColor = computed(() => {
  if (overallScore.value >= 90) return '#67c23a'
  if (overallScore.value >= 80) return '#409eff'
  if (overallScore.value >= 70) return '#e6a23c'
  return '#f56c6c'
})

const scoreLevel = computed(() => {
  if (overallScore.value >= 90) return '优秀'
  if (overallScore.value >= 80) return '良好'
  if (overallScore.value >= 70) return '中等'
  if (overallScore.value >= 60) return '及格'
  return '待提升'
})

const scoreComment = computed(() => {
  if (overallScore.value >= 90) return '您的面试表现非常出色，保持这个状态！'
  if (overallScore.value >= 80) return '表现良好，还有一些细节可以优化'
  if (overallScore.value >= 70) return '基础扎实，需要加强某些方面的训练'
  return '建议多加练习，重点提升薄弱环节'
})

const betterThan = ref(0)
const improvement = ref(0)

// ================================================================================================
// 📋 第四部分：详细指标数据
// ================================================================================================

const detailMetrics = ref([
  {
    name: '专业知识',
    score: 0,
    icon: 'Reading',
    color: '#409eff',
    description: '技术深度和广度的综合评估',
    tags: ['算法', '数据结构', '框架原理'],
    suggestions: [
      '建议深入学习Vue3的响应式原理',
      '加强对算法复杂度分析的理解'
    ]
  },
  {
    name: '表达能力',
    score: 0,
    icon: 'ChatLineSquare',
    color: '#67c23a',
    description: '语言组织和沟通效果评估',
    tags: ['逻辑清晰', '语速适中'],
    suggestions: [
      '回答时可以更多使用STAR法则',
      '适当增加一些具体的案例说明'
    ]
  },
  {
    name: '逻辑思维',
    score: 0,
    icon: 'TrendCharts',
    color: '#e6a23c',
    description: '问题分析和解决方案的逻辑性',
    tags: ['结构化思维', '问题拆解'],
    suggestions: [
      '在复杂问题上可以先理清思路再回答',
      '多使用"首先、其次、最后"等结构化表达'
    ]
  },
  {
    name: '应变能力',
    score: 0,
    icon: 'Timer',
    color: '#f56c6c',
    description: '面对压力和突发问题的处理能力',
    tags: ['冷静应对', '灵活变通'],
    suggestions: [
      '遇到不会的问题可以坦诚说明思考过程',
      '多练习一些压力面试场景'
    ]
  },
  {
    name: '职业素养',
    score: 0,
    icon: 'Trophy',
    color: '#909399',
    description: '职业态度和综合素质评估',
    tags: ['积极主动', '团队意识'],
    suggestions: [
      '保持当前的职业态度',
      '可以多了解目标公司的文化价值观'
    ]
  }
])

const recentRecords = ref([])
const personalAdvice = ref([])

// ================================================================================================
// 🤖 第五部分：AI数据获取接口区域
// ================================================================================================

/**
 * 🚨 需要真实数据：获取最新面试的AI分析得分
 *
 * 当前问题：从历史记录获取原始分数，缺少AI深度分析
 * 需要对接：AI面试分析API
 *
 * 应该返回：
 * - AI分析后的各维度能力得分（不是简单的历史记录分数）
 * - 基于答题内容、语音语调、逻辑思维等综合分析结果
 * - 面试表现的细节反馈
 */
const fetchLatestInterviewScores = async () => {
  // 🚨 AI接口调用示例代码位置：
  // try {
  //   const response = await apiService.ai.getLatestInterviewAnalysis({
  //     user_id: getCurrentUserId(),
  //     analysis_type: 'comprehensive'
  //   })
  //
  //   return {
  //     interviewId: response.data.interview_id,
  //     date: response.data.interview_date,
  //     abilityScores: {
  //       professional: Math.round(response.data.ai_analysis.professional_score),
  //       language_expression: Math.round(response.data.ai_analysis.expression_score),
  //       logical_thinking: Math.round(response.data.ai_analysis.logic_score),
  //       comprehensive_quality: Math.round(response.data.ai_analysis.adaptability_score),
  //       skill_match: Math.round(response.data.ai_analysis.skill_match_score)
  //     },
  //     aiInsights: response.data.ai_analysis.detailed_insights,
  //     performanceMetrics: response.data.ai_analysis.performance_metrics
  //   }
  // } catch (error) {
  //   console.error('AI分析获取失败:', error)
  //   return null
  // }

  // 🚨 当前使用模拟数据（AI对接后可删除）
  try {
    const historyResponse = await apiService.interview.getHistory({
      page: 1,
      page_size: 1
    })

    if (historyResponse?.data?.list?.length > 0) {
      const latestInterview = historyResponse.data.list[0]

      if (latestInterview.scores) {
        return {
          interviewId: latestInterview.id,
          date: latestInterview.date,
          abilityScores: {
            professional: Math.round(latestInterview.scores.professional || 0),
            language_expression: Math.round(latestInterview.scores.expression || 0),
            logical_thinking: Math.round(latestInterview.scores.logic || 0),
            comprehensive_quality: Math.round(latestInterview.scores.adaptability || 0),
            skill_match: Math.round(latestInterview.scores.attitude || 0)
          }
        }
      }
    }

    return null
  } catch (error) {
    return null
  }
}

/**
 * 🚨 需要真实数据：历史能力对比分析
 *
 * 当前问题：使用随机生成的对比数据
 * 需要对接：历史数据分析API
 *
 * 应该返回：
 * - 用户历史面试的能力趋势
 * - 与上个月/上次面试的真实对比
 * - 能力提升或下降的具体数据
 */
const fetchHistoricalComparison = async (currentScores) => {
  // 🚨 AI接口调用示例代码位置：
  // try {
  //   const response = await apiService.ai.getHistoricalComparison({
  //     user_id: getCurrentUserId(),
  //     current_scores: currentScores,
  //     comparison_period: 'last_month',
  //     metrics: ['professional', 'language_expression', 'logical_thinking', 'comprehensive_quality', 'skill_match']
  //   })
  //
  //   return {
  //     previous: [
  //       Math.round(response.data.historical_avg.professional),
  //       Math.round(response.data.historical_avg.language_expression),
  //       Math.round(response.data.historical_avg.logical_thinking),
  //       Math.round(response.data.historical_avg.comprehensive_quality),
  //       Math.round(response.data.historical_avg.skill_match)
  //     ],
  //     hasHistoryData: response.data.has_sufficient_data,
  //     trendAnalysis: response.data.trend_analysis
  //   }
  // } catch (error) {
  //   console.error('历史对比数据获取失败:', error)
  //   return generateReasonableComparison(currentScores)
  // }

  // 🚨 当前使用合理的模拟对比数据（AI对接后可删除）
  if (!currentScores) {
    return {
      previous: [70, 68, 72, 65, 75], // 🚨 模拟数据
      hasHistoryData: false
    }
  }

  // 🚨 这里是随机生成的对比数据，需要真实历史数据
  const previousScores = Object.values(currentScores).map(score => {
    const change = Math.floor(Math.random() * 11) - 5 // -5到+5的变化
    return Math.max(0, Math.min(100, Math.round(score + change)))
  })

  return {
    previous: previousScores, // 🚨 需要真实历史数据
    hasHistoryData: true
  }
}

/**
 * 🚨 需要真实数据：AI能力深度洞察分析
 *
 * 当前问题：基于分数简单判断，缺少AI深度分析
 * 需要对接：AI洞察分析API
 *
 * 应该返回：
 * - AI基于面试内容的深度分析
 * - 个性化的能力提升建议
 * - 针对性的练习推荐
 */
const generateAbilityInsights = async (abilityScores) => {
  // 🚨 AI接口调用示例代码位置：
  // try {
  //   const response = await apiService.ai.generateAbilityInsights({
  //     user_id: getCurrentUserId(),
  //     ability_scores: abilityScores,
  //     interview_content: await getLatestInterviewContent(),
  //     user_profile: await getUserProfile(),
  //     target_position: await getTargetPosition()
  //   })
  //
  //   return response.data.insights.map(insight => ({
  //     ability: insight.ability_name,
  //     suggestions: insight.improvement_suggestions,
  //     strengths: insight.identified_strengths,
  //     practiceRecommendations: insight.practice_recommendations,
  //     personalizedTips: insight.personalized_tips
  //   }))
  // } catch (error) {
  //   console.error('AI洞察分析失败:', error)
  //   return getDefaultInsights(abilityScores)
  // }

  // 🚨 当前使用基于分数的智能建议（AI对接后可删除）
  const insights = []

  Object.entries(abilityScores).forEach(([key, score]) => {
    let suggestions = []

    // 🚨 这里是固定的分数判断逻辑，需要AI个性化分析
    if (score >= 85) {
      suggestions = ['保持当前优势', '可以尝试更高难度的挑战'] // 🚨 固定建议
    } else if (score >= 70) {
      suggestions = ['继续巩固基础', '针对性练习提升'] // 🚨 固定建议
    } else {
      suggestions = ['重点加强训练', '建议系统性学习'] // 🚨 固定建议
    }

    insights.push({ ability: key, suggestions })
  })

  return insights
}

/**
 * 🚨 需要真实数据：用户表现统计
 *
 * 当前问题：betterThan和improvement使用随机数据
 * 需要对接：用户表现统计API
 */
const fetchUserPerformanceStats = async () => {
  // 🚨 AI接口调用示例代码位置：
  // try {
  //   const response = await apiService.user.getPerformanceStats({
  //     user_id: getCurrentUserId(),
  //     time_period: 'current_month'
  //   })
  //
  //   return {
  //     betterThanPercentage: response.data.better_than_percentage,
  //     monthlyImprovement: response.data.monthly_improvement,
  //     rankingInfo: response.data.ranking_info,
  //     progressMetrics: response.data.progress_metrics
  //   }
  // } catch (error) {
  //   console.error('用户统计数据获取失败:', error)
  //   return null
  // }

  // 🚨 当前返回null，在fetchPerformanceData中使用随机数据
  return null
}

// ================================================================================================
// 📡 第六部分：数据获取方法
// ================================================================================================

const fetchPerformanceData = async () => {
  try {
    loading.value.performance = true
    error.value.performance = null

    // 获取最新面试的具体能力得分
    const latestScores = await fetchLatestInterviewScores()

    if (latestScores) {
      // 使用具体面试的能力得分
      const abilityScores = latestScores.abilityScores
      overallScore.value = Math.round(Object.values(abilityScores).reduce((a, b) => a + b, 0) / Object.values(abilityScores).length)

      updateDetailMetricsFromScores(abilityScores)
      updateRadarChartFromScores(abilityScores)

      // 🚨 获取真实的用户统计数据
      const statsData = await fetchUserPerformanceStats()
      if (statsData) {
        betterThan.value = statsData.betterThanPercentage
        improvement.value = statsData.monthlyImprovement
      } else {
        // 🚨 无统计数据时使用模拟数据（需要改为真实API）
        betterThan.value = Math.round(Math.random() * 30 + 60) // 🚨 随机排名数据
        improvement.value = Math.round(Math.random() * 20 + 5) // 🚨 随机提升数据
      }

    } else {
      // 没有面试数据时的处理
      displayNoInterviewData()
    }

    // 获取最近记录
    await fetchRecentRecords()

  } catch (err) {
    error.value.performance = err.response?.data?.detail || err.message || '获取数据失败'
    ElMessage.error('获取面试表现数据失败')
    displayNoInterviewData()

  } finally {
    loading.value.performance = false
  }
}

const fetchRecentRecords = async () => {
  try {
    const response = await apiService.interview.getHistory({
      page: 1,
      page_size: 5
    })

    if (response?.data?.list) {
      recentRecords.value = response.data.list.map(record => ({
        id: record.id,
        date: record.date,
        type: record.type || 'practice',
        company: record.company || '模拟公司',
        position: record.position || '前端开发',
        duration: record.duration || '30分钟',
        score: Math.round(Number(record.score) || 0)
      }))
    }
  } catch (error) {
    recentRecords.value = []
  }
}

/**
 * 🚨 需要真实数据：能力提升趋势
 *
 * 当前问题：无数据时使用generateMockTrendData()
 * 需要对接：确保趋势分析API返回真实数据
 */
const fetchTrendData = async (dimension = 'overall', period = 'month') => {
  try {
    loading.value.trend = true
    error.value.trend = null

    const response = await apiService.interview.getTrend({
      dimension,
      period,
      aggregation: 'individual'
    })

    if (response?.data && response.data.dates && response.data.scores) {
      // ✅ 有真实数据时使用真实数据
      trendData.value = {
        dates: response.data.dates || [],
        scores: response.data.scores?.map(score => Math.round(score)) || [],
        labels: response.data.labels || []
      }
    } else {
      // 🚨 无数据时使用模拟数据，需要改为显示"暂无数据"
      generateMockTrendData() // 🚨 这个方法生成模拟数据，应该改为显示无数据状态
    }

    if (mainTrendChartInstance) {
      updateTrendChartDisplay()
    }

  } catch (err) {
    error.value.trend = err.response?.data?.detail || err.message || '获取趋势数据失败'
    // 🚨 出错时也使用模拟数据，需要改为显示错误状态
    generateMockTrendData() // 🚨 应该改为显示错误信息而不是模拟数据

  } finally {
    loading.value.trend = false
  }
}

/**
 * 🚨 需要真实数据：AI个性化建议
 *
 * 当前问题：无数据时使用getDefaultAdvice()返回固定建议
 * 需要对接：确保个人建议API返回AI生成的建议
 */
const fetchPersonalAdvice = async () => {
  try {
    loading.value.advice = true

    const response = await apiService.interview.getPersonalAdvice()

    if (response?.data && Array.isArray(response.data) && response.data.length > 0) {
      // ✅ 有真实数据时使用真实数据
      personalAdvice.value = response.data.map(advice => ({
        type: advice.type || 'info',
        title: advice.title || '建议',
        content: advice.content || '',
        action: advice.action || null,
        actionText: advice.action_text || advice.actionText || null,
        actionData: advice.action_data || advice.actionData || null
      }))
    } else {
      // 🚨 无数据时使用固定默认建议，需要AI生成个性化建议
      personalAdvice.value = getDefaultAdvice() // 🚨 固定建议，需要AI生成
    }

  } catch (err) {
    // 🚨 出错时使用固定默认建议，需要AI生成个性化建议
    personalAdvice.value = getDefaultAdvice() // 🚨 固定建议，需要AI生成

  } finally {
    loading.value.advice = false
  }
}

// ================================================================================================
// 🔧 第七部分：数据处理方法
// ================================================================================================

const updateDetailMetricsFromScores = (abilityScores) => {
  const scoreMapping = {
    '专业知识': abilityScores.professional || 0,
    '表达能力': abilityScores.language_expression || 0,
    '逻辑思维': abilityScores.logical_thinking || 0,
    '应变能力': abilityScores.comprehensive_quality || 0,
    '职业素养': abilityScores.skill_match || 0
  }

  detailMetrics.value = detailMetrics.value.map(metric => ({
    ...metric,
    score: Math.round(scoreMapping[metric.name] || 0)
  }))
}

const updateRadarChartFromScores = async (abilityScores) => {
  if (!mainRadarChartInstance) return

  const currentData = [
    abilityScores.professional || 0,
    abilityScores.language_expression || 0,
    abilityScores.logical_thinking || 0,
    abilityScores.comprehensive_quality || 0,
    abilityScores.skill_match || 0
  ]

  const comparison = await fetchHistoricalComparison(abilityScores)
  const previousData = comparison.previous || currentData.map(score => Math.max(0, score - 5))

  const option = {
    series: [{
      data: [
        {
          value: currentData,
          name: '当前能力',
          lineStyle: { color: '#409eff', width: 2 },
          areaStyle: { color: 'rgba(64, 158, 255, 0.3)' },
          itemStyle: { color: '#409eff' }
        },
        {
          value: previousData,
          name: comparison.hasHistoryData ? '上月能力' : '参考水平',
          lineStyle: { color: '#67c23a', width: 2, type: 'dashed' },
          areaStyle: { color: 'rgba(103, 194, 58, 0.2)' },
          itemStyle: { color: '#67c23a' }
        }
      ]
    }]
  }

  mainRadarChartInstance.setOption(option, { notMerge: false })
}

const displayNoInterviewData = () => {
  overallScore.value = 0
  betterThan.value = 0
  improvement.value = 0

  detailMetrics.value = detailMetrics.value.map(metric => ({
    ...metric,
    score: 0,
    description: '完成面试后将显示具体能力得分',
    suggestions: ['请先完成一次面试练习或模拟面试']
  }))

  if (mainRadarChartInstance) {
    const emptyOption = {
      title: {
        text: '暂无面试数据\n请先完成面试练习',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: 'var(--text-secondary)',
          fontSize: 16
        }
      },
      series: [{ data: [] }]
    }
    mainRadarChartInstance.setOption(emptyOption, true)
  }
}

/**
 * 🚨 需要删除：模拟趋势数据生成方法
 *
 * 当前问题：生成假的趋势数据
 * 需要处理：当无真实数据时，显示"暂无数据"而不是模拟数据
 */
const generateMockTrendData = () => {
  // 🚨 整个方法都是模拟数据，应该删除或改为显示无数据状态
  const dates = []
  const scores = []

  for (let i = 14; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))

    // 🚨 模拟分数生成逻辑，需要删除
    const baseScore = 70 + (14 - i) * 1.5
    const randomVariation = Math.floor(Math.random() * 11) - 5
    const score = Math.max(60, Math.min(95, Math.round(baseScore + randomVariation)))
    scores.push(score)
  }

  trendData.value = { dates, scores, labels: dates.map((_, index) => `第${index + 1}次`) }

  if (mainTrendChartInstance) {
    updateTrendChartDisplay()
  }
}

/**
 * 🚨 需要替换：固定的默认建议
 *
 * 当前问题：返回固定的建议内容
 * 需要改为：基于用户实际情况的AI建议
 */
const getDefaultAdvice = () => {
  // 🚨 AI接口调用示例代码位置：
  // 应该调用 AI生成个性化建议API
  // try {
  //   const response = await apiService.ai.generatePersonalizedAdvice({
  //     user_id: getCurrentUserId(),
  //     recent_performance: getRecentPerformanceData(),
  //     weak_areas: getIdentifiedWeakAreas(),
  //     learning_preferences: getUserLearningPreferences()
  //   })
  //
  //   return response.data.personalized_advice.map(advice => ({
  //     type: advice.priority_level, // 'info', 'warning', 'success'
  //     title: advice.title,
  //     content: advice.description,
  //     action: advice.recommended_action,
  //     actionText: advice.action_text,
  //     actionData: advice.action_parameters
  //   }))
  // } catch (error) {
  //   // 只有在AI服务不可用时才返回基础建议
  // }

  // 🚨 这里是固定建议，需要基于用户实际情况生成
  return [
    {
      type: 'info',
      title: '开始练习', // 🚨 固定内容
      content: '建议开始面试练习来提升您的技能和信心。', // 🚨 固定内容
      action: 'practice',
      actionText: '开始练习',
      actionData: { type: 'basic' }
    },
    {
      type: 'success',
      title: '持续改进', // 🚨 固定内容
      content: '通过定期练习和反馈来持续改进您的面试表现。', // 🚨 固定内容
      action: 'learning',
      actionText: '查看资源',
      actionData: { resource: 'tips' }
    }
  ]
}

// ================================================================================================
// 📊 第八部分：图表初始化和更新
// ================================================================================================

const initMainRadarChart = () => {
  if (!radarChart.value) return

  if (mainRadarChartInstance) {
    mainRadarChartInstance.dispose()
  }

  mainRadarChartInstance = echarts.init(radarChart.value)

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      textStyle: { color: '#fff' },
      formatter: function(params) {
        const abilities = ['专业知识', '表达能力', '逻辑思维', '应变能力', '职业素养']
        let content = `<div style="padding: 5px;">
          <div style="font-weight: bold; margin-bottom: 5px;">${params.seriesName}</div>`

        params.value.forEach((value, index) => {
          content += `<div>${abilities[index]}: ${Math.round(value)}分</div>`
        })

        content += '</div>'
        return content
      }
    },
    legend: {
      data: ['当前能力', '历史对比'],
      bottom: 10,
      textStyle: { color: 'var(--text-secondary)' }
    },
    radar: {
      indicator: [
        { name: '专业知识', max: 100 },
        { name: '表达能力', max: 100 },
        { name: '逻辑思维', max: 100 },
        { name: '应变能力', max: 100 },
        { name: '职业素养', max: 100 }
      ],
      center: ['50%', '50%'],
      radius: '65%',
      splitNumber: 5,
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.05)', 'rgba(64, 158, 255, 0.1)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: {
        color: 'var(--text-secondary)',
        formatter: function(value) {
          return Math.round(value)
        }
      }
    },
    series: [{
      name: '能力评分',
      type: 'radar',
      data: []
    }]
  }

  mainRadarChartInstance.setOption(option)
}

const initMainTrendChart = () => {
  if (!trendChart.value) return

  if (mainTrendChartInstance) {
    mainTrendChartInstance.dispose()
  }

  mainTrendChartInstance = echarts.init(trendChart.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      textStyle: { color: '#fff' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: [],
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'var(--text-secondary)' }
    },
    yAxis: {
      type: 'value',
      min: 60,
      max: 100,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'var(--text-secondary)' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    series: [{
      name: '评分趋势',
      type: 'line',
      smooth: true,
      data: [],
      lineStyle: { color: '#409eff', width: 3 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      },
      itemStyle: { color: '#409eff' },
      markLine: {
        data: [{ type: 'average', name: '平均值' }],
        lineStyle: { color: '#67c23a' }
      }
    }]
  }

  mainTrendChartInstance.setOption(option)
}

const updateTrendChartDisplay = () => {
  if (!mainTrendChartInstance || !trendData.value.dates) return

  const option = {
    xAxis: { data: trendData.value.dates },
    series: [{ data: trendData.value.scores }]
  }

  mainTrendChartInstance.setOption(option, { notMerge: false })
}

/**
 * 🚨 需要真实数据：面试详情分析图表
 *
 * 当前问题：使用固定的演示数据
 * 需要对接：具体面试的详细分析数据
 */
const initDetailCharts = () => {
  // 详情雷达图
  if (detailRadarChart.value) {
    if (detailRadarChartInstance) {
      detailRadarChartInstance.dispose()
    }

    detailRadarChartInstance = echarts.init(detailRadarChart.value)

    // 🚨 需要真实数据：应该从currentRecord获取真实的面试分析数据
    // TODO: 替换为真实的面试详情分析数据
    // const realScores = currentRecord.value?.detailedAnalysis?.abilityScores || [88, 82, 85, 79, 90]

    const radarOption = {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        textStyle: { color: '#fff' },
        formatter: function(params) {
          const abilities = ['专业知识', '表达能力', '逻辑思维', '应变能力', '职业素养']
          let content = `<div style="padding: 5px;">
            <div style="font-weight: bold; margin-bottom: 5px;">${params.seriesName}</div>`

          params.value.forEach((value, index) => {
            content += `<div>${abilities[index]}: ${Math.round(value)}分</div>`
          })

          content += '</div>'
          return content
        }
      },
      radar: {
        indicator: [
          { name: '专业知识', max: 100 },
          { name: '表达能力', max: 100 },
          { name: '逻辑思维', max: 100 },
          { name: '应变能力', max: 100 },
          { name: '职业素养', max: 100 }
        ],
        radius: '70%',
        center: ['50%', '50%'],
        axisLabel: {
          formatter: function(value) {
            return Math.round(value)
          }
        }
      },
      series: [{
        type: 'radar',
        data: [{
          value: [88, 82, 85, 79, 90], // 🚨 固定演示数据，需要从API获取真实数据
          name: '本次面试',
          lineStyle: { color: '#409eff', width: 2 },
          areaStyle: { color: 'rgba(64, 158, 255, 0.3)' },
          itemStyle: { color: '#409eff' }
        }]
      }]
    }

    detailRadarChartInstance.setOption(radarOption)
  }

  // 时间线图
  if (timelineChart.value) {
    if (timelineChartInstance) {
      timelineChartInstance.dispose()
    }

    timelineChartInstance = echarts.init(timelineChart.value)

    // 🚨 需要真实数据：应该从面试过程分析获取时间线数据
    // TODO: 替换为真实的面试时间线分析数据
    // const timelineData = currentRecord.value?.timelineAnalysis?.scores || [0, 85, 88, 82, 90, 85]

    const timelineOption = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        textStyle: { color: '#fff' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['开始', '自我介绍', '技术问答', '项目介绍', '提问环节', '结束'],
        axisLabel: { interval: 0, rotate: 0 }
      },
      yAxis: { type: 'value', max: 100, min: 0 },
      series: [{
        type: 'line',
        data: [0, 85, 88, 82, 90, 85], // 🚨 固定演示数据，需要从API获取真实数据
        lineStyle: { color: '#67c23a', width: 3 },
        itemStyle: { color: '#67c23a' },
        smooth: true,
        markPoint: {
          data: [
            { type: 'max', name: '最高分' },
            { type: 'min', name: '最低分' }
          ]
        }
      }]
    }

    timelineChartInstance.setOption(timelineOption)
  }
}

// ================================================================================================
// 🎮 第九部分：用户交互方法
// ================================================================================================

const changePeriod = async (period) => {
  selectedPeriod.value = period
  await fetchTrendData(trendDimension.value, period)
}

const updateTrendChart = async () => {
  await fetchTrendData(trendDimension.value, selectedPeriod.value)
}

const startTargetedPractice = async (metricName) => {
  try {
    const response = await apiService.interview.createTargetedPractice({
      target_ability: getScoreKey(metricName),
      difficulty_level: 'medium',
      practice_type: 'question_bank',
      duration: 30
    })

    if (response?.data) {
      ElMessage.success(`正在为您准备${metricName}的专项练习...`)

      if (response.data.recommended_sessions?.length > 0) {
        const session = response.data.recommended_sessions[0]
        router.push({
          path: '/dashboard/interview-practice',
          query: {
            plan_id: response.data.plan_id,
            focus: getScoreKey(metricName),
            type: session.type
          }
        })
      }
    }

  } catch (err) {
    ElMessage.error('创建练习计划失败')

    const practiceRoutes = {
      '专业知识': '/dashboard/interview-practice?focus=technical',
      '表达能力': '/dashboard/interview-practice?focus=expression',
      '逻辑思维': '/dashboard/interview-practice?focus=logic',
      '应变能力': '/dashboard/interview-practice?type=stress',
      '职业素养': '/dashboard/interview-practice?focus=professional'
    }

    const route = practiceRoutes[metricName]
    if (route) {
      router.push(route)
    }
  }
}

const viewDetail = async (record) => {
  try {
    loading.value.detail = true
    currentRecord.value = record
    showDetailDialog.value = true

    // 🚨 需要真实数据：获取面试详细分析数据
    try {
      const detailResponse = await apiService.interview.getDetailedAnalysis(record.id)
      if (detailResponse?.data) {
        // 🚨 应该包含AI分析的详细数据：
        // - detailedAnalysis.abilityScores: 各维度详细得分
        // - timelineAnalysis.scores: 面试过程时间线分析
        // - performanceInsights: AI洞察分析
        currentRecord.value = { ...record, ...detailResponse.data }
      }
    } catch (err) {
      // 使用基础数据
    }

    try {
      const qaResponse = await apiService.interview.getQARecords(record.id)
      if (qaResponse?.data) {
        currentRecord.value.qaRecords = qaResponse.data
      }
    } catch (err) {
      currentRecord.value.qaRecords = []
    }

    await nextTick()
    initDetailCharts()

  } catch (err) {
    ElMessage.error('获取面试详情失败')
  } finally {
    loading.value.detail = false
  }
}

const closeDetailDialog = () => {
  showDetailDialog.value = false
  currentRecord.value = null

  setTimeout(() => {
    if (detailRadarChartInstance) {
      detailRadarChartInstance.dispose()
      detailRadarChartInstance = null
    }

    if (timelineChartInstance) {
      timelineChartInstance.dispose()
      timelineChartInstance = null
    }
  }, 100)
}

const replay = async (record) => {
  try {
    const response = await apiService.interview.getReplayInfo(record.id)

    if (response?.data) {
      replayVideoSrc.value = response.data.video_url || response.data.audio_url
      currentRecord.value = record
      showReplayDialog.value = true

      if (response.data.video_url) {
        ElMessage.success('正在加载面试回放视频...')
      } else if (response.data.audio_url) {
        ElMessage.info('该面试只有音频回放')
      } else {
        ElMessage.warning('该面试暂无回放内容')
      }
    } else {
      ElMessage.warning('暂无回放内容')
    }

  } catch (err) {
    ElMessage.error('获取回放信息失败')
  }
}

const handleAdviceAction = (action, actionData) => {
  switch (action) {
    case 'knowledge':
      router.push(`/dashboard/knowledge-base?category=${actionData.category}`)
      break
    case 'practice':
      if (actionData.type === 'stress') {
        ElMessage.success('正在为您准备压力面试场景...')
        router.push(`/dashboard/interview-practice?type=${actionData.type}&difficulty=${actionData.difficulty}`)
      } else {
        router.push('/dashboard/interview-practice')
      }
      break
    case 'learning':
      router.push(`/dashboard/personalized-learning?resource=${actionData.resource}&chapter=${actionData.chapter}`)
      break
    default:
      ElMessage.info('功能开发中...')
  }
}

// ================================================================================================
// 🛠️ 第十部分：工具函数
// ================================================================================================

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getScoreKey = (metricName) => {
  const mapping = {
    '专业知识': 'professional',
    '表达能力': 'language_expression',
    '逻辑思维': 'logical_thinking',
    '应变能力': 'comprehensive_quality',
    '职业素养': 'skill_match'
  }
  return mapping[metricName] || 'professional'
}

const playFromTimestamp = (timestamp) => {
  if (replayVideo.value) {
    const parts = timestamp.split(':')
    const seconds = parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2])
    replayVideo.value.currentTime = seconds
    replayVideo.value.play()
  }
}

const onVideoLoaded = () => {
  ElMessage.success('视频加载完成')
}

const refreshAllData = async () => {
  try {
    ElMessage.info('正在刷新数据...')

    const results = await Promise.allSettled([
      fetchPerformanceData(),
      fetchTrendData(trendDimension.value, selectedPeriod.value),
      fetchPersonalAdvice()
    ])

    const failedCount = results.filter(result => result.status === 'rejected').length

    if (failedCount === 0) {
      ElMessage.success('数据刷新完成')
    } else if (failedCount < results.length) {
      ElMessage.warning(`部分数据刷新成功`)
    } else {
      ElMessage.error('数据刷新失败')
    }

  } catch (error) {
    ElMessage.error('数据刷新失败，请稍后重试')
  }
}

const handleChartResize = () => {
  if (mainRadarChartInstance && !showDetailDialog.value) {
    mainRadarChartInstance.resize()
  }

  if (mainTrendChartInstance && !showDetailDialog.value) {
    mainTrendChartInstance.resize()
  }

  if (showDetailDialog.value) {
    if (detailRadarChartInstance) {
      detailRadarChartInstance.resize()
    }
    if (timelineChartInstance) {
      timelineChartInstance.resize()
    }
  }
}

// ================================================================================================
// 🔄 第十一部分：生命周期管理
// ================================================================================================

watch(showDetailDialog, (newVal, oldVal) => {
  if (!newVal && oldVal) {
    // 对话框关闭时清理详情图表实例
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleChartResize)

  // 清理所有图表实例
  if (mainRadarChartInstance) {
    mainRadarChartInstance.dispose()
    mainRadarChartInstance = null
  }

  if (mainTrendChartInstance) {
    mainTrendChartInstance.dispose()
    mainTrendChartInstance = null
  }

  if (detailRadarChartInstance) {
    detailRadarChartInstance.dispose()
    detailRadarChartInstance = null
  }

  if (timelineChartInstance) {
    timelineChartInstance.dispose()
    timelineChartInstance = null
  }
})

onMounted(async () => {
  await nextTick()

  try {
    initMainRadarChart()
    initMainTrendChart()

    await refreshAllData()

    window.addEventListener('resize', handleChartResize)

  } catch (error) {
    ElMessage.error('页面初始化失败，请刷新重试')
  }
})

</script>

<style scoped>
.performance-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.page-subtitle {
  color: var(--text-secondary);
}

/* 综合评分 */
.overview-section {
  margin-bottom: 30px;
}

.score-card {
  display: flex;
  align-items: center;
  padding: 40px;
  gap: 60px;
}

.score-main {
  flex-shrink: 0;
}

.score-circle {
  position: relative;
  width: 200px;
  height: 200px;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  display: block;
  font-size: 3rem;
  font-weight: bold;
  background: var(--gradient-tech);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.score-label {
  display: block;
  color: var(--text-secondary);
  margin-top: 5px;
}

.score-info {
  flex: 1;
}

.score-info h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: var(--text-primary);
}

.score-info p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 25px;
}

.score-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-label {
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
}

/* 雷达图 */
.radar-section {
  padding: 30px;
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 1.3rem;
  color: var(--text-primary);
  margin: 0;
}

.radar-chart {
  height: 400px;
}

/* 详细指标 */
.metrics-section {
  margin-bottom: 30px;
}

.metrics-section h3 {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-card {
  padding: 25px;
  transition: all 0.3s ease;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.metric-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--text-primary);
}

.metric-score {
  margin-bottom: 10px;
}

.metric-score .score {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-primary);
}

.metric-score .total {
  color: var(--text-secondary);
  font-size: 1.2rem;
}

.metric-details {
  margin: 15px 0;
}

.metric-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 10px;
}

.metric-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.metric-feedback {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-feedback h5 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.metric-feedback ul {
  margin: 0;
  padding-left: 20px;
}

.metric-feedback li {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.8;
}

.metric-actions {
  margin-top: 15px;
  text-align: center;
}

/* 趋势图 */
.trend-section {
  padding: 30px;
  margin-bottom: 30px;
}

.trend-chart {
  height: 300px;
}

/* 面试记录 */
.records-section {
  padding: 30px;
  margin-bottom: 30px;
}

.records-section h3 {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.score-text {
  font-weight: bold;
}

/* 个性化建议 */
.advice-section {
  padding: 30px;
}

.advice-section h3 {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.advice-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 详情对话框 */
.detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h4 {
  font-size: 1.1rem;
  color: var(--text-primary);
  margin-bottom: 15px;
}

.analysis-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.chart-container {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  padding: 20px;
}

.chart-container h5 {
  color: var(--text-primary);
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
}

.detail-radar-chart,
.timeline-chart {
  height: 300px;
  width: 100%;
  min-height: 300px;
}

.qa-item {
  padding: 15px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.question,
.answer {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  line-height: 1.6;
}

.question {
  color: var(--text-primary);
  font-weight: bold;
}

.answer {
  color: var(--text-secondary);
}

.qa-feedback {
  margin-top: 10px;
  padding: 10px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.qa-feedback .el-tag {
  margin-right: 10px;
}

.dialog-footer {
  text-align: right;
}

/* 回放对话框 */
.replay-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-container {
  text-align: center;
}

.replay-video {
  width: 100%;
  max-width: 800px;
  height: auto;
  border-radius: 8px;
}

.replay-controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* 通用样式 */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.hover-float:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-card {
    flex-direction: column;
    text-align: center;
  }

  .score-stats {
    justify-content: center;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .analysis-charts {
    grid-template-columns: 1fr;
  }
}
</style>
