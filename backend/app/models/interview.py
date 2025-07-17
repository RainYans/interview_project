# app/models/interview.py - 完整版本，包含所有新增字段
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Interview(Base):
    """面试记录主表"""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 面试基本信息
    type = Column(String(20), nullable=False)  # 'practice' 或 'simulation'
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'interrupted'
    
    # 面试配置信息
    position = Column(String(100), nullable=False)  # 面试岗位
    company = Column(String(100), nullable=True)    # 面试公司（模拟面试时使用）
    difficulty = Column(String(20), nullable=True)  # 'junior', 'medium', 'senior'
    interview_style = Column(String(30), nullable=True)  # 面试风格
    interviewer_id = Column(Integer, nullable=True)  # 虚拟面试官ID
    round_type = Column(String(20), nullable=True)  # 'first', 'second', 'final'
    
    # 时间相关
    scheduled_duration = Column(Integer, nullable=True)  # 计划时长（分钟）
    actual_duration = Column(Integer, nullable=True)    # 实际时长（分钟）
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 评分相关
    overall_score = Column(Float, nullable=True)  # 综合评分 0-100
    professional_score = Column(Float, nullable=True)         # 专业知识（硬性专业知识和开放性创新能力）
    skill_match_score = Column(Float, nullable=True)          # 技能匹配（工具/技术是否匹配岗位）
    language_expression_score = Column(Float, nullable=True)  # 语言表达（语速、音量、情感）
    logical_thinking_score = Column(Float, nullable=True)     # 逻辑思维（过渡、语言逻辑）
    comprehensive_quality_score = Column(Float, nullable=True) # 综合素养（表情+动作（仪态+抗压能力））
    
    # 面试设置（JSON存储）
    settings = Column(JSON, nullable=True)  # 存储面试的详细配置
    
    # 评价和反馈
    ai_feedback = Column(Text, nullable=True)      # AI综合反馈
    key_feedback = Column(Text, nullable=True)     # 关键反馈要点
    improvement_suggestions = Column(Text, nullable=True)  # 改进建议
    
    # 统计数据
    total_questions = Column(Integer, default=0)    # 总题目数
    answered_questions = Column(Integer, default=0) # 已回答题目数
    hints_used = Column(Integer, default=0)         # 使用提示次数
    
    # ===== 新增字段支持前端功能 =====
    
    # 面试状态控制
    is_paused = Column(Boolean, default=False)          # 是否暂停（练习模式）
    pause_count = Column(Integer, default=0)            # 暂停次数
    current_phase = Column(String(30), nullable=True)   # 当前阶段 (intro/self/technical/project/behavioral/questions)
    current_question_id = Column(Integer, nullable=True) # 当前题目ID
    
    # 实时状态
    is_recording = Column(Boolean, default=False)       # 是否录音中
    last_activity = Column(DateTime, nullable=True)     # 最后活动时间
    
    # 文件存储路径
    session_data_path = Column(String(500), nullable=True)  # 会话数据存储路径
    analysis_data_path = Column(String(500), nullable=True) # 分析数据存储路径
    
    # 紧急退出相关
    exit_reason = Column(String(200), nullable=True)    # 退出原因
    is_emergency_exit = Column(Boolean, default=False)  # 是否紧急退出
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    recorded_audio_blob = Column(Text, nullable=True)  # 录音数据
    recording_duration = Column(Integer, nullable=True)  # 录音时长
    transcript_text = Column(Text, nullable=True)  # 语音转文字结果
    
    # 关系
    user = relationship("User")
    questions = relationship("InterviewQuestion", back_populates="interview")
    answers = relationship("InterviewAnswer", back_populates="interview")

    

class InterviewQuestion(Base):
    """面试题目关联表"""
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)  # 关联题库中的题目
    
    # 题目信息
    question_text = Column(Text, nullable=False)    # 题目内容
    question_type = Column(String(30), nullable=True)  # 题目类型
    difficulty = Column(String(20), nullable=True)     # 题目难度
    category = Column(String(50), nullable=True)       # 题目分类
    
    # 题目顺序和状态
    sequence_number = Column(Integer, nullable=False)  # 在面试中的顺序
    status = Column(String(20), default='pending')     # 'pending', 'current', 'answered', 'skipped'
    
    # 时间记录
    asked_at = Column(DateTime(timezone=True), nullable=True)      # 提问时间
    answered_at = Column(DateTime(timezone=True), nullable=True)   # 回答完成时间
    time_limit = Column(Integer, nullable=True)                   # 时间限制（秒）
    time_spent = Column(Integer, nullable=True)                   # 实际用时（秒）
    
    # 题目配置
    allow_hints = Column(Boolean, default=True)        # 是否允许提示
    is_followup = Column(Boolean, default=False)       # 是否为追问题目
    parent_question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    
    # ===== 新增字段 =====
    
    # 提示相关
    hint_text = Column(Text, nullable=True)             # 题目提示内容
    hint_used_count = Column(Integer, default=0)        # 提示使用次数
    
    # 跳过相关
    skip_reason = Column(String(100), nullable=True)    # 跳过原因
    is_skipped = Column(Boolean, default=False)         # 是否被跳过
    
    # 实时分析
    real_time_data = Column(JSON, nullable=True)        # 实时分析数据
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False)
    # 自关联：追问题目的父子关系
    parent_question = relationship("InterviewQuestion", remote_side=[id])


class InterviewAnswer(Base):
    """用户回答记录表"""
    __tablename__ = "interview_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False, unique=True)
    
    # 回答内容
    answer_text = Column(Text, nullable=True)          # 文字回答
    audio_file_path = Column(String(500), nullable=True)  # 音频文件路径
    video_file_path = Column(String(500), nullable=True)  # 视频文件路径
    
    # 回答评分
    score = Column(Float, nullable=True)                      # 单题评分 0-100
    professional_score = Column(Float, nullable=True)         # 专业知识评分
    skill_match_score = Column(Float, nullable=True)          # 技能匹配评分
    language_expression_score = Column(Float, nullable=True)  # 语言表达评分
    logical_thinking_score = Column(Float, nullable=True)     # 逻辑思维评分
    comprehensive_quality_score = Column(Float, nullable=True) # 综合素养评分
    
    # AI分析结果
    ai_feedback = Column(Text, nullable=True)          # AI反馈
    key_points = Column(Text, nullable=True)           # 要点分析
    improvement_tips = Column(Text, nullable=True)     # 改进建议
    
    # 语音分析数据（预留给讯飞AI）
    speech_analysis = Column(JSON, nullable=True)      # 语音分析结果
    emotion_analysis = Column(JSON, nullable=True)     # 情绪分析结果
    
    # 回答状态
    is_complete = Column(Boolean, default=False)       # 是否完整回答
    used_hint = Column(Boolean, default=False)         # 是否使用了提示
    skip_reason = Column(String(100), nullable=True)   # 跳过原因
    
    # 时间记录
    started_at = Column(DateTime(timezone=True), nullable=True)    # 开始回答时间
    submitted_at = Column(DateTime(timezone=True), nullable=True)  # 提交时间
    
    # ===== 新增字段 =====
    
    # 文件信息
    audio_file_size = Column(Integer, nullable=True)    # 音频文件大小
    video_file_size = Column(Integer, nullable=True)    # 视频文件大小
    file_upload_time = Column(DateTime, nullable=True)  # 文件上传时间
    
    # 实时分析结果
    realtime_emotion_data = Column(JSON, nullable=True) # 实时情绪分析
    realtime_voice_data = Column(JSON, nullable=True)   # 实时语音分析
    realtime_behavior_data = Column(JSON, nullable=True) # 实时行为分析
    
    # 提示使用详情
    hint_view_time = Column(DateTime, nullable=True)    # 查看提示时间
    hint_content = Column(Text, nullable=True)          # 使用的提示内容
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    interview = relationship("Interview", back_populates="answers")
    question = relationship("InterviewQuestion", back_populates="answer")


class InterviewStatistics(Base):
    """用户面试统计表"""
    __tablename__ = "interview_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 基础统计
    total_interviews = Column(Integer, default=0)      # 总面试次数
    practice_interviews = Column(Integer, default=0)   # 练习模式次数
    simulation_interviews = Column(Integer, default=0) # 模拟模式次数
    completed_interviews = Column(Integer, default=0)  # 完成的面试次数
    
    # 时长统计
    total_interview_time = Column(Integer, default=0)  # 总面试时长（分钟）
    avg_interview_time = Column(Float, default=0)      # 平均面试时长
    
    # 评分统计
    avg_overall_score = Column(Float, default=0)              # 平均综合评分
    best_overall_score = Column(Float, default=0)             # 最高综合评分
    avg_professional_score = Column(Float, default=0)         # 平均专业知识评分
    avg_skill_match_score = Column(Float, default=0)          # 平均技能匹配评分
    avg_language_expression_score = Column(Float, default=0)  # 平均语言表达评分
    avg_logical_thinking_score = Column(Float, default=0)     # 平均逻辑思维评分
    avg_comprehensive_quality_score = Column(Float, default=0) # 平均综合素养评分
    
    # 排名相关
    current_rank = Column(Integer, nullable=True)      # 当前排名
    rank_percentile = Column(Float, nullable=True)     # 排名百分位
    
    # 学习统计
    total_study_time = Column(Integer, default=0)      # 总学习时长（分钟）
    questions_practiced = Column(Integer, default=0)   # 练习过的题目数
    daily_streak = Column(Integer, default=0)          # 连续学习天数
    
    # 改进统计
    last_month_avg_score = Column(Float, default=0)    # 上月平均分
    current_month_avg_score = Column(Float, default=0) # 本月平均分
    improvement_rate = Column(Float, default=0)        # 提升幅度
    
    # ===== 新增统计字段 =====
    
    # 暂停和提示统计
    total_pauses = Column(Integer, default=0)          # 总暂停次数
    total_hints_used = Column(Integer, default=0)      # 总提示使用次数
    total_questions_skipped = Column(Integer, default=0) # 总跳过题目数
    
    # 紧急退出统计
    emergency_exits = Column(Integer, default=0)       # 紧急退出次数
    incomplete_interviews = Column(Integer, default=0) # 未完成面试次数
    
    # 实时分析统计
    avg_audio_level = Column(Float, default=0)         # 平均音频音量
    avg_speech_speed = Column(Float, default=0)        # 平均语速
    dominant_emotion = Column(String(20), nullable=True) # 主要情绪类型
    
    # 文件上传统计
    total_audio_uploads = Column(Integer, default=0)   # 音频上传次数
    total_video_uploads = Column(Integer, default=0)   # 视频上传次数
    total_upload_size = Column(Integer, default=0)     # 总上传文件大小(KB)
    
    # 时间戳
    last_interview_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")


class InterviewTrendData(Base):
    """面试趋势数据表（用于图表展示）"""
    __tablename__ = "interview_trend_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    
    # 时间维度
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, index=True)  # 'YYYY-MM'
    year_week = Column(String(8), nullable=False, index=True)   # 'YYYY-WW'
    
    # 评分数据
    overall_score = Column(Float, nullable=False)
    professional_score = Column(Float, nullable=True)         # 专业知识
    skill_match_score = Column(Float, nullable=True)          # 技能匹配
    language_expression_score = Column(Float, nullable=True)  # 语言表达
    logical_thinking_score = Column(Float, nullable=True)     # 逻辑思维
    comprehensive_quality_score = Column(Float, nullable=True) # 综合素养
    
    # 面试信息
    position = Column(String(100), nullable=True)
    interview_type = Column(String(20), nullable=False)
    duration = Column(Integer, nullable=True)
    
    # ===== 新增趋势数据字段 =====
    
    # 面试行为数据
    questions_answered = Column(Integer, default=0)    # 回答题目数
    hints_used = Column(Integer, default=0)            # 使用提示数
    questions_skipped = Column(Integer, default=0)     # 跳过题目数
    pauses_count = Column(Integer, default=0)          # 暂停次数
    
    # 实时分析数据
    avg_audio_level = Column(Float, nullable=True)     # 平均音频音量
    dominant_emotion = Column(String(20), nullable=True) # 主要情绪
    eye_contact_quality = Column(String(20), nullable=True) # 眼神接触质量
    speech_fluency = Column(Float, nullable=True)      # 语音流畅度
    
    # 技术数据
    camera_enabled = Column(Boolean, default=False)    # 是否开启摄像头
    audio_uploads = Column(Integer, default=0)         # 音频上传数量
    video_uploads = Column(Integer, default=0)         # 视频上传数量
    
    # 完成状态
    is_emergency_exit = Column(Boolean, default=False) # 是否紧急退出
    completion_rate = Column(Float, default=0)         # 完成率(%)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")
    interview = relationship("Interview")


# ===== 新增：虚拟面试官配置表（可选） =====

class VirtualInterviewer(Base):
    """虚拟面试官配置表"""
    __tablename__ = "virtual_interviewers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(50), nullable=False)          # 面试官名称
    description = Column(Text, nullable=True)          # 描述
    avatar_url = Column(String(255), nullable=True)    # 头像URL
    model_url = Column(String(255), nullable=True)     # 3D模型URL
    
    # 专业信息
    specialties = Column(JSON, nullable=True)          # 专长领域
    experience = Column(String(100), nullable=True)    # 经验描述
    style = Column(String(30), nullable=False)         # 面试风格
    
    # 配置信息
    voice_settings = Column(JSON, nullable=True)       # 语音设置
    behavior_settings = Column(JSON, nullable=True)    # 行为设置
    question_style = Column(JSON, nullable=True)       # 提问风格
    
    # 状态
    is_active = Column(Boolean, default=True)          # 是否激活
    sort_order = Column(Integer, default=0)            # 排序
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ===== 新增：实时分析数据表（可选） =====

class RealtimeAnalysisData(Base):
    """实时分析数据表"""
    __tablename__ = "realtime_analysis_data"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # 音频分析
    audio_level = Column(Float, nullable=True)         # 音频音量
    speech_speed = Column(Float, nullable=True)        # 语速
    speech_pause_duration = Column(Float, nullable=True) # 停顿时长
    
    # 视觉分析
    emotion_type = Column(String(20), nullable=True)   # 情绪类型
    emotion_confidence = Column(Float, nullable=True)  # 情绪置信度
    eye_contact_score = Column(Float, nullable=True)   # 眼神接触评分
    head_pose = Column(JSON, nullable=True)            # 头部姿态
    
    # 行为分析
    gesture_detected = Column(Boolean, default=False)  # 是否检测到手势
    posture_score = Column(Float, nullable=True)       # 姿态评分
    attention_level = Column(Float, nullable=True)     # 注意力水平
    
    # 综合分析
    engagement_score = Column(Float, nullable=True)    # 参与度评分
    confidence_level = Column(Float, nullable=True)    # 自信水平
    stress_indicators = Column(JSON, nullable=True)    # 压力指标
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    interview = relationship("Interview")
    question = relationship("InterviewQuestion")
    user = relationship("User")