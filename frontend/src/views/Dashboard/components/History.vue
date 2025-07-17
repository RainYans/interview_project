<template>
  <div class="history-container">
    <div class="page-header">
      <h2 class="page-title">历史会话记录</h2>
      <p class="page-subtitle">回顾您的面试历程，追踪成长轨迹</p>
    </div>

    <!-- 筛选和统计 -->
    <div class="filter-section glass-card">
      <div class="filter-left">
        <el-select v-model="filters.type" placeholder="面试类型" clearable @change="handleSearchDebounced">
          <el-option label="全部类型" value="" />
          <el-option label="模拟面试" value="simulation" />
          <el-option label="练习模式" value="practice" />
        </el-select>

        <el-select v-model="filters.position" placeholder="岗位类型" clearable @change="handleSearchDebounced">
          <el-option label="全部岗位" value="" />
          <el-option label="前端开发" value="frontend" />
          <el-option label="后端开发" value="backend" />
          <el-option label="产品经理" value="product" />
          <el-option label="算法工程师" value="algorithm" />
        </el-select>

        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleSearchDebounced"
        />

        <el-button type="primary" @click="handleSearch" :loading="loading.history">
          搜索
        </el-button>
        <el-button @click="resetFilters">
          重置
        </el-button>
      </div>

      <div class="filter-right">
        <div class="stat-item">
          <span class="stat-label">总计</span>
          <span class="stat-value">{{ statistics.total_count }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">本月</span>
          <span class="stat-value">{{ statistics.month_count }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均分</span>
          <span class="stat-value">{{ statistics.avg_score }}</span>
        </div>
      </div>
    </div>

    <!-- 骨架屏加载状态 -->
    <div v-if="loading.history && isInitialLoad" class="loading-container">
      <div class="skeleton-list">
        <div v-for="i in 3" :key="i" class="skeleton-card">
          <div class="skeleton-header">
            <div class="skeleton-tag"></div>
            <div class="skeleton-date"></div>
          </div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-info"></div>
            <div class="skeleton-scores"></div>
          </div>
          <div class="skeleton-footer"></div>
        </div>
      </div>
    </div>

    <!-- 后续加载指示器 -->
    <div v-else-if="loading.history" class="loading-indicator">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在加载...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error.history" class="error-container">
      <el-alert
        title="获取历史记录失败"
        :description="error.history"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <el-button @click="loadHistory" type="primary" size="small">
            重新加载
          </el-button>
        </template>
      </el-alert>
    </div>

    <!-- 历史记录列表 -->
    <div v-else class="history-list">
      <div
        v-for="record in historyRecords"
        :key="record.id"
        class="history-card glass-card"
        @click="viewDetail(record)"
      >
        <div class="card-header">
          <div class="header-left">
            <el-tag :type="record.type === 'simulation' ? 'primary' : 'success'" size="small">
              {{ record.type === 'simulation' ? '模拟面试' : '练习模式' }}
            </el-tag>
            <span class="interview-date">{{ formatDate(record.date) }}</span>
          </div>
          <div class="header-right">
            <el-rate
              v-model="record.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}分"
            />
          </div>
        </div>

        <div class="card-content">
          <h3 class="interview-title">
            {{ record.company }} - {{ record.position }}
            <span class="interview-round">{{ record.round }}</span>
          </h3>

          <div class="interview-info">
            <div class="info-item">
              <el-icon><Timer /></el-icon>
              <span>时长：{{ record.duration }}</span>
            </div>
            <div class="info-item">
              <el-icon><ChatDotSquare /></el-icon>
              <span>问题：{{ record.questionCount }}个</span>
            </div>
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>面试官：{{ record.interviewer }}</span>
            </div>
          </div>

          <!-- 能力评分显示 -->
          <div class="score-overview" v-if="record.scores && Object.keys(record.scores).length > 0">
            <div
              v-for="(score, key) in record.scores"
              :key="key"
              class="score-item"
            >
              <span class="score-label">{{ scoreLabels[key] }}</span>
              <el-progress
                :percentage="score"
                :color="getScoreColor(score)"
                :stroke-width="6"
              />
            </div>
          </div>

          <!-- 关键反馈 -->
          <div class="key-feedback" v-if="record.keyFeedback">
            <p class="feedback-title">关键反馈：</p>
            <p class="feedback-content">{{ record.keyFeedback }}</p>
          </div>
        </div>

        <div class="card-footer">
          <el-button size="small" @click.stop="viewReport(record)">
            <el-icon><Document /></el-icon>
            查看报告
          </el-button>
          <el-button size="small" @click.stop="playback(record)" :disabled="!record.video_url">
            <el-icon><VideoPlay /></el-icon>
            视频回放
          </el-button>
          <el-button size="small" @click.stop="practiceAgain(record)">
            <el-icon><RefreshRight /></el-icon>
            再次练习
          </el-button>
          <el-button
            size="small"
            text
            type="danger"
            @click.stop="deleteRecord(record)"
            :loading="record._deleting"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading.history && !error.history && historyRecords.length === 0" class="empty-state">
      <el-empty description="暂无面试记录">
        <el-button type="primary" @click="startInterview">
          开始面试
        </el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div v-if="totalCount > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="面试详情"
      width="80%"
      top="5vh"
      destroy-on-close
      :loading="loading.detail"
    >
      <div class="detail-content" v-if="currentRecord && !loading.detail">
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
              {{ currentRecord.rating }}分
            </el-descriptions-item>
          </el-descriptions>
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

        <!-- 空状态 -->
        <div v-else class="detail-section">
          <h4>问答记录</h4>
          <el-empty description="暂无问答记录" :image-size="100" />
        </div>
      </div>

      <!-- 详情加载状态 -->
      <div v-else-if="loading.detail" class="detail-loading">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="rect" style="width: 100%; height: 300px;" />
          </template>
        </el-skeleton>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDetailDialog">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'HistoryView'
}
</script>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { debounce } from 'lodash'
import {
  Timer,
  ChatDotSquare,
  User,
  Document,
  VideoPlay,
  RefreshRight,
  Delete,
  QuestionFilled,
  Comment,
  Loading
} from '@element-plus/icons-vue'
import apiService from '@/api/service.js'

const router = useRouter()

// ================================================================================================
// 🎯 第一部分：基础状态管理
// ================================================================================================

const loading = reactive({
  history: false,
  detail: false,
  statistics: false
})

const error = reactive({
  history: null,
  detail: null
})

const isInitialLoad = ref(true)
const hasCache = ref(false)

// ================================================================================================
// 📊 第二部分：数据状态管理
// ================================================================================================

// 筛选条件
const filters = ref({
  type: '',
  position: '',
  dateRange: []
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

// 统计数据
const statistics = reactive({
  total_count: 0,
  month_count: 0,
  avg_score: 0,
  total_duration: 0,
  practice_count: 0,
  simulation_count: 0
})

// 历史记录数据
const historyRecords = ref([])

// 分数标签映射
const scoreLabels = {
  professional: '专业知识',
  expression: '表达能力',
  logic: '逻辑思维',
  adaptability: '应变能力',
  attitude: '职业素养'
}

// 当前查看的记录
const showDetailDialog = ref(false)
const currentRecord = ref(null)

// ================================================================================================
// 🤖 第三部分：API数据获取区域（需要标注真实数据位置）
// ================================================================================================

/**
 * 🚨 需要真实数据：获取历史记录列表
 *
 * 当前问题：API返回的数据结构与前端期望不完全匹配
 * 需要对接：确保后端API返回正确的数据结构
 */
const loadHistory = async () => {
  try {
    loading.history = true
    error.history = null

    // 优化缓存处理
    if (hasCache.value && !isInitialLoad.value) {
      loading.history = false
      await nextTick()
      loading.history = true
    }

    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      type: filters.value.type || undefined,
      position: filters.value.position || undefined,
      start_date: filters.value.dateRange?.[0] || undefined,
      end_date: filters.value.dateRange?.[1] || undefined
    }

    // 移除undefined值
    Object.keys(params).forEach(key =>
      params[key] === undefined && delete params[key]
    )

    // 🚨 调用后端API获取历史记录
    const response = await apiService.interview.getHistory(params)

    if (response && response.code === 200 && response.data) {
      const data = response.data

      // 🚨 数据结构映射 - 需要确保与后端返回结构匹配
      historyRecords.value = (data.list || []).map(record => ({
        id: record.id,
        type: record.type || 'practice',
        date: record.date,
        company: record.company || '模拟公司',
        position: record.position || '前端开发',
        round: record.round || '练习',
        duration: record.duration || '30分钟',
        // 🚨 字段名匹配问题修复
        questionCount: record.questionCount || record.question_count || 0,
        interviewer: record.interviewer || 'AI面试官',
        // 🚨 评分计算 - 后端返回的是百分制，前端显示为5分制
        rating: Math.round((record.rating || 0) * 5 / 100) || Math.round((record.overall_score || 80) / 20),
        scores: record.scores || null,
        // 🚨 字段名映射
        keyFeedback: record.keyFeedback || record.key_feedback || '',
        status: record.status || 'completed',
        video_url: record.video_url,
        _deleting: false
      }))

      totalCount.value = data.total || 0
      hasCache.value = true

      // 更新统计数据
      if (data.statistics) {
        Object.assign(statistics, data.statistics)
      }

    } else {
      throw new Error('获取历史记录失败：API响应格式错误')
    }

  } catch (err) {
    error.history = err.response?.data?.detail || err.message || '获取历史记录失败'

    // 只在初始加载时显示错误，后续加载失败保留缓存数据
    if (isInitialLoad.value) {
      ElMessage.error('获取历史记录失败：' + error.history)
      historyRecords.value = []
      totalCount.value = 0
    } else {
      ElMessage.warning('刷新数据失败，显示缓存数据')
    }

  } finally {
    loading.history = false
    isInitialLoad.value = false
  }
}

/**
 * 🚨 需要真实数据：获取统计数据
 *
 * 当前问题：统计数据可能需要实时计算
 * 需要对接：确保统计数据的准确性和实时性
 */
const loadStatistics = async () => {
  try {
    loading.statistics = true

    // 🚨 调用统计数据API
    const response = await apiService.interview.getHistoryStatistics()

    if (response && response.code === 200 && response.data) {
      // 🚨 更新统计数据 - 确保字段名匹配
      Object.assign(statistics, {
        total_count: response.data.total_count || 0,
        month_count: response.data.month_count || 0,
        avg_score: Math.round(response.data.avg_score || 0),
        total_duration: response.data.total_duration || 0,
        practice_count: response.data.practice_count || 0,
        simulation_count: response.data.simulation_count || 0
      })
    }

  } catch (err) {
    // 统计数据失败不影响主要功能
  } finally {
    loading.statistics = false
  }
}

/**
 * 🚨 需要真实数据：获取面试详细信息
 *
 * 当前问题：详细分析数据可能不够丰富
 * 需要对接：获取更详细的面试分析数据
 */
const loadDetailedRecord = async (recordId) => {
  try {
    loading.detail = true

    // 🚨 调用详细分析API
    const response = await apiService.interview.getDetailedAnalysis(recordId)

    if (response && response.code === 200 && response.data) {
      const detailData = response.data

      // 更新当前记录的详细信息
      currentRecord.value = {
        ...currentRecord.value,
        ...detailData,
        qaRecords: detailData.qaRecords || []
      }
    }

    // 🚨 获取问答记录 - 单独的API调用
    try {
      const qaResponse = await apiService.interview.getQARecords(recordId)
      if (qaResponse && qaResponse.code === 200 && qaResponse.data) {
        currentRecord.value.qaRecords = qaResponse.data
      }
    } catch (qaErr) {
      // 问答记录获取失败不影响基本信息显示
      currentRecord.value.qaRecords = []
    }

  } catch (err) {
    ElMessage.error('获取面试详情失败：' + (err.response?.data?.detail || err.message))
  } finally {
    loading.detail = false
  }
}

// ================================================================================================
// 🎮 第四部分：用户交互事件处理
// ================================================================================================

const handleSearch = async () => {
  currentPage.value = 1
  await loadHistory()
}

const handleSearchDebounced = debounce(handleSearch, 300)

const resetFilters = async () => {
  filters.value = {
    type: '',
    position: '',
    dateRange: []
  }
  currentPage.value = 1
  await loadHistory()
}

const handlePageChange = async (page) => {
  currentPage.value = page
  await loadHistory()
}

const handleSizeChange = async (size) => {
  pageSize.value = size
  currentPage.value = 1
  await loadHistory()
}

const viewDetail = async (record) => {
  currentRecord.value = record
  showDetailDialog.value = true
  await loadDetailedRecord(record.id)
}

const closeDetailDialog = () => {
  showDetailDialog.value = false
  currentRecord.value = null
}

const viewReport = (record) => {
  router.push({
    path: '/dashboard/performance',
    query: { interview_id: record.id }
  })
}

/**
 * 🚨 需要真实数据：获取回放信息
 *
 * 当前问题：回放功能可能需要视频/音频文件的真实URL
 * 需要对接：确保回放文件的可访问性
 */
const playback = async (record) => {
  try {
    // 🚨 调用回放信息API
    const response = await apiService.interview.getReplayInfo(record.id)

    if (response && response.code === 200 && response.data) {
      const replayData = response.data

      if (replayData.video_url || replayData.audio_url) {
        ElMessage.success('正在加载回放内容...')

        // 🚨 需要真实的回放URL
        if (replayData.video_url) {
          window.open(replayData.video_url, '_blank')
        } else if (replayData.audio_url) {
          window.open(replayData.audio_url, '_blank')
        }
      } else {
        ElMessage.warning('该面试暂无回放内容')
      }
    } else {
      ElMessage.warning('获取回放信息失败')
    }

  } catch (err) {
    ElMessage.error('获取回放信息失败：' + (err.response?.data?.detail || err.message))
  }
}

/**
 * 🚨 需要真实数据：复制面试设置
 *
 * 当前问题：面试设置的字段可能需要调整
 * 需要对接：确保设置数据的完整性
 */
const practiceAgain = async (record) => {
  try {
    await ElMessageBox.confirm(
      '是否基于这次面试的设置再次练习？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 🚨 调用复制设置API
    const response = await apiService.interview.copyInterviewSettings(record.id)

    if (response && response.code === 200 && response.data) {
      const settings = response.data

      // 🚨 跳转参数可能需要调整字段名
      router.push({
        path: '/dashboard/interview-practice',
        query: {
          type: settings.type,
          position: settings.position,
          company: settings.company,
          difficulty: settings.difficulty,
          duration: settings.duration,
          preset: 'copy'
        }
      })

      ElMessage.success('已为您准备相同设置的面试练习')
    } else {
      // 备用方案：使用基础信息
      router.push({
        path: '/dashboard/interview-practice',
        query: {
          position: record.position,
          company: record.company
        }
      })
      ElMessage.info('已为您准备相似的面试练习')
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const deleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      '删除后将无法恢复，确定要删除这条记录吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    record._deleting = true

    // 🚨 调用删除API
    const response = await apiService.interview.deleteInterview(record.id)

    if (response && response.code === 200) {
      // 从列表中移除
      const index = historyRecords.value.findIndex(r => r.id === record.id)
      if (index > -1) {
        historyRecords.value.splice(index, 1)
        totalCount.value--

        // 更新统计数据
        statistics.total_count = Math.max(0, statistics.total_count - 1)
      }

      ElMessage.success('删除成功')

      // 如果当前页没有数据了，回到上一页
      if (historyRecords.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
        await loadHistory()
      }
    } else {
      throw new Error('删除失败')
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    record._deleting = false
  }
}

const startInterview = () => {
  router.push('/dashboard/interview-practice')
}

// ================================================================================================
// 🛠️ 第五部分：工具函数
// ================================================================================================

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '未知时间'

  try {
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateStr
  }
}

// ================================================================================================
// 🔄 第六部分：生命周期管理
// ================================================================================================

onMounted(async () => {
  // 优化：先加载关键数据
  await loadHistory()

  // 然后加载统计数据（非关键）
  nextTick(() => {
    loadStatistics()
  })
})
</script>

<style scoped>
:root {
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  --card-hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  --skeleton-bg: rgba(255, 255, 255, 0.1);
}

.history-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 筛选区域 */
.filter-section {
  padding: 20px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-left {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  flex: 1;
}

.filter-right {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
}

/* 加载状态 */
.loading-container {
  margin-bottom: 30px;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.skeleton-tag {
  width: 80px;
  height: 24px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-date {
  width: 120px;
  height: 16px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-content {
  margin-bottom: 20px;
}

.skeleton-title {
  width: 60%;
  height: 20px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  margin-bottom: 15px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-info {
  width: 80%;
  height: 16px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  margin-bottom: 20px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-scores {
  width: 100%;
  height: 60px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  margin-bottom: 20px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-footer {
  width: 100%;
  height: 40px;
  background: var(--skeleton-bg);
  border-radius: 4px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 20px;
  color: var(--text-secondary);
}

@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.error-container {
  margin-bottom: 30px;
}

.detail-loading {
  padding: 20px 0;
}

/* 历史记录列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.history-card {
  padding: 25px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  will-change: transform;
}

.history-card:hover {
  transform: translate3d(0, -2px, 0);
  box-shadow: var(--card-hover-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.interview-date {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-content {
  margin-bottom: 20px;
}

.interview-title {
  font-size: 1.2rem;
  color: var(--text-primary);
  margin-bottom: 15px;
}

.interview-round {
  font-size: 14px;
  color: var(--text-secondary);
  margin-left: 10px;
}

.interview-info {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 能力评分 */
.score-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 关键反馈 */
.key-feedback {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.feedback-title {
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.feedback-content {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 0;
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 30px;
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

/* 通用样式 */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
  }

  .filter-left,
  .filter-right {
    width: 100%;
    justify-content: center;
  }

  .interview-info {
    flex-direction: column;
    gap: 10px;
  }

  .card-footer {
    flex-wrap: wrap;
  }
}
</style>
