# app/schemas/interview.py - 完整版本
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ===== 面试开始相关 =====

class InterviewStartRequest(BaseModel):
    """面试开始请求 - 匹配前端"""
    type: str = Field(..., description="面试类型: practice/simulation")
    position: str = Field(..., description="面试岗位")
    company: Optional[str] = Field(None, description="面试公司")
    difficulty: Optional[str] = Field("medium", description="难度: junior/medium/senior")
    interview_style: Optional[str] = Field("standard", description="面试风格")
    interviewer_id: Optional[int] = Field(None, description="面试官ID")
    round_type: Optional[str] = Field("first", description="面试轮次")
    duration: Optional[int] = Field(30, description="预期时长(分钟)")
    
    # 面试配置
    question_types: Optional[List[str]] = Field(default_factory=list, description="题目类型")
    special_settings: Optional[List[str]] = Field(default_factory=list, description="特殊设置")
    evaluation_focus: Optional[List[str]] = Field(default_factory=list, description="评估重点")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "practice",
                "position": "frontend",
                "difficulty": "medium",
                "interview_style": "gentle",
                "duration": 30,
                "question_types": ["behavioral", "technical"],
                "special_settings": ["realtime_hints"]
            }
        }

class InterviewStartResponse(BaseModel):
    """面试开始响应"""
    interview_id: int
    first_question: Optional[Dict[str, Any]] = None
    total_questions: int
    estimated_duration: int
    
    class Config:
        schema_extra = {
            "example": {
                "interview_id": 123,
                "first_question": {
                    "id": 1,
                    "text": "请做一下自我介绍",
                    "type": "behavioral",
                    "time_limit": 180
                },
                "total_questions": 8,
                "estimated_duration": 30
            }
        }

# ===== 面试进行中相关 =====

class AnswerSubmitRequest(BaseModel):
    """回答提交请求"""
    answer_text: Optional[str] = Field(None, description="文字回答")
    audio_file_path: Optional[str] = Field(None, description="音频文件路径")
    video_file_path: Optional[str] = Field(None, description="视频文件路径")
    time_spent: Optional[int] = Field(None, description="回答用时(秒)")
    used_hint: Optional[bool] = Field(False, description="是否使用提示")
    
    class Config:
        schema_extra = {
            "example": {
                "answer_text": "我是一名前端开发工程师...",
                "time_spent": 120,
                "used_hint": False
            }
        }

class AnswerSubmitResponse(BaseModel):
    """回答提交响应 - AI评分反馈"""
    score: float = Field(..., description="单题评分")
    ai_feedback: str = Field(..., description="AI反馈")
    improvement_tips: List[str] = Field(default_factory=list, description="改进建议")
    next_question: Optional[Dict[str, Any]] = Field(None, description="下一题信息")
    
    class Config:
        schema_extra = {
            "example": {
                "score": 85.5,
                "ai_feedback": "回答结构清晰，表达流畅...",
                "improvement_tips": ["可以增加具体案例", "注意时间控制"],
                "next_question": {
                    "id": 2,
                    "text": "介绍一个你负责的项目",
                    "type": "project"
                }
            }
        }

class InterviewCompleteRequest(BaseModel):
    """面试完成请求"""
    interview_id: int
    completion_type: Optional[str] = Field("normal", description="完成类型: normal/emergency/timeout")
    
class InterviewCompleteResponse(BaseModel):
    """面试完成响应"""
    interview_id: int
    overall_score: float
    duration: int
    completion_message: str
    report_available: bool

# ===== 新增：面试控制相关Schema =====

class InterviewControlRequest(BaseModel):
    """面试控制请求"""
    action: str = Field(..., description="控制动作: pause/resume/skip")
    question_id: Optional[int] = Field(None, description="题目ID（跳过时需要）")
    reason: Optional[str] = Field(None, description="操作原因")

class InterviewStatusResponse(BaseModel):
    """面试状态响应"""
    interview_id: int
    status: str  # pending/in_progress/completed/interrupted
    is_paused: bool = False
    is_recording: bool = False
    current_phase: str
    current_question_index: int
    total_questions: int
    elapsed_time: int
    answered_questions: int
    pause_count: int = 0
    last_activity: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "interview_id": 123,
                "status": "in_progress",
                "is_paused": False,
                "is_recording": True,
                "current_phase": "technical",
                "current_question_index": 2,
                "total_questions": 8,
                "elapsed_time": 1200,
                "answered_questions": 3,
                "pause_count": 1
            }
        }

# ===== 新增：AI提示相关Schema =====

class QuestionHintResponse(BaseModel):
    """题目提示响应"""
    question_id: int
    hint: str
    warning: str
    can_use: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": 123,
                "hint": "建议使用STAR法则回答：Situation、Task、Action、Result",
                "warning": "使用提示后该题不计入综合评分",
                "can_use": True
            }
        }

class HintUsageResponse(BaseModel):
    """提示使用响应"""
    question_id: int
    hint_used: bool
    total_hints_used: int
    message: str

# ===== 新增：实时分析相关Schema =====

class RealtimeAnalysisRequest(BaseModel):
    """实时分析数据请求"""
    audio_level: Optional[float] = Field(None, description="音频音量 0-100")
    emotion_type: Optional[str] = Field(None, description="情绪类型")
    eye_contact_score: Optional[float] = Field(None, description="眼神接触评分")
    speech_speed: Optional[float] = Field(None, description="语速")
    facial_expression: Optional[Dict[str, Any]] = Field(None, description="面部表情数据")
    body_posture: Optional[Dict[str, Any]] = Field(None, description="身体姿态数据")
    timestamp: Optional[str] = Field(None, description="时间戳")

class RealtimeStatusResponse(BaseModel):
    """实时状态响应"""
    audio_level: float = 0
    emotion_analysis: Dict[str, str] = {
        "type": "neutral",
        "text": "自然"
    }
    eye_contact_status: Dict[str, str] = {
        "type": "good", 
        "text": "良好"
    }
    voice_analysis: Dict[str, str] = {
        "speed": "normal",
        "speed_text": "适中"
    }
    
    class Config:
        schema_extra = {
            "example": {
                "audio_level": 65,
                "emotion_analysis": {
                    "type": "confident",
                    "text": "自信"
                },
                "eye_contact_status": {
                    "type": "good",
                    "text": "良好"
                },
                "voice_analysis": {
                    "speed": "normal",
                    "speed_text": "适中"
                }
            }
        }

# ===== 新增：文件上传相关Schema =====

class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str
    file_path: str
    file_size: int
    upload_time: str
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "audio_123_456_abc123.mp3",
                "file_path": "uploads/audio/audio_123_456_abc123.mp3",
                "file_size": 1024000,
                "upload_time": "2024-01-20T10:30:00",
                "message": "音频文件上传成功"
            }
        }

# ===== 新增：虚拟面试官相关Schema =====

class InterviewerInfo(BaseModel):
    """面试官信息"""
    id: int
    name: str
    description: str
    avatar: str
    model: str
    specialties: List[str]
    experience: str
    style: str

class InterviewerConfig(BaseModel):
    """面试官配置"""
    id: int
    name: str
    description: str
    avatar: str
    model: str
    specialties: List[str]
    experience: str
    style: str
    voice_settings: Dict[str, float]
    behavior_settings: Dict[str, Any]
    question_style: Dict[str, float]
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "李面试官",
                "description": "亲和力强，善于引导",
                "avatar": "/avatars/interviewer-1.jpg",
                "model": "/models/avatar-1.glb",
                "specialties": ["温和型", "鼓励式", "新人友好"],
                "experience": "5年HR经验",
                "style": "gentle",
                "voice_settings": {
                    "speed": 1.0,
                    "pitch": 1.0,
                    "volume": 0.8
                },
                "behavior_settings": {
                    "question_interval": 3,
                    "patience_level": 5,
                    "follow_up_probability": 0.3
                },
                "question_style": {
                    "formal_level": 0.5,
                    "detail_focus": 0.6,
                    "encouragement": 0.9
                }
            }
        }

# ===== 新增：面试阶段相关Schema =====

class InterviewPhase(BaseModel):
    """面试阶段"""
    id: str
    title: str
    description: str

class InterviewPhasesResponse(BaseModel):
    """面试阶段响应"""
    phases: List[InterviewPhase]
    current_phase: str
    current_phase_index: int
    total_phases: int
    progress_percentage: float
    
    class Config:
        schema_extra = {
            "example": {
                "phases": [
                    {"id": "intro", "title": "开场介绍", "description": "面试官介绍和氛围营造"},
                    {"id": "self", "title": "自我介绍", "description": "候选人自我展示"}
                ],
                "current_phase": "technical",
                "current_phase_index": 2,
                "total_phases": 6,
                "progress_percentage": 50.0
            }
        }

# ===== 新增：紧急功能相关Schema =====

class EmergencyExitRequest(BaseModel):
    """紧急退出请求"""
    exit_reason: Optional[str] = Field(None, description="退出原因")
    save_partial_data: bool = Field(True, description="是否保存部分数据")

class EmergencyExitResponse(BaseModel):
    """紧急退出响应"""
    interview_id: int
    exit_reason: Optional[str]
    duration: Optional[int]
    answered_questions: int
    partial_score: Optional[float]
    report_available: bool
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "interview_id": 123,
                "exit_reason": "网络连接问题",
                "duration": 15,
                "answered_questions": 3,
                "partial_score": 75.5,
                "report_available": True,
                "message": "面试已紧急退出，已保存部分数据"
            }
        }

# ===== 新增：跳过问题相关Schema =====

class SkipQuestionResponse(BaseModel):
    """跳过问题响应"""
    skipped_question_id: int
    next_question: Optional[Dict[str, Any]]
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "skipped_question_id": 456,
                "next_question": {
                    "id": 457,
                    "text": "下一个问题内容",
                    "type": "technical"
                },
                "message": "问题已跳过"
            }
        }

# ===== 面试表现分析相关 =====

class AbilityScores(BaseModel):
    """能力评分"""
    professional: float = Field(0, description="专业知识（硬性专业知识和开放性创新能力）")
    skill_match: float = Field(0, description="技能匹配（工具/技术是否匹配岗位）")
    language_expression: float = Field(0, description="语言表达（语速、音量、情感）")
    logical_thinking: float = Field(0, description="逻辑思维（过渡、语言逻辑）")
    comprehensive_quality: float = Field(0, description="综合素养（表情+动作（仪态+抗压能力））")

class PerformanceResponse(BaseModel):
    """面试表现分析响应 - 匹配前端期望"""
    overall_score: float = Field(0, description="综合评分")
    ability_scores: AbilityScores = Field(default_factory=AbilityScores, description="能力维度评分")
    better_than: float = Field(0, description="超过用户百分比")
    improvement: float = Field(0, description="提升幅度")
    recent_records: List[Dict[str, Any]] = Field(default_factory=list, description="最近面试记录")
    
    class Config:
        schema_extra = {
            "example": {
                "overall_score": 85.5,
                "ability_scores": {
                    "professional": 88,
                    "skill_match": 82,
                    "language_expression": 85,
                    "logical_thinking": 80,
                    "comprehensive_quality": 90
                },
                "better_than": 78.5,
                "improvement": 12.3,
                "recent_records": []
            }
        }

class TrendDataRequest(BaseModel):
    """趋势数据请求"""
    dimension: str = Field("overall", description="维度: overall/professional/skill_match/language_expression/logical_thinking/comprehensive_quality")
    period: str = Field("month", description="时间周期: week/month/quarter")
    aggregation: Optional[str] = Field("individual", description="聚合方式: individual/daily/weekly")

class TrendDataResponse(BaseModel):
    """趋势数据响应"""
    dates: List[str] = Field(default_factory=list, description="日期列表")
    scores: List[float] = Field(default_factory=list, description="评分列表")
    labels: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    details: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="详细信息")

# ===== 历史记录相关 =====

class InterviewHistoryQuery(BaseModel):
    """历史记录查询参数"""
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页大小")
    type: Optional[str] = Field(None, description="面试类型筛选")
    position: Optional[str] = Field(None, description="岗位筛选")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")

class InterviewHistoryItem(BaseModel):
    """历史记录项"""
    id: int
    type: str
    date: str
    company: Optional[str]
    position: str
    round: Optional[str]
    duration: str
    score: float
    rating: float  # 对应前端的 rating 字段
    question_count: int
    interviewer: str
    status: str
    
    # 评分详情
    scores: Optional[Dict[str, float]] = None
    key_feedback: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "type": "simulation",
                "date": "2024-01-20 14:30",
                "company": "字节跳动",
                "position": "前端开发工程师",
                "round": "一面",
                "duration": "45分钟",
                "score": 85.5,
                "rating": 4.3,
                "question_count": 8,
                "interviewer": "AI面试官-张经理",
                "status": "completed"
            }
        }

class InterviewHistoryResponse(BaseModel):
    """历史记录响应"""
    list: List[InterviewHistoryItem]
    total: int
    page: int
    page_size: int
    has_more: bool

# ===== 题目相关 =====

class QuestionResponse(BaseModel):
    """题目响应"""
    id: int
    text: str
    type: str
    difficulty: str
    category: Optional[str] = None
    time_limit: Optional[int] = None
    allow_hints: bool = True
    hint: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "text": "请做一下自我介绍",
                "type": "behavioral",
                "difficulty": "easy",
                "category": "开场",
                "time_limit": 180,
                "allow_hints": True,
                "hint": "建议按照个人信息-教育背景-项目经验的结构来组织回答"
            }
        }

# ===== 基础响应格式 =====

class StandardResponse(BaseModel):
    """标准响应格式 - 匹配前端期望"""
    code: int = Field(200, description="响应代码")
    data: Any = Field(None, description="响应数据")
    message: str = Field("success", description="响应消息")

# ===== 实时状态相关 =====

class InterviewStatus(BaseModel):
    """面试状态"""
    interview_id: int
    status: str  # pending/in_progress/completed/interrupted
    current_question_index: int
    total_questions: int
    elapsed_time: int  # 已用时间(秒)
    current_question: Optional[QuestionResponse] = None

class RealTimeAnalysis(BaseModel):
    """实时分析数据"""
    audio_level: float = Field(0, description="音频音量")
    emotion: str = Field("neutral", description="情绪状态")
    eye_contact: str = Field("good", description="眼神接触")
    speech_speed: str = Field("normal", description="语速")
    
# ===== 数据一致性检查 =====

class DataConsistencyReport(BaseModel):
    """数据一致性报告"""
    total_users: int
    users_with_interviews: int
    users_with_statistics: int
    inconsistent_users: List[int]
    missing_statistics: List[int]
    issues_found: List[str]
    fix_suggestions: List[str]
    
class UserStatisticsFix(BaseModel):
    """用户统计修复结果"""
    processed_users: int
    created_statistics: int
    updated_statistics: int
    fixed_issues: List[str]
    remaining_issues: List[str]

#面试表现

class DetailedAnalysisResponse(BaseModel):
    """详细分析响应"""
    interview_info: Dict[str, Any]
    ability_breakdown: Dict[str, Dict[str, float]]  # 每个能力的详细分解
    question_performance: List[Dict[str, Any]]  # 每题表现
    comparison_data: Dict[str, Any]  # 对比数据
    timeline_analysis: List[Dict[str, Any]]  # 时间线分析

class QARecord(BaseModel):
    """问答记录"""
    timestamp: str
    question: str
    answer: str
    feedback: Optional[str] = None
    score: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None

class PersonalAdvice(BaseModel):
    """个性化建议"""
    type: str  # success/warning/info/error
    title: str
    content: str
    action: Optional[str] = None
    action_text: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    priority: int = 1  # 优先级

class ReplayInfo(BaseModel):
    """回放信息"""
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    transcript_url: Optional[str] = None
    timestamps: List[Dict[str, Any]]  # 关键时间点
    chapters: List[Dict[str, Any]]  # 章节信息
    duration: int  # 总时长

class AbilityInsight(BaseModel):
    """能力洞察"""
    name: str
    current_score: float
    trend: str  # up/down/stable
    trend_value: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    practice_recommendations: List[Dict[str, Any]]
    benchmark_comparison: Dict[str, float]  # 与基准的对比

class TargetedPracticeRequest(BaseModel):
    """针对性练习请求"""
    target_ability: str
    difficulty_level: str
    practice_type: str  # question_bank/simulation/scenario
    duration: Optional[int] = 30
    focus_areas: Optional[List[str]] = None

class PracticePlan(BaseModel):
    """练习计划"""
    plan_id: str
    target_ability: str
    recommended_sessions: List[Dict[str, Any]]
    learning_path: List[Dict[str, Any]]
    expected_improvement: float
    estimated_time: int  # 预计用时(小时)

class HistoryStatistics(BaseModel):
    """历史统计数据"""
    total_count: int = Field(0, description="总面试次数")
    month_count: int = Field(0, description="本月面试次数")
    avg_score: float = Field(0, description="平均分")
    total_duration: int = Field(0, description="总时长(分钟)")
    practice_count: int = Field(0, description="练习模式次数")
    simulation_count: int = Field(0, description="模拟面试次数")

class QARecord(BaseModel):
    """问答记录"""
    timestamp: str = Field(..., description="时间戳")
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="回答")
    feedback: Optional[str] = Field(None, description="AI反馈")
    score: Optional[float] = Field(None, description="单题得分")

class InterviewDetailResponse(BaseModel):
    """面试详情响应"""
    # 基本信息
    id: int
    type: str
    date: str
    company: str
    position: str
    round: str
    duration: str
    interviewer: str
    rating: float
    
    # 详细评分
    scores: Dict[str, float]
    
    # 问答记录
    qa_records: List[QARecord]
    
    # 额外信息
    total_questions: int
    answered_questions: int
    key_feedback: Optional[str] = None

class InterviewHistoryEnhanced(BaseModel):
    """增强的历史记录响应"""
    list: List[InterviewHistoryItem]
    total: int
    page: int
    page_size: int
    has_more: bool
    
    # 新增统计数据
    statistics: HistoryStatistics

class CopySettingsResponse(BaseModel):
    """复制设置响应"""
    type: str
    position: str
    company: Optional[str] = None
    difficulty: Optional[str] = None
    interview_style: Optional[str] = None
    duration: Optional[int] = None
    question_types: Optional[List[str]] = None
    special_settings: Optional[List[str]] = None