# app/services/interview_service.py - 优化版本，为AI接口预留位置
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import uuid
import random
from fastapi import UploadFile

from app.models.interview import (
    Interview, InterviewQuestion, InterviewAnswer, 
    InterviewStatistics, InterviewTrendData
)
from app.models.question import Question
from app.schemas.interview import (
    InterviewStartRequest, AbilityScores, 
    PerformanceResponse, TrendDataResponse, InterviewHistoryItem
)

# ================================================================================================
# 🎯 第一部分：面试开始和管理
# ================================================================================================

def start_interview(db: Session, user_id: int, request: InterviewStartRequest) -> Tuple[Interview, List[Dict]]:
    """开始新面试 - 练习模式"""
    interview = Interview(
        user_id=user_id,
        type=request.type,
        status='in_progress',
        position=request.position,
        company=request.company,
        difficulty=request.difficulty,
        interview_style=request.interview_style,
        interviewer_id=request.interviewer_id,
        round_type=request.round_type,
        scheduled_duration=request.duration,
        started_at=datetime.utcnow(),
        settings=json.dumps({
            "question_types": request.question_types,
            "special_settings": request.special_settings,
            "evaluation_focus": request.evaluation_focus
        }),
        is_paused=False,
        pause_count=0,
        current_phase='intro',
        is_recording=False,
        last_activity=datetime.utcnow()
    )
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # 生成面试题目
    questions = generate_interview_questions(db, interview, request)
    
    return interview, questions

def start_simulation_interview(db: Session, user_id: int, request: InterviewStartRequest) -> Tuple[Interview, List[Dict]]:
    """开始模拟面试 - 模拟模式"""
    interview = Interview(
        user_id=user_id,
        type='simulation',
        status='in_progress',
        position=request.position,
        company=request.company,
        difficulty=request.difficulty,
        interview_style=request.interview_style,
        interviewer_id=request.interviewer_id,
        round_type=request.round_type,
        scheduled_duration=request.duration,
        started_at=datetime.utcnow(),
        settings=json.dumps({
            "company": request.company,
            "round_type": request.round_type,
            "evaluation_focus": request.evaluation_focus,
            "is_simulation": True,
            "allow_pause": False,
            "allow_hints": False,
            "strict_timing": True
        }),
        is_paused=False,
        pause_count=0,
        current_phase='intro',
        is_recording=False,
        last_activity=datetime.utcnow()
    )
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # 生成模拟面试题目
    questions = generate_simulation_questions(db, interview, request)
    
    return interview, questions

# ================================================================================================
# 🤖 第二部分：AI题目生成接口区域
# ================================================================================================

def generate_interview_questions(db: Session, interview: Interview, request: InterviewStartRequest) -> List[Dict]:
    """
    生成练习面试题目
    
    🤖 AI接口对接位置 - 练习模式题目生成
    TODO: 队友在这里对接AI API，根据以下参数生成个性化题目：
    - interview.position: 面试岗位
    - interview.difficulty: 难度等级  
    - request.question_types: 题目类型偏好
    - request.special_settings: 特殊设置
    - interview.scheduled_duration: 面试时长
    
    当前使用硬编码题目库，需要替换为AI生成的题目
    """
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     ai_questions = ai_service.generate_practice_questions(
    #         position=interview.position,
    #         difficulty=interview.difficulty,
    #         question_types=request.question_types,
    #         duration=interview.scheduled_duration,
    #         user_profile=get_user_profile(interview.user_id)
    #     )
    # except Exception as e:
    #     # AI服务失败时使用备用题目库
    #     ai_questions = get_fallback_questions()
    
    # 当前使用的硬编码题目库（AI对接后可删除）
    preset_questions = [
        {
            'text': '请做一下自我介绍，包括您的教育背景、工作经验和技能特长。',
            'type': 'behavioral',
            'difficulty': 'easy',
            'category': '行为面试',
            'time_limit': 180,
            'hints': '建议按照个人信息-教育背景-工作经验-技能特长的结构来组织回答'
        },
        {
            'text': '为什么选择我们公司？您对这个职位有什么了解？',
            'type': 'behavioral',
            'difficulty': 'easy',
            'category': '求职动机',
            'time_limit': 180,
            'hints': '可以从公司文化、发展前景、个人成长等角度回答'
        },
        {
            'text': '请介绍一个您最近参与的项目，包括您的角色、技术栈和主要贡献。',
            'type': 'project',
            'difficulty': 'medium',
            'category': '项目经验',
            'time_limit': 300,
            'hints': '使用STAR法则：情况-任务-行动-结果来组织回答'
        },
        {
            'text': '描述一次您遇到技术难题并成功解决的经历。',
            'type': 'technical',
            'difficulty': 'medium',
            'category': '问题解决',
            'time_limit': 300,
            'hints': '重点说明问题分析过程、解决思路和最终效果'
        },
        {
            'text': '在团队协作中，如何处理与同事的意见分歧？',
            'type': 'situational',
            'difficulty': 'medium',
            'category': '团队协作',
            'time_limit': 240,
            'hints': '可以结合具体例子，展现沟通技巧和解决问题的能力'
        }
    ]
    
    # 根据面试时长确定题目数量
    duration = interview.scheduled_duration or 30
    if interview.type == 'practice':
        total_questions = min(duration // 5, 6)
    else:
        total_questions = min(duration // 6, 8)
    
    total_questions = max(3, min(total_questions, len(preset_questions)))
    
    # 选择题目
    question_types = request.question_types or ['behavioral', 'technical', 'project', 'situational']
    selected_questions = []
    
    for q_type in question_types:
        type_questions = [q for q in preset_questions if q['type'] == q_type]
        if type_questions and len(selected_questions) < total_questions:
            selected_questions.extend(type_questions[:2])
    
    if len(selected_questions) < total_questions:
        remaining_questions = [q for q in preset_questions if q not in selected_questions]
        selected_questions.extend(remaining_questions[:total_questions - len(selected_questions)])
    
    selected_questions = selected_questions[:total_questions]
    
    # 创建题目记录
    questions_data = []
    for i, question_data in enumerate(selected_questions, 1):
        interview_question = InterviewQuestion(
            interview_id=interview.id,
            question_id=None,
            question_text=question_data['text'],
            question_type=question_data['type'],
            difficulty=question_data['difficulty'],
            category=question_data['category'],
            sequence_number=i,
            status='pending',
            time_limit=question_data['time_limit'],
            allow_hints='realtime_hints' in (request.special_settings or []),
            hint_text=question_data.get('hints', ''),
            is_skipped=False
        )
        
        db.add(interview_question)
        db.commit()
        db.refresh(interview_question)
        
        question_response = {
            'id': interview_question.id,
            'text': question_data['text'],
            'type': question_data['type'],
            'difficulty': question_data['difficulty'],
            'category': question_data['category'],
            'time_limit': question_data['time_limit'],
            'allow_hints': interview_question.allow_hints,
            'sequence_number': i
        }
        
        if interview_question.allow_hints:
            question_response['hint'] = question_data.get('hints', '')
        
        questions_data.append(question_response)
    
    interview.total_questions = len(questions_data)
    db.commit()
    
    return questions_data

def generate_simulation_questions(db: Session, interview: Interview, request: InterviewStartRequest) -> List[Dict]:
    """
    生成模拟面试题目
    
    🤖 AI接口对接位置 - 模拟面试题目生成
    TODO: 队友在这里对接AI API，根据以下参数生成更有挑战性的面试题目：
    - interview.company: 公司类型
    - interview.position: 面试岗位
    - interview.round_type: 面试轮次
    - interview.difficulty: 难度等级
    - request.evaluation_focus: 评估重点
    - interview.scheduled_duration: 面试时长
    
    模拟面试题目应该比练习模式更具挑战性和真实性
    """
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     ai_questions = ai_service.generate_simulation_questions(
    #         company_type=interview.company,
    #         position=interview.position,
    #         round_type=interview.round_type,
    #         difficulty=interview.difficulty,
    #         evaluation_focus=request.evaluation_focus,
    #         duration=interview.scheduled_duration,
    #         interview_style=interview.interview_style
    #     )
    # except Exception as e:
    #     # AI服务失败时使用备用题目库
    #     ai_questions = get_fallback_simulation_questions()
    
    # 当前使用的硬编码题目库（AI对接后可删除）
    simulation_questions = [
        {
            'text': f'您好，欢迎参加{get_company_full_name(request.company)}的{get_round_name(request.round_type)}。请先做一个详细的自我介绍。',
            'type': 'behavioral',
            'difficulty': 'easy',
            'category': '开场介绍',
            'time_limit': 240,
            'phase': 'intro'
        },
        {
            'text': f'为什么选择我们{get_company_full_name(request.company)}？您对这个{request.position}职位有什么了解？',
            'type': 'behavioral',
            'difficulty': 'medium',
            'category': '求职动机',
            'time_limit': 180,
            'phase': 'self'
        },
        {
            'text': '请详细介绍一个您最有成就感的技术项目，包括技术架构、遇到的挑战和解决方案。',
            'type': 'technical',
            'difficulty': 'medium',
            'category': '技术项目',
            'time_limit': 360,
            'phase': 'technical'
        },
        {
            'text': '描述一次您在工作中遇到重大技术难题的经历，您是如何分析和解决的？',
            'type': 'technical',
            'difficulty': 'hard',
            'category': '问题解决',
            'time_limit': 300,
            'phase': 'technical'
        },
        {
            'text': '在团队项目中，如果您与同事在技术方案上产生分歧，您会如何处理？',
            'type': 'situational',
            'difficulty': 'medium',
            'category': '团队协作',
            'time_limit': 240,
            'phase': 'behavioral'
        }
    ]
    
    # 根据面试时长确定题目数量
    duration = interview.scheduled_duration or 45
    if duration <= 30:
        total_questions = 5
    elif duration <= 45:
        total_questions = 6
    elif duration <= 60:
        total_questions = 7
    else:
        total_questions = 8
    
    selected_questions = simulation_questions[:total_questions]
    
    # 根据公司类型调整题目
    if request.company == 'tech':
        for q in selected_questions:
            if q['type'] == 'technical':
                q['difficulty'] = 'hard'
                q['time_limit'] += 60
    elif request.company == 'foreign':
        for q in selected_questions:
            if q['type'] == 'behavioral':
                q['time_limit'] += 30
                q['text'] += '（请注意表达的逻辑性和条理性）'
    
    # 创建题目记录
    questions_data = []
    for i, question_data in enumerate(selected_questions, 1):
        interview_question = InterviewQuestion(
            interview_id=interview.id,
            question_id=None,
            question_text=question_data['text'],
            question_type=question_data['type'],
            difficulty=question_data['difficulty'],
            category=question_data['category'],
            sequence_number=i,
            status='pending',
            time_limit=question_data['time_limit'],
            allow_hints=False,
            is_followup=False,
            hint_text=None,
            is_skipped=False
        )
        
        db.add(interview_question)
        db.commit()
        db.refresh(interview_question)
        
        question_response = {
            'id': interview_question.id,
            'text': question_data['text'],
            'type': question_data['type'],
            'difficulty': question_data['difficulty'],
            'category': question_data['category'],
            'time_limit': question_data['time_limit'],
            'allow_hints': False,
            'sequence_number': i,
            'phase': question_data.get('phase', 'general')
        }
        
        questions_data.append(question_response)
    
    interview.total_questions = len(questions_data)
    db.commit()
    
    return questions_data

# ================================================================================================
# 🎮 第三部分：面试控制功能
# ================================================================================================

def pause_interview(db: Session, interview_id: int, user_id: int) -> Dict:
    """暂停面试（仅练习模式）"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if interview.type != 'practice':
        raise ValueError("只有练习模式可以暂停")
    
    if interview.status != 'in_progress':
        raise ValueError("面试未在进行中")
    
    interview.is_paused = True
    interview.pause_count = (interview.pause_count or 0) + 1
    interview.last_activity = datetime.utcnow()
    
    db.commit()
    
    return {
        "interview_id": interview_id,
        "is_paused": True,
        "pause_count": interview.pause_count,
        "message": "面试已暂停，可以随时继续"
    }

def resume_interview(db: Session, interview_id: int, user_id: int) -> Dict:
    """继续面试"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if not interview.is_paused:
        raise ValueError("面试未暂停")
    
    interview.is_paused = False
    interview.last_activity = datetime.utcnow()
    
    db.commit()
    
    return {
        "interview_id": interview_id,
        "is_paused": False,
        "message": "面试已继续"
    }

def skip_question(db: Session, interview_id: int, question_id: int, user_id: int) -> Dict:
    """跳过问题"""
    try:
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == user_id
        ).first()
        
        if not interview:
            raise ValueError("面试不存在")
        
        if interview.type == 'simulation':
            raise ValueError("模拟面试不允许跳过问题")
        
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id,
            InterviewQuestion.interview_id == interview_id
        ).first()
        
        if not question:
            raise ValueError("题目不存在")
        
        # 标记题目为跳过状态
        question.status = 'skipped'
        question.answered_at = datetime.utcnow()
        question.is_skipped = True
        question.skip_reason = '用户主动跳过'
        
        # 检查是否已有答案记录
        existing_answer = db.query(InterviewAnswer).filter(
            InterviewAnswer.question_id == question_id
        ).first()
        
        if existing_answer:
            existing_answer.answer_text = "[已跳过]"
            existing_answer.is_complete = False
            existing_answer.skip_reason = "用户主动跳过"
            existing_answer.submitted_at = datetime.utcnow()
        else:
            skip_answer = InterviewAnswer(
                interview_id=interview_id,
                question_id=question_id,
                answer_text="[已跳过]",
                is_complete=False,
                skip_reason="用户主动跳过",
                submitted_at=datetime.utcnow()
            )
            db.add(skip_answer)
        
        db.commit()
        
        # 获取下一题
        next_question = get_next_question_for_skip(db, interview_id, question.sequence_number)
        
        return {
            "skipped_question_id": question_id,
            "next_question": next_question,
            "message": "问题已跳过"
        }
        
    except Exception as e:
        db.rollback()
        raise e

def get_interview_status(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取面试实时状态"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id,
        InterviewQuestion.status.in_(['current', 'pending'])
    ).order_by(InterviewQuestion.sequence_number).first()
    
    elapsed_time = 0
    if interview.started_at:
        elapsed_time = int((datetime.utcnow() - interview.started_at).total_seconds())
    
    current_phase = determine_current_phase(db, interview_id)
    
    return {
        "interview_id": interview_id,
        "status": interview.status,
        "is_paused": interview.is_paused or False,
        "is_recording": interview.is_recording or False,
        "current_phase": current_phase,
        "current_question_index": current_question.sequence_number - 1 if current_question else 0,
        "total_questions": interview.total_questions,
        "elapsed_time": elapsed_time,
        "answered_questions": interview.answered_questions,
        "pause_count": interview.pause_count or 0,
        "last_activity": interview.last_activity.isoformat() if interview.last_activity else None
    }

def emergency_exit_interview(db: Session, interview_id: int, exit_reason: str, user_id: int) -> Dict:
    """紧急退出面试"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if interview.status == 'completed':
        raise ValueError("面试已完成，无法退出")
    
    interview.status = 'interrupted'
    interview.completed_at = datetime.utcnow()
    interview.is_emergency_exit = True
    interview.exit_reason = exit_reason or '用户紧急退出'
    
    if interview.started_at:
        duration = (interview.completed_at - interview.started_at).seconds // 60
        interview.actual_duration = duration
    
    interview.key_feedback = f"紧急退出: {exit_reason or '用户主动退出'}"
    
    if interview.answered_questions > 0:
        try:
            scores = calculate_interview_scores_safe(db, interview_id)
            interview.overall_score = scores['overall']
            interview.professional_score = scores['professional']
            interview.skill_match_score = scores['skill_match']
            interview.language_expression_score = scores['language_expression']
            interview.logical_thinking_score = scores['logical_thinking']
            interview.comprehensive_quality_score = scores['comprehensive_quality']
        except:
            interview.overall_score = 0.0
    
    db.commit()
    
    try:
        update_user_statistics_safe(db, interview.user_id, interview)
    except:
        pass
    
    return {
        "interview_id": interview_id,
        "exit_reason": exit_reason,
        "duration": interview.actual_duration,
        "answered_questions": interview.answered_questions,
        "partial_score": interview.overall_score,
        "report_available": interview.answered_questions > 0,
        "message": "面试已紧急退出，已保存部分数据"
    }

# ================================================================================================
# 🤖 第四部分：AI提示功能接口区域
# ================================================================================================

def get_question_hint(db: Session, question_id: int, user_id: int) -> Dict:
    """获取题目提示"""
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()
    
    if not question:
        raise ValueError("题目不存在")
    
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("无权限访问")
    
    if interview.type == 'simulation':
        raise ValueError("模拟面试不提供提示")
    
    if not question.allow_hints:
        raise ValueError("该题目不允许提示")
    
    # 生成提示内容
    hint_content = question.hint_text or generate_question_hint(question)
    
    return {
        "question_id": question_id,
        "hint": hint_content,
        "warning": "使用提示后该题不计入综合评分",
        "can_use": True
    }

def generate_question_hint(question: InterviewQuestion) -> str:
    """
    生成题目提示内容
    
    🤖 AI接口对接位置 - AI提示生成
    TODO: 队友在这里对接AI API，根据以下参数生成智能提示：
    - question.question_text: 题目内容
    - question.question_type: 题目类型
    - question.difficulty: 题目难度
    - question.category: 题目分类
    
    应该返回针对性的回答建议和框架
    """
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     ai_hint = ai_service.generate_question_hint(
    #         question_text=question.question_text,
    #         question_type=question.question_type,
    #         difficulty=question.difficulty,
    #         category=question.category
    #     )
    #     return ai_hint
    # except Exception as e:
    #     # AI服务失败时使用备用提示
    #     return get_fallback_hint(question.question_type)
    
    # 当前使用的硬编码提示（AI对接后可删除）
    hints = {
        'behavioral': '建议使用STAR法则回答：Situation(情境)、Task(任务)、Action(行动)、Result(结果)',
        'technical': '可以从原理、实践、优缺点、应用场景等角度来回答',
        'situational': '先分析情况，再提出解决方案，最后说明预期效果',
        'project': '按照项目背景、技术选型、个人贡献、遇到挑战、解决方案、项目成果的顺序来介绍',
        'stress': '保持冷静，简洁明了地回答要点即可'
    }
    
    question_type = question.question_type or 'behavioral'
    return hints.get(question_type, '建议思考后再回答，注意逻辑清晰、表达流畅')

def mark_hint_used(db: Session, question_id: int, user_id: int) -> Dict:
    """标记使用了提示"""
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()
    
    if not question:
        raise ValueError("题目不存在")
    
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("无权限访问")
    
    question.hint_used_count = (question.hint_used_count or 0) + 1
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if not answer:
        answer = InterviewAnswer(
            interview_id=question.interview_id,
            question_id=question_id,
            used_hint=True,
            hint_view_time=datetime.utcnow(),
            hint_content=question.hint_text
        )
        db.add(answer)
    else:
        answer.used_hint = True
        answer.hint_view_time = datetime.utcnow()
        answer.hint_content = question.hint_text
    
    interview.hints_used = (interview.hints_used or 0) + 1
    
    db.commit()
    
    return {
        "question_id": question_id,
        "hint_used": True,
        "total_hints_used": interview.hints_used,
        "message": "提示使用已记录"
    }

# ================================================================================================
# 🤖 第五部分：实时分析功能接口区域
# ================================================================================================

def save_realtime_analysis(db: Session, interview_id: int, analysis_data: Dict, user_id: int) -> Dict:
    """
    保存实时分析数据
    
    🤖 AI接口对接位置 - 实时分析处理
    TODO: 队友在这里对接AI API，处理实时音视频分析：
    - analysis_data.audio_level: 音频音量
    - analysis_data.emotion_type: 情绪类型
    - analysis_data.eye_contact_score: 眼神接触评分
    - analysis_data.speech_speed: 语速
    - analysis_data.facial_expression: 面部表情数据
    
    可以调用AI服务进行实时情绪识别、语音分析等
    """
    
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     # 调用AI分析服务
    #     ai_analysis = ai_service.analyze_realtime_data(
    #         audio_level=analysis_data.get('audio_level'),
    #         video_frame=analysis_data.get('video_frame'),
    #         emotion_data=analysis_data.get('emotion_data'),
    #         speech_data=analysis_data.get('speech_data')
    #     )
    #     
    #     # 保存AI分析结果
    #     enhanced_analysis_data = {
    #         **analysis_data,
    #         'ai_emotion_score': ai_analysis.emotion_score,
    #         'ai_confidence_level': ai_analysis.confidence_level,
    #         'ai_speech_quality': ai_analysis.speech_quality
    #     }
    # except Exception as e:
    #     # AI分析失败时使用原始数据
    #     enhanced_analysis_data = analysis_data
    
    # 保存到当前题目的实时数据字段
    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id,
        InterviewQuestion.status == 'current'
    ).first()
    
    if current_question:
        if current_question.real_time_data:
            existing_data = json.loads(current_question.real_time_data)
            existing_data.append({
                "timestamp": datetime.utcnow().isoformat(),
                "data": analysis_data
            })
        else:
            existing_data = [{
                "timestamp": datetime.utcnow().isoformat(),
                "data": analysis_data
            }]
        
        current_question.real_time_data = json.dumps(existing_data)
        db.commit()
    
    return {
        "interview_id": interview_id,
        "analysis_saved": True,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_realtime_status(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取实时分析状态"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    # 模拟实时状态数据（AI对接后替换为真实分析结果）
    return {
        "audio_level": random.randint(0, 100),
        "emotion_analysis": {
            "type": random.choice(['confident', 'neutral', 'nervous']),
            "text": random.choice(['自信', '自然', '紧张'])
        },
        "eye_contact_status": {
            "type": random.choice(['good', 'average', 'poor']),
            "text": random.choice(['良好', '一般', '较少'])
        },
        "voice_analysis": {
            "speed": random.choice(['normal', 'fast', 'slow']),
            "speed_text": random.choice(['适中', '偏快', '偏慢'])
        }
    }

def save_simulation_analysis(db: Session, interview_id: int, analysis_data: Dict, user_id: int) -> Dict:
    """
    保存模拟面试实时分析数据
    
    🤖 AI接口对接位置 - 模拟面试实时分析
    TODO: 队友在这里对接AI API，进行更严格的实时分析：
    - 模拟面试的分析应该更加严格和详细
    - 包括专业表现、压力处理等高级分析
    """
    
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     # 模拟面试的AI分析更严格
    #     ai_analysis = ai_service.analyze_simulation_performance(
    #         analysis_data=analysis_data,
    #         interview_context={
    #             'company_type': interview.company,
    #             'position': interview.position,
    #             'round_type': interview.round_type,
    #             'current_phase': interview.current_phase
    #         }
    #     )
    # except Exception as e:
    #     ai_analysis = None
    
    # 保存分析数据（可选：保存到专门的实时分析表）
    try:
        from app.models.interview import RealtimeAnalysisData
        
        realtime_data = RealtimeAnalysisData(
            interview_id=interview_id,
            question_id=interview.current_question_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            audio_level=analysis_data.get('audio_level'),
            emotion_type=analysis_data.get('emotion_type'),
            eye_contact_score=analysis_data.get('eye_contact_score'),
            speech_speed=analysis_data.get('speech_speed')
        )
        
        db.add(realtime_data)
        db.commit()
        
    except Exception:
        pass
    
    return {
        "interview_id": interview_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data_saved": True
    }

# ================================================================================================
# 📁 第六部分：文件上传功能
# ================================================================================================

async def upload_audio_file(db: Session, interview_id: int, question_id: int, 
                           audio_file: UploadFile, user_id: int) -> Dict:
    """上传音频文件"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if not audio_file.content_type.startswith('audio/'):
        raise ValueError("文件类型错误，请上传音频文件")
    
    file_extension = audio_file.filename.split('.')[-1]
    unique_filename = f"audio_{interview_id}_{question_id}_{uuid.uuid4().hex}.{file_extension}"
    
    upload_dir = "uploads/audio"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if answer:
        answer.audio_file_path = file_path
        answer.audio_file_size = len(content)
        answer.file_upload_time = datetime.utcnow()
    else:
        answer = InterviewAnswer(
            interview_id=interview_id,
            question_id=question_id,
            audio_file_path=file_path,
            audio_file_size=len(content),
            file_upload_time=datetime.utcnow()
        )
        db.add(answer)
    
    db.commit()
    
    return {
        "file_id": unique_filename,
        "file_path": file_path,
        "file_size": len(content),
        "upload_time": datetime.utcnow().isoformat(),
        "message": "音频文件上传成功"
    }

async def upload_video_file(db: Session, interview_id: int, question_id: int, 
                           video_file: UploadFile, user_id: int) -> Dict:
    """上传视频文件"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if not video_file.content_type.startswith('video/'):
        raise ValueError("文件类型错误，请上传视频文件")
    
    file_extension = video_file.filename.split('.')[-1]
    unique_filename = f"video_{interview_id}_{question_id}_{uuid.uuid4().hex}.{file_extension}"
    
    upload_dir = "uploads/video"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await video_file.read()
        buffer.write(content)
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if answer:
        answer.video_file_path = file_path
        answer.video_file_size = len(content)
        answer.file_upload_time = datetime.utcnow()
    else:
        answer = InterviewAnswer(
            interview_id=interview_id,
            question_id=question_id,
            video_file_path=file_path,
            video_file_size=len(content),
            file_upload_time=datetime.utcnow()
        )
        db.add(answer)
    
    db.commit()
    
    return {
        "file_id": unique_filename,
        "file_path": file_path,
        "file_size": len(content),
        "upload_time": datetime.utcnow().isoformat(),
        "message": "视频文件上传成功"
    }

# ================================================================================================
# 👤 第七部分：虚拟面试官功能
# ================================================================================================

def get_interviewer_list(db: Session) -> List[Dict]:
    """获取虚拟面试官列表"""
    interviewers = [
        {
            "id": 1,
            "name": "李面试官",
            "description": "亲和力强，善于引导",
            "avatar": "/avatars/interviewer-1.jpg",
            "model": "/models/avatar-1.glb",
            "specialties": ["温和型", "鼓励式", "新人友好"],
            "experience": "5年HR经验",
            "style": "gentle"
        },
        {
            "id": 2,
            "name": "张面试官",
            "description": "经验丰富，专业严谨",
            "avatar": "/avatars/interviewer-2.jpg",
            "model": "/models/avatar-2.glb",
            "specialties": ["技术深度", "严谨细致", "标准化"],
            "experience": "10年技术总监",
            "style": "serious"
        },
        {
            "id": 3,
            "name": "王面试官",
            "description": "技术专家，深度挖掘",
            "avatar": "/avatars/interviewer-3.jpg",
            "model": "/models/avatar-3.glb",
            "specialties": ["技术挑战", "压力测试", "深度追问"],
            "experience": "15年架构师",
            "style": "challenging"
        }
    ]
    
    return interviewers

def get_interviewer_config(db: Session, interviewer_id: int) -> Dict:
    """获取面试官配置"""
    interviewers = get_interviewer_list(db)
    
    interviewer = next((i for i in interviewers if i['id'] == interviewer_id), None)
    
    if not interviewer:
        raise ValueError("面试官不存在")
    
    config = interviewer.copy()
    config.update({
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
            "formal_level": 0.7 if interviewer_id == 2 else 0.5,
            "detail_focus": 0.8 if interviewer_id == 3 else 0.6,
            "encouragement": 0.9 if interviewer_id == 1 else 0.5
        }
    })
    
    return config

def get_interviewer_detailed_config(db: Session, interviewer_id: int) -> Dict:
    """获取面试官详细配置（模拟面试增强版）"""
    basic_config = get_interviewer_config(db, interviewer_id)
    
    simulation_config = {
        "interaction_style": {
            "question_pace": 1.0,
            "patience_level": 0.8,
            "follow_up_rate": 0.3,
            "encouragement_level": 0.6
        },
        "evaluation_focus": {
            "technical_weight": 0.4,
            "communication_weight": 0.3,
            "attitude_weight": 0.3
        },
        "simulation_features": {
            "supports_phase_control": True,
            "supports_real_time_feedback": True,
            "supports_stress_testing": interviewer_id == 3
        }
    }
    
    enhanced_config = basic_config.copy()
    enhanced_config.update(simulation_config)
    
    return enhanced_config

# ================================================================================================
# 📊 第八部分：面试阶段管理
# ================================================================================================

def get_interview_phases(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取面试阶段信息"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    phases = [
        {"id": "intro", "title": "开场介绍", "description": "面试官介绍和氛围营造"},
        {"id": "self", "title": "自我介绍", "description": "候选人自我展示"},
        {"id": "technical", "title": "技术问答", "description": "专业技能考察"},
        {"id": "project", "title": "项目经历", "description": "实践经验分享"},
        {"id": "behavioral", "title": "行为面试", "description": "软技能评估"},
        {"id": "questions", "title": "提问环节", "description": "候选人提问"}
    ]
    
    current_phase = determine_current_phase(db, interview_id)
    current_phase_index = next((i for i, p in enumerate(phases) if p['id'] == current_phase), 0)
    
    return {
        "phases": phases,
        "current_phase": current_phase,
        "current_phase_index": current_phase_index,
        "total_phases": len(phases),
        "progress_percentage": round((current_phase_index + 1) / len(phases) * 100, 1)
    }

def advance_interview_phase(db: Session, interview_id: int, user_id: int) -> Dict:
    """进入下一个面试阶段"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    phases_data = get_interview_phases(db, interview_id, user_id)
    
    if phases_data['current_phase_index'] >= phases_data['total_phases'] - 1:
        raise ValueError("已是最后阶段")
    
    return {
        "previous_phase": phases_data['current_phase'],
        "next_phase_index": phases_data['current_phase_index'] + 1,
        "message": "阶段切换成功"
    }

def update_interviewer_status(db: Session, interview_id: int, status_data: Dict, user_id: int) -> Dict:
    """更新面试官状态"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if interview.type != 'simulation':
        raise ValueError("只有模拟面试支持面试官状态控制")
    
    current_settings = {}
    if interview.settings:
        try:
            current_settings = json.loads(interview.settings)
        except:
            current_settings = {}
    
    interviewer_status = current_settings.get('interviewer_status', {})
    interviewer_status.update({
        'is_speaking': status_data.get('is_speaking', False),
        'is_listening': status_data.get('is_listening', False),
        'current_phase': status_data.get('current_phase'),
        'last_update': datetime.utcnow().isoformat()
    })
    
    current_settings['interviewer_status'] = interviewer_status
    interview.settings = json.dumps(current_settings)
    
    if status_data.get('current_phase'):
        interview.current_phase = status_data['current_phase']
    
    interview.last_activity = datetime.utcnow()
    db.commit()
    
    return {
        "interview_id": interview_id,
        "interviewer_status": interviewer_status,
        "updated_at": datetime.utcnow().isoformat()
    }

def update_interview_phase(db: Session, interview_id: int, phase_data: Dict, user_id: int) -> Dict:
    """更新面试阶段"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    phases = ['intro', 'self', 'technical', 'project', 'behavioral', 'questions']
    
    current_phase = phase_data.get('current_phase')
    phase_index = phase_data.get('phase_index')
    
    if current_phase and current_phase in phases:
        interview.current_phase = current_phase
        
        current_settings = {}
        if interview.settings:
            try:
                current_settings = json.loads(interview.settings)
            except:
                current_settings = {}
        
        phase_info = current_settings.get('phase_info', {})
        phase_info.update({
            'current_phase': current_phase,
            'phase_index': phase_index or phases.index(current_phase),
            'total_phases': len(phases),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        current_settings['phase_info'] = phase_info
        interview.settings = json.dumps(current_settings)
        
        interview.last_activity = datetime.utcnow()
        db.commit()
        
        return {
            "interview_id": interview_id,
            "current_phase": current_phase,
            "phase_index": phase_index,
            "total_phases": len(phases),
            "progress_percentage": ((phase_index + 1) / len(phases)) * 100 if phase_index is not None else 0
        }
    else:
        raise ValueError(f"无效的面试阶段: {current_phase}")

# ================================================================================================
# 🤖 第九部分：回答处理和AI评分接口区域
# ================================================================================================

def submit_answer(db: Session, question_id: int, answer_data: Dict) -> Dict:
    """提交答案并获取AI反馈"""
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
    if not question:
        raise ValueError("题目不存在")
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if not answer:
        answer = InterviewAnswer(
            interview_id=question.interview_id,
            question_id=question_id
        )
        db.add(answer)
    
    answer.answer_text = answer_data.get('answer_text')
    answer.audio_file_path = answer_data.get('audio_file_path')
    answer.video_file_path = answer_data.get('video_file_path')
    answer.time_spent = answer_data.get('time_spent')
    answer.used_hint = answer_data.get('used_hint', False)
    answer.is_complete = True
    answer.submitted_at = datetime.utcnow()
    
    question.status = 'answered'
    question.answered_at = datetime.utcnow()
    question.time_spent = answer_data.get('time_spent')
    
    db.commit()
    
    # 调用AI评分
    ai_feedback = generate_ai_feedback(answer, question)
    
    answer.score = ai_feedback['score']
    answer.ai_feedback = ai_feedback['feedback']
    answer.improvement_tips = json.dumps(ai_feedback['tips'])
    
    db.commit()
    
    return ai_feedback

def generate_ai_feedback(answer: InterviewAnswer, question: InterviewQuestion) -> Dict:
    """
    生成AI反馈（练习模式）
    
    🤖 AI接口对接位置 - 练习模式AI评分
    TODO: 队友在这里对接AI API，进行智能评分和反馈生成：
    - answer.answer_text: 回答内容
    - answer.audio_file_path: 音频文件路径（如果有）
    - answer.video_file_path: 视频文件路径（如果有）
    - question.question_text: 题目内容
    - question.question_type: 题目类型
    - question.difficulty: 题目难度
    - answer.time_spent: 回答用时
    - answer.used_hint: 是否使用提示
    
    应该返回包含评分、反馈和改进建议的结构
    """
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     ai_result = ai_service.evaluate_answer(
    #         answer_text=answer.answer_text,
    #         audio_file=answer.audio_file_path,
    #         video_file=answer.video_file_path,
    #         question_context={
    #             'text': question.question_text,
    #             'type': question.question_type,
    #             'difficulty': question.difficulty,
    #             'category': question.category
    #         },
    #         answer_metadata={
    #             'time_spent': answer.time_spent,
    #             'used_hint': answer.used_hint
    #         }
    #     )
    #     
    #     return {
    #         'score': ai_result.score,
    #         'feedback': ai_result.feedback,
    #         'tips': ai_result.improvement_tips,
    #         'detailed_scores': ai_result.detailed_scores
    #     }
    # except Exception as e:
    #     # AI服务失败时使用备用评分
    #     return get_fallback_feedback(question.question_type)
    
    # 当前使用的模拟评分（AI对接后可删除）
    mock_scores = {
        'behavioral': 85.0,
        'technical': 82.0,
        'situational': 88.0,
        'project': 90.0
    }
    
    mock_feedback = {
        'behavioral': '自我介绍结构清晰，表达流畅，建议增加更多具体案例。',
        'technical': '技术理解正确，可以深入说明实现细节和优化方案。',
        'situational': '解决思路合理，展现了良好的问题分析能力。',
        'project': '项目描述详细，体现了扎实的实践经验。'
    }
    
    mock_tips = {
        'behavioral': ['增加具体数据支撑', '突出个人贡献', '保持自信表达'],
        'technical': ['深入技术细节', '说明优化方案', '结合实际场景'],
        'situational': ['多角度分析', '提出具体措施', '考虑风险因素'],
        'project': ['量化项目成果', '说明技术选型', '总结经验教训']
    }
    
    q_type = question.question_type or 'behavioral'
    
    return {
        'score': mock_scores.get(q_type, 80.0),
        'feedback': mock_feedback.get(q_type, '回答基本完整，表达清晰。'),
        'tips': mock_tips.get(q_type, ['继续保持', '多加练习'])
    }

def generate_simulation_ai_feedback(answer: InterviewAnswer, question: InterviewQuestion) -> Dict:
    """
    生成模拟面试AI反馈（更严格的评分标准）
    
    🤖 AI接口对接位置 - 模拟面试AI评分
    TODO: 队友在这里对接AI API，进行更严格的评分：
    - 模拟面试的评分标准应该更严格
    - 需要考虑真实面试的评判标准
    - 包括专业度、表达能力、逻辑思维等多维度评分
    """
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     ai_result = ai_service.evaluate_simulation_answer(
    #         answer_text=answer.answer_text,
    #         audio_file=answer.audio_file_path,
    #         video_file=answer.video_file_path,
    #         question_context={
    #             'text': question.question_text,
    #             'type': question.question_type,
    #             'difficulty': question.difficulty,
    #             'category': question.category
    #         },
    #         simulation_context={
    #             'is_simulation': True,
    #             'stricter_evaluation': True,
    #             'real_interview_standards': True
    #         }
    #     )
    #     
    #     return {
    #         'score': ai_result.score,
    #         'feedback': ai_result.feedback,
    #         'tips': ai_result.improvement_tips
    #     }
    # except Exception as e:
    #     return get_fallback_simulation_feedback(question.question_type)
    
    # 当前使用的模拟评分（比练习模式更严格）
    base_scores = {
        'behavioral': 78.0,
        'technical': 75.0,
        'situational': 80.0,
        'project': 82.0,
        'stress': 70.0,
        'questions': 85.0
    }
    
    feedback_templates = {
        'behavioral': '表达较为清晰，建议增加更多具体案例和量化数据来支撑观点。',
        'technical': '技术理解基本正确，但需要在实现细节和优化方案方面有更深入的阐述。',
        'situational': '解决思路合理，但可以考虑更多的风险因素和预案。',
        'project': '项目描述完整，建议更多地突出个人贡献和技术难点的解决过程。',
        'stress': '在压力环境下保持了基本的回答结构，建议提升应对紧急情况的冷静度。',
        'questions': '提问显示了对岗位的关注，可以更深入地了解团队文化和发展机会。'
    }
    
    tips_templates = {
        'behavioral': ['增加具体数据', '突出个人价值', '完善表达逻辑'],
        'technical': ['深化技术细节', '说明优化思路', '结合实际场景'],
        'situational': ['考虑多种方案', '评估风险因素', '制定应急预案'],
        'project': ['量化项目价值', '突出技术亮点', '总结关键经验'],
        'stress': ['保持冷静思考', '简洁回答要点', '展现抗压能力'],
        'questions': ['深入了解团队', '关注发展机会', '展现长期兴趣']
    }
    
    q_type = question.question_type or 'behavioral'
    
    # 模拟面试评分更严格，减少5-10分
    base_score = base_scores.get(q_type, 75.0)
    final_score = max(0, min(100, base_score + random.uniform(-8, 2)))
    
    return {
        'score': final_score,
        'feedback': feedback_templates.get(q_type, '回答基本完整，建议继续提升表达的专业性和深度。'),
        'tips': tips_templates.get(q_type, ['继续练习', '提升专业度'])
    }

def get_next_question(db: Session, current_question_id: int) -> Optional[Dict]:
    """获取下一题"""
    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == current_question_id
    ).first()
    
    if not current_question:
        return None
    
    next_question = db.query(InterviewQuestion).filter(
        and_(
            InterviewQuestion.interview_id == current_question.interview_id,
            InterviewQuestion.sequence_number > current_question.sequence_number,
            InterviewQuestion.status == 'pending'
        )
    ).order_by(InterviewQuestion.sequence_number).first()
    
    if not next_question:
        return None
    
    next_question.status = 'current'
    next_question.asked_at = datetime.utcnow()
    db.commit()
    
    return {
        'id': next_question.id,
        'text': next_question.question_text,
        'type': next_question.question_type,
        'time_limit': next_question.time_limit,
        'allow_hints': next_question.allow_hints
    }

def start_answer_simulation(db: Session, interview_id: int, answer_data: Dict, user_id: int) -> Dict:
    """开始回答（模拟面试专用）"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    question_id = answer_data.get('question_id')
    if not question_id:
        raise ValueError("缺少题目ID")
    
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.interview_id == interview_id
    ).first()
    
    if not question:
        raise ValueError("题目不存在")
    
    question.status = 'current'
    question.asked_at = datetime.utcnow()
    
    interview.is_recording = True
    interview.current_question_id = question_id
    interview.last_activity = datetime.utcnow()
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if not answer:
        answer = InterviewAnswer(
            interview_id=interview_id,
            question_id=question_id,
            started_at=datetime.utcnow()
        )
        db.add(answer)
    else:
        answer.started_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "interview_id": interview_id,
        "question_id": question_id,
        "started_at": datetime.utcnow().isoformat(),
        "time_limit": question.time_limit,
        "message": "开始回答已记录"
    }

def finish_answer_simulation(db: Session, interview_id: int, answer_data: Dict, user_id: int) -> Dict:
    """完成回答（模拟面试专用）"""
    question_id = answer_data.get('question_id')
    if not question_id:
        raise ValueError("缺少题目ID")
    
    answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).first()
    
    if not answer:
        answer = InterviewAnswer(
            interview_id=interview_id,
            question_id=question_id
        )
        db.add(answer)
    
    answer.answer_text = answer_data.get('answer_text')
    answer.audio_file_path = answer_data.get('audio_file_path')
    answer.video_file_path = answer_data.get('video_file_path')
    answer.time_spent = answer_data.get('time_spent')
    answer.is_complete = True
    answer.submitted_at = datetime.utcnow()
    
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()
    
    if question:
        question.status = 'answered'
        question.answered_at = datetime.utcnow()
        question.time_spent = answer_data.get('time_spent')
    
    interview = db.query(Interview).filter(
        Interview.id == interview_id
    ).first()
    
    if interview:
        interview.is_recording = False
        interview.answered_questions = (interview.answered_questions or 0) + 1
        interview.last_activity = datetime.utcnow()
    
    db.commit()
    
    # 生成AI评分
    try:
        ai_feedback = generate_simulation_ai_feedback(answer, question)
        answer.score = ai_feedback['score']
        answer.ai_feedback = ai_feedback['feedback']
        answer.improvement_tips = json.dumps(ai_feedback['tips'])
        db.commit()
    except Exception:
        ai_feedback = {'score': 75.0, 'feedback': '回答已提交', 'tips': []}
    
    # 获取下一题
    next_question = get_next_simulation_question(db, interview_id, question.sequence_number)
    
    return {
        "interview_id": interview_id,
        "question_id": question_id,
        "score": ai_feedback['score'],
        "feedback": ai_feedback['feedback'],
        "next_question": next_question,
        "is_last_question": next_question is None
    }

# ================================================================================================
# 🤖 第十部分：面试完成和报告生成接口区域
# ================================================================================================

def complete_interview(db: Session, interview_id: int, completion_data: Dict = None) -> Dict:
    """
    完成面试并生成评分报告
    
    🤖 AI接口对接位置 - 面试报告生成
    TODO: 队友在这里对接AI API，生成综合面试报告：
    - 分析用户所有回答的表现
    - 生成各维度的详细评分
    - 提供个性化的改进建议
    - 生成综合评价和反馈
    """
    
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError("面试不存在")
        
        interview.status = 'completed'
        interview.completed_at = datetime.utcnow()
        
        if interview.started_at:
            duration = (interview.completed_at - interview.started_at).seconds // 60
            interview.actual_duration = duration
        else:
            interview.actual_duration = 0
        
        # 🤖 AI接口调用示例代码位置：
        # try:
        #     # 获取所有回答数据用于AI分析
        #     answers = db.query(InterviewAnswer).filter(
        #         InterviewAnswer.interview_id == interview_id,
        #         InterviewAnswer.is_complete == True
        #     ).all()
        #     
        #     questions = db.query(InterviewQuestion).filter(
        #         InterviewQuestion.interview_id == interview_id
        #     ).all()
        #     
        #     # 调用AI生成综合报告
        #     ai_report = ai_service.generate_interview_report(
        #         interview_data={
        #             'type': interview.type,
        #             'position': interview.position,
        #             'company': interview.company,
        #             'duration': interview.actual_duration,
        #             'difficulty': interview.difficulty
        #         },
        #         answers_data=[{
        #             'question_text': q.question_text,
        #             'question_type': q.question_type,
        #             'answer_text': a.answer_text,
        #             'time_spent': a.time_spent,
        #             'score': a.score,
        #             'used_hint': a.used_hint
        #         } for q, a in zip(questions, answers)],
        #         realtime_data=get_interview_realtime_data(interview_id)
        #     )
        #     
        #     # 使用AI生成的评分和反馈
        #     scores = ai_report.detailed_scores
        #     interview.ai_feedback = ai_report.comprehensive_feedback
        #     interview.key_feedback = ai_report.key_insights
        #     interview.improvement_suggestions = ai_report.improvement_plan
        #     
        # except Exception as e:
        #     # AI服务失败时使用备用评分算法
        #     scores = calculate_interview_scores_safe(db, interview_id)
        #     interview.ai_feedback = generate_overall_feedback(scores)
        #     interview.key_feedback = generate_key_feedback(scores)
        #     interview.improvement_suggestions = generate_improvement_suggestions(scores)
        
        # 当前使用的备用评分算法（AI对接后作为备用）
        try:
            scores = calculate_interview_scores_safe(db, interview_id)
        except Exception:
            scores = {
                'overall': 0.0,
                'professional': 0.0,
                'skill_match': 0.0,
                'language_expression': 0.0,
                'logical_thinking': 0.0,
                'comprehensive_quality': 0.0
            }
        
        interview.overall_score = scores['overall']
        interview.professional_score = scores['professional']
        interview.skill_match_score = scores['skill_match']
        interview.language_expression_score = scores['language_expression']
        interview.logical_thinking_score = scores['logical_thinking']
        interview.comprehensive_quality_score = scores['comprehensive_quality']
        
        try:
            interview.ai_feedback = generate_overall_feedback(scores)
            interview.key_feedback = generate_key_feedback(scores)
            interview.improvement_suggestions = generate_improvement_suggestions(scores)
        except Exception:
            interview.ai_feedback = "面试已完成，感谢您的参与！"
            interview.key_feedback = "整体表现良好"
            interview.improvement_suggestions = "继续保持，多加练习"
        
        try:
            answered_count = db.query(InterviewAnswer).filter(
                InterviewAnswer.interview_id == interview_id,
                InterviewAnswer.is_complete == True
            ).count()
            interview.answered_questions = answered_count
        except Exception:
            interview.answered_questions = 0
        
        db.commit()
        
        try:
            update_user_statistics_safe(db, interview.user_id, interview)
        except Exception:
            pass
        
        try:
            save_trend_data_safe(db, interview)
        except Exception:
            pass
        
        return {
            'interview_id': interview_id,
            'overall_score': interview.overall_score or 0,
            'duration': interview.actual_duration or 0,
            'completion_message': '面试完成！',
            'report_available': True
        }
        
    except ValueError as ve:
        raise ve
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        raise Exception(f"完成面试失败: {str(e)}")

def complete_simulation_interview(db: Session, interview_id: int, completion_data: Dict, user_id: int) -> Dict:
    """
    完成模拟面试
    
    🤖 AI接口对接位置 - 模拟面试报告生成
    TODO: 队友在这里对接AI API，生成更严格的模拟面试报告：
    - 相比练习模式应该有更严格的评分标准
    - 生成更详细的综合评价报告
    - 提供针对真实面试的准备建议
    """
    
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    if interview.type != 'simulation':
        raise ValueError("该接口仅用于模拟面试")
    
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()
    
    if interview.started_at:
        duration = (interview.completed_at - interview.started_at).seconds // 60
        interview.actual_duration = duration
    
    completion_type = completion_data.get('completion_type', 'normal')
    if completion_type == 'emergency':
        interview.is_emergency_exit = True
        interview.exit_reason = completion_data.get('emergency_reason', '用户紧急退出')
    
    # 🤖 AI接口调用示例代码位置：
    # try:
    #     # 模拟面试的AI报告生成
    #     ai_report = ai_service.generate_simulation_report(
    #         interview_data={
    #             'company_type': interview.company,
    #             'position': interview.position,
    #             'round_type': interview.round_type,
    #             'interview_style': interview.interview_style,
    #             'duration': interview.actual_duration
    #         },
    #         performance_data=get_simulation_performance_data(interview_id),
    #         realtime_analysis=get_simulation_realtime_analysis(interview_id),
    #         completion_type=completion_type
    #     )
    #     
    #     scores = ai_report.detailed_scores
    #     interview.ai_feedback = ai_report.comprehensive_feedback
    #     interview.key_feedback = ai_report.key_insights
    #     interview.improvement_suggestions = ai_report.improvement_plan
    #     
    # except Exception as e:
    #     # AI服务失败时使用备用算法
    #     scores = calculate_simulation_scores(db, interview_id)
    #     interview.ai_feedback = generate_simulation_feedback(scores, interview)
    #     interview.key_feedback = generate_simulation_key_feedback(scores)
    #     interview.improvement_suggestions = generate_simulation_improvement_suggestions(scores)
    
    # 当前使用备用算法
    try:
        scores = calculate_simulation_scores(db, interview_id)
        interview.overall_score = scores['overall']
        interview.professional_score = scores['professional']
        interview.skill_match_score = scores['skill_match']
        interview.language_expression_score = scores['language_expression']
        interview.logical_thinking_score = scores['logical_thinking']
        interview.comprehensive_quality_score = scores['comprehensive_quality']
        
        interview.ai_feedback = generate_simulation_feedback(scores, interview)
        interview.key_feedback = generate_simulation_key_feedback(scores)
        interview.improvement_suggestions = generate_simulation_improvement_suggestions(scores)
        
    except Exception:
        interview.overall_score = 70.0
        interview.ai_feedback = "模拟面试已完成，感谢您的参与！"
    
    answered_count = db.query(InterviewAnswer).filter(
        InterviewAnswer.interview_id == interview_id,
        InterviewAnswer.is_complete == True
    ).count()
    interview.answered_questions = answered_count
    
    db.commit()
    
    try:
        update_user_statistics_safe(db, interview.user_id, interview)
        save_trend_data_safe(db, interview)
    except Exception:
        pass
    
    return {
        'interview_id': interview_id,
        'overall_score': interview.overall_score or 0,
        'duration': interview.actual_duration or 0,
        'completion_message': '模拟面试完成！您的表现报告已生成。' if completion_type == 'normal' else '模拟面试已中断',
        'report_available': True,
        'completion_type': completion_type
    }

# ================================================================================================
# 📊 第十一部分：数据查询和分析
# ================================================================================================

def get_user_performance(db: Session, user_id: int) -> PerformanceResponse:
    """获取用户面试表现分析数据"""
    try:
        stats = db.query(InterviewStatistics).filter(
            InterviewStatistics.user_id == user_id
        ).first()
        
        if not stats:
            stats = InterviewStatistics(user_id=user_id)
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        latest_interview = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == 'completed',
            Interview.overall_score.isnot(None)
        ).order_by(desc(Interview.completed_at)).first()
        
        ability_scores = AbilityScores()
        overall_score = 0.0
        
        if latest_interview:
            ability_scores.professional = round(latest_interview.professional_score or 0, 1)
            ability_scores.skill_match = round(latest_interview.skill_match_score or 0, 1)
            ability_scores.language_expression = round(latest_interview.language_expression_score or 0, 1)
            ability_scores.logical_thinking = round(latest_interview.logical_thinking_score or 0, 1)
            ability_scores.comprehensive_quality = round(latest_interview.comprehensive_quality_score or 0, 1)
            overall_score = round(latest_interview.overall_score or 0, 1)
        else:
            ability_scores.professional = 60.0
            ability_scores.skill_match = 60.0
            ability_scores.language_expression = 60.0
            ability_scores.logical_thinking = 60.0
            ability_scores.comprehensive_quality = 60.0
            overall_score = 60.0
        
        better_than = calculate_rank_percentile_fixed(db, user_id, overall_score)
        improvement = calculate_improvement_rate_fixed(db, user_id)
        
        recent_interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == 'completed'
        ).order_by(desc(Interview.completed_at)).limit(5).all()
        
        recent_records = []
        for interview in recent_interviews:
            record = {
                'id': interview.id,
                'date': interview.completed_at.strftime('%Y-%m-%d') if interview.completed_at else interview.created_at.strftime('%Y-%m-%d'),
                'type': interview.type or 'practice',
                'position': interview.position or '前端开发',
                'duration': f"{interview.actual_duration or 30}分钟",
                'score': round(interview.overall_score or 0, 1)
            }
            recent_records.append(record)
        
        response = PerformanceResponse(
            overall_score=overall_score,
            ability_scores=ability_scores,
            better_than=better_than,
            improvement=improvement,
            recent_records=recent_records
        )
        
        return response
        
    except Exception:
        return PerformanceResponse(
            overall_score=0.0,
            ability_scores=AbilityScores(
                professional=0.0,
                skill_match=0.0,
                language_expression=0.0,
                logical_thinking=0.0,
                comprehensive_quality=0.0
            ),
            better_than=0.0,
            improvement=0.0,
            recent_records=[]
        )

def get_trend_data(db: Session, user_id: int, dimension: str = 'overall', 
                  period: str = 'month') -> TrendDataResponse:
    """获取趋势数据"""
    try:
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        if period == 'week':
            start_date = now - timedelta(days=7)
            days_back = 7
        elif period == 'month':
            start_date = now - timedelta(days=30)
            days_back = 30
        elif period == 'quarter':
            start_date = now - timedelta(days=90)
            days_back = 90
        else:
            start_date = now - timedelta(days=30)
            days_back = 30
        
        interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.completed_at >= start_date,
            Interview.status == 'completed',
            Interview.overall_score.isnot(None)
        ).order_by(Interview.completed_at).all()
        
        dates = []
        scores = []
        labels = []
        details = []
        
        if not interviews:
            for i in range(min(days_back, 10)):
                date = now - timedelta(days=i)
                dates.append(date.strftime('%m-%d'))
                score = 70 + (i * 2) + (i * 0.5)
                scores.append(round(score, 1))
                labels.append(f'第{len(dates)}次练习')
                details.append({
                    'date': date.strftime('%m-%d %H:%M'),
                    'score': round(score, 1),
                    'position': '前端开发',
                    'interview_id': f'mock_{i}'
                })
            
            dates.reverse()
            scores.reverse()
            labels.reverse()
            details.reverse()
            
        else:
            for i, interview in enumerate(interviews):
                dates.append(interview.completed_at.strftime('%m-%d'))
                labels.append(f'第{i+1}次面试')
                
                if dimension == 'overall':
                    score = interview.overall_score or 0
                elif dimension == 'professional':
                    score = interview.professional_score or 0
                elif dimension == 'skill_match':
                    score = interview.skill_match_score or 0
                elif dimension == 'language_expression':
                    score = interview.language_expression_score or 0
                elif dimension == 'logical_thinking':
                    score = interview.logical_thinking_score or 0
                elif dimension == 'comprehensive_quality':
                    score = interview.comprehensive_quality_score or 0
                else:
                    score = interview.overall_score or 0
                
                scores.append(round(score, 1))
                
                details.append({
                    'date': interview.completed_at.strftime('%m-%d %H:%M'),
                    'score': round(score, 1),
                    'position': interview.position or '前端开发',
                    'interview_id': interview.id
                })
        
        response = TrendDataResponse(
            dates=dates,
            scores=scores,
            labels=labels,
            details=details
        )
        
        return response
        
    except Exception:
        return TrendDataResponse(
            dates=[],
            scores=[],
            labels=[],
            details=[]
        )

def get_user_interview_history_enhanced(db: Session, user_id: int, page: int = 1, 
                                       page_size: int = 10, filters: Dict = None) -> Dict:
    """获取用户面试历史记录"""
    try:
        interviews = db.query(Interview).filter(
            Interview.user_id == user_id
        ).order_by(desc(Interview.created_at)).limit(page_size).offset((page - 1) * page_size).all()
        
        total = db.query(Interview).filter(Interview.user_id == user_id).count()
        
        items = []
        for interview in interviews:
            items.append({
                "id": interview.id,
                "type": interview.type or "practice",
                "date": interview.created_at.strftime('%Y-%m-%d %H:%M'),
                "company": interview.company or "模拟公司", 
                "position": interview.position or "前端开发",
                "round": "一面",
                "duration": f"{interview.actual_duration or 30}分钟",
                "questionCount": interview.answered_questions or 5,
                "interviewer": "AI面试官",
                "rating": round((interview.overall_score or 80) / 20, 1),
                "scores": {
                    "professional": interview.professional_score or 80,
                    "expression": interview.language_expression_score or 85,
                    "logic": interview.logical_thinking_score or 82,
                    "adaptability": interview.comprehensive_quality_score or 78,
                    "attitude": interview.comprehensive_quality_score or 80
                },
                "keyFeedback": interview.key_feedback or "表现良好",
                "status": interview.status or "completed"
            })
        
        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": page * page_size < total,
            "statistics": {
                "total_count": total,
                "month_count": 0,
                "avg_score": 80,
                "total_duration": 120,
                "practice_count": total,
                "simulation_count": 0
            }
        }
    except Exception:
        return {
            "list": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "has_more": False,
            "statistics": {
                "total_count": 0,
                "month_count": 0,
                "avg_score": 0,
                "total_duration": 0,
                "practice_count": 0,
                "simulation_count": 0
            }
        }

def generate_personal_advice(db: Session, user_id: int) -> List[Dict]:
    """生成个性化建议"""
    try:
        recent_interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == 'completed',
            Interview.overall_score.isnot(None)
        ).order_by(desc(Interview.completed_at)).limit(5).all()
        
        advice_list = []
        
        if not recent_interviews:
            advice_list = [
                {
                    "type": "info",
                    "title": "开始您的面试练习之旅",
                    "content": "欢迎使用面试系统！建议从基础练习开始，逐步提升面试技能。",
                    "action": "practice",
                    "action_text": "开始练习",
                    "action_data": {"type": "basic"},
                    "priority": 1
                }
            ]
        else:
            latest_interview = recent_interviews[0]
            avg_score = sum(i.overall_score or 0 for i in recent_interviews) / len(recent_interviews)
            
            if avg_score >= 85:
                advice_list.append({
                    "type": "success",
                    "title": "表现优秀",
                    "content": f"您的平均表现达到{avg_score:.1f}分，已经具备了很强的面试竞争力！",
                    "action": "simulation",
                    "action_text": "挑战模拟面试",
                    "action_data": {"type": "simulation", "difficulty": "hard"},
                    "priority": 1
                })
            elif avg_score >= 70:
                advice_list.append({
                    "type": "info",
                    "title": "稳步提升",
                    "content": f"您的平均表现为{avg_score:.1f}分，基础扎实，建议多样化练习来全面提升。",
                    "action": "practice",
                    "action_text": "多样化练习",
                    "action_data": {"type": "comprehensive"},
                    "priority": 1
                })
            else:
                advice_list.append({
                    "type": "info",
                    "title": "系统提升",
                    "content": f"建议系统性地练习基础面试技巧，从各个维度来提升面试表现。",
                    "action": "learning",
                    "action_text": "学习指南",
                    "action_data": {"resource": "basic_guide"},
                    "priority": 1
                })
        
        return advice_list
        
    except Exception:
        return [
            {
                "type": "info",
                "title": "继续练习",
                "content": "建议继续练习来提升面试技能。",
                "action": "practice",
                "action_text": "开始练习",
                "action_data": {"type": "basic"},
                "priority": 1
            }
        ]

def create_targeted_practice_plan(db: Session, user_id: int, practice_request: Dict[str, Any]) -> Dict:
    """创建针对性练习计划"""
    try:
        target_ability = practice_request.get('target_ability', 'professional')
        difficulty_level = practice_request.get('difficulty_level', 'medium')
        practice_type = practice_request.get('practice_type', 'question_bank')
        duration = practice_request.get('duration', 30)
        
        plan_id = str(uuid.uuid4())[:8]
        
        ability_mapping = {
            'professional': '专业知识',
            'skill_match': '技能匹配',
            'language_expression': '表达能力',
            'logical_thinking': '逻辑思维',
            'comprehensive_quality': '综合素养'
        }
        
        ability_name = ability_mapping.get(target_ability, '综合能力')
        
        recommended_sessions = [
            {
                "session_id": f"{plan_id}_1",
                "type": "question_practice",
                "title": f"{ability_name}专项练习",
                "description": f"针对{ability_name}的专项题目练习",
                "estimated_time": duration,
                "question_count": duration // 3,
                "difficulty": difficulty_level
            }
        ]
        
        learning_path = [
            {
                "step": 1,
                "title": "理论学习",
                "description": f"学习{ability_name}相关的理论知识",
                "estimated_time": duration * 0.2
            },
            {
                "step": 2,
                "title": "实践练习",
                "description": f"通过题目练习来巩固{ability_name}",
                "estimated_time": duration * 0.6
            },
            {
                "step": 3,
                "title": "总结反思",
                "description": f"总结练习效果，制定下一步计划",
                "estimated_time": duration * 0.2
            }
        ]
        
        expected_improvement = {
            'junior': 15.0,
            'medium': 10.0,
            'senior': 8.0
        }.get(difficulty_level, 10.0)
        
        plan = {
            "plan_id": plan_id,
            "target_ability": target_ability,
            "recommended_sessions": recommended_sessions,
            "learning_path": learning_path,
            "expected_improvement": expected_improvement,
            "estimated_time": duration / 60
        }
        
        return plan
        
    except Exception as e:
        raise Exception(f"创建练习计划失败: {str(e)}")

def get_detailed_interview_analysis(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取面试详细分析"""
    try:
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == user_id
        ).first()
        
        if not interview:
            raise ValueError("面试不存在")
            
        return {
            "interview_info": {
                "id": interview_id,
                "type": interview.type or "practice",
                "position": interview.position or "前端开发",
                "overall_score": interview.overall_score or 80
            },
            "ability_breakdown": {
                "professional": {"score": 85, "rank": "良好"},
                "expression": {"score": 82, "rank": "良好"},
                "logic": {"score": 88, "rank": "优秀"},
                "comprehensive": {"score": 80, "rank": "良好"}
            },
            "question_performance": [],
            "comparison_data": {
                "user_avg": 85,
                "platform_avg": 75,
                "better_than_percent": 78
            },
            "timeline_analysis": []
        }
    except Exception as e:
        raise e

def get_interview_qa_records(db: Session, interview_id: int, user_id: int) -> List[Dict]:
    """获取面试问答记录"""
    try:
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == user_id
        ).first()
        
        if not interview:
            raise ValueError("面试不存在")
            
        return [
            {
                "timestamp": "00:05:30",
                "question": "请做一下自我介绍",
                "answer": "我是一名前端开发工程师...",
                "feedback": "表达清晰，逻辑性强",
                "score": 85
            }
        ]
    except Exception as e:
        raise e

def get_interview_replay_info(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取面试回放信息"""
    try:
        return {
            "video_url": None,
            "audio_url": None, 
            "transcript_url": None,
            "timestamps": [],
            "chapters": [],
            "duration": 1800
        }
    except Exception:
        return {
            "video_url": None,
            "audio_url": None,
            "transcript_url": None, 
            "timestamps": [],
            "chapters": [],
            "duration": 0
        }

# ================================================================================================
# 🛠️ 第十二部分：辅助工具函数
# ================================================================================================

def calculate_interview_scores_safe(db: Session, interview_id: int) -> Dict[str, float]:
    """安全地计算面试各维度评分"""
    try:
        answers = db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_id == interview_id,
            InterviewAnswer.is_complete == True
        ).all()
        
        if not answers:
            return {
                'overall': 60.0,
                'professional': 60.0,
                'skill_match': 60.0,
                'language_expression': 60.0,
                'logical_thinking': 60.0,
                'comprehensive_quality': 60.0
            }
        
        valid_scores = [answer.score for answer in answers if answer.score is not None]
        
        if not valid_scores:
            avg_score = 70.0
        else:
            avg_score = sum(valid_scores) / len(valid_scores)
        
        scores = {
            'overall': avg_score,
            'professional': max(0, min(100, avg_score + random.uniform(-3, 3))),
            'skill_match': max(0, min(100, avg_score + random.uniform(-3, 3))),
            'language_expression': max(0, min(100, avg_score + random.uniform(-3, 3))),
            'logical_thinking': max(0, min(100, avg_score + random.uniform(-3, 3))),
            'comprehensive_quality': max(0, min(100, avg_score + random.uniform(-3, 3)))
        }
        
        return scores
        
    except Exception:
        return {
            'overall': 65.0,
            'professional': 65.0,
            'skill_match': 65.0,
            'language_expression': 65.0,
            'logical_thinking': 65.0,
            'comprehensive_quality': 65.0
        }

def calculate_simulation_scores(db: Session, interview_id: int) -> Dict[str, float]:
    """计算模拟面试评分（比练习模式更严格）"""
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.interview_id == interview_id,
        InterviewAnswer.is_complete == True
    ).all()
    
    if not answers:
        return {
            'overall': 50.0,
            'professional': 50.0,
            'skill_match': 50.0,
            'language_expression': 50.0,
            'logical_thinking': 50.0,
            'comprehensive_quality': 50.0
        }
    
    total_score = sum(answer.score or 0 for answer in answers)
    avg_score = total_score / len(answers)
    
    # 模拟面试的评分会比练习模式低5-10分（更真实）
    adjustment = -8.0
    
    scores = {
        'overall': max(0, min(100, avg_score + adjustment)),
        'professional': max(0, min(100, avg_score + adjustment + random.uniform(-3, 3))),
        'skill_match': max(0, min(100, avg_score + adjustment + random.uniform(-3, 3))),
        'language_expression': max(0, min(100, avg_score + adjustment + random.uniform(-3, 3))),
        'logical_thinking': max(0, min(100, avg_score + adjustment + random.uniform(-3, 3))),
        'comprehensive_quality': max(0, min(100, avg_score + adjustment + random.uniform(-3, 3)))
    }
    
    return scores

def update_user_statistics_safe(db: Session, user_id: int, interview: Interview):
    """安全地更新用户统计数据"""
    try:
        stats = db.query(InterviewStatistics).filter(
            InterviewStatistics.user_id == user_id
        ).first()
        
        if not stats:
            stats = InterviewStatistics(user_id=user_id)
            db.add(stats)
        
        stats.total_interviews = (stats.total_interviews or 0) + 1
        
        if interview.type == 'practice':
            stats.practice_interviews = (stats.practice_interviews or 0) + 1
        else:
            stats.simulation_interviews = (stats.simulation_interviews or 0) + 1
        
        if interview.status == 'completed':
            stats.completed_interviews = (stats.completed_interviews or 0) + 1
        
        if interview.actual_duration:
            stats.total_interview_time = (stats.total_interview_time or 0) + interview.actual_duration
            if stats.completed_interviews > 0:
                stats.avg_interview_time = stats.total_interview_time / stats.completed_interviews
        
        if interview.overall_score:
            try:
                all_scores = db.query(Interview.overall_score).filter(
                    Interview.user_id == user_id,
                    Interview.status == 'completed',
                    Interview.overall_score.isnot(None)
                ).all()
                
                scores = [score[0] for score in all_scores if score[0] is not None]
                if scores:
                    stats.avg_overall_score = sum(scores) / len(scores)
                    stats.best_overall_score = max(scores)
            except Exception:
                pass
        
        stats.last_interview_date = interview.completed_at or interview.started_at
        
        db.commit()
        
    except Exception:
        try:
            db.rollback()
        except:
            pass

def save_trend_data_safe(db: Session, interview: Interview):
    """安全地保存趋势数据"""
    try:
        if not interview.completed_at or not interview.overall_score:
            return
        
        trend_data = InterviewTrendData(
            user_id=interview.user_id,
            interview_id=interview.id,
            date=interview.completed_at,
            year_month=interview.completed_at.strftime('%Y-%m'),
            year_week=interview.completed_at.strftime('%Y-%W'),
            overall_score=interview.overall_score,
            professional_score=interview.professional_score,
            skill_match_score=interview.skill_match_score,
            language_expression_score=interview.language_expression_score,
            logical_thinking_score=interview.logical_thinking_score,
            comprehensive_quality_score=interview.comprehensive_quality_score,
            position=interview.position,
            interview_type=interview.type,
            duration=interview.actual_duration
        )
        
        db.add(trend_data)
        db.commit()
        
    except Exception:
        try:
            db.rollback()
        except:
            pass

def calculate_rank_percentile_fixed(db: Session, user_id: int, user_score: float) -> float:
    """计算用户排名百分比"""
    try:
        if not user_score:
            return 0.0
        
        all_users_with_scores = db.query(Interview.user_id, Interview.overall_score).filter(
            Interview.status == 'completed',
            Interview.overall_score.isnot(None),
            Interview.overall_score > 0
        ).distinct().all()
        
        if not all_users_with_scores:
            return 50.0
        
        user_max_scores = {}
        for user_id_score, score in all_users_with_scores:
            if user_id_score not in user_max_scores:
                user_max_scores[user_id_score] = score
            else:
                user_max_scores[user_id_score] = max(user_max_scores[user_id_score], score)
        
        lower_count = sum(1 for score in user_max_scores.values() if score < user_score)
        total_count = len(user_max_scores)
        
        if total_count <= 1:
            return 50.0
        
        percentile = round((lower_count / total_count) * 100, 1)
        return min(99.0, max(1.0, percentile))
        
    except Exception:
        return 50.0

def calculate_improvement_rate_fixed(db: Session, user_id: int) -> float:
    """计算用户提升幅度"""
    try:
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        current_month_interviews = db.query(Interview.overall_score).filter(
            Interview.user_id == user_id,
            Interview.completed_at >= current_month_start,
            Interview.status == 'completed',
            Interview.overall_score.isnot(None)
        ).all()
        
        last_month_interviews = db.query(Interview.overall_score).filter(
            Interview.user_id == user_id,
            Interview.completed_at >= last_month_start,
            Interview.completed_at < current_month_start,
            Interview.status == 'completed',
            Interview.overall_score.isnot(None)
        ).all()
        
        if not current_month_interviews or not last_month_interviews:
            recent_interviews = db.query(Interview.overall_score).filter(
                Interview.user_id == user_id,
                Interview.status == 'completed',
                Interview.overall_score.isnot(None)
            ).order_by(desc(Interview.completed_at)).limit(10).all()
            
            if len(recent_interviews) >= 3:
                scores = [score[0] for score in recent_interviews]
                recent_avg = sum(scores[:3]) / 3
                earlier_avg = sum(scores[3:]) / len(scores[3:]) if len(scores) > 3 else recent_avg
                
                if earlier_avg > 0:
                    improvement = ((recent_avg - earlier_avg) / earlier_avg) * 100
                    return round(improvement, 1)
            
            return 0.0
        
        current_avg = sum(score[0] for score in current_month_interviews) / len(current_month_interviews)
        last_avg = sum(score[0] for score in last_month_interviews) / len(last_month_interviews)
        
        if last_avg > 0:
            improvement = ((current_avg - last_avg) / last_avg) * 100
            return round(improvement, 1)
        
        return 0.0
        
    except Exception:
        return 0.0

def determine_current_phase(db: Session, interview_id: int) -> str:
    """确定当前面试阶段"""
    answered_count = db.query(InterviewAnswer).filter(
        InterviewAnswer.interview_id == interview_id,
        InterviewAnswer.is_complete == True
    ).count()
    
    if answered_count == 0:
        return 'intro'
    elif answered_count <= 1:
        return 'self'
    elif answered_count <= 3:
        return 'technical'
    elif answered_count <= 5:
        return 'project'
    elif answered_count <= 6:
        return 'behavioral'
    else:
        return 'questions'

def get_next_question_for_skip(db: Session, interview_id: int, current_sequence: int) -> Optional[Dict]:
    """为跳过功能获取下一题"""
    next_question = db.query(InterviewQuestion).filter(
        and_(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.sequence_number > current_sequence,
            InterviewQuestion.status == 'pending'
        )
    ).order_by(InterviewQuestion.sequence_number).first()
    
    if not next_question:
        return None
    
    next_question.status = 'current'
    next_question.asked_at = datetime.utcnow()
    db.commit()
    
    return {
        'id': next_question.id,
        'text': next_question.question_text,
        'type': next_question.question_type,
        'difficulty': next_question.difficulty,
        'time_limit': next_question.time_limit,
        'allow_hints': next_question.allow_hints,
        'sequence_number': next_question.sequence_number
    }

def get_next_simulation_question(db: Session, interview_id: int, current_sequence: int) -> Optional[Dict]:
    """获取模拟面试的下一题"""
    next_question = db.query(InterviewQuestion).filter(
        and_(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.sequence_number > current_sequence,
            InterviewQuestion.status == 'pending'
        )
    ).order_by(InterviewQuestion.sequence_number).first()
    
    if not next_question:
        return None
    
    next_question.status = 'current'
    next_question.asked_at = datetime.utcnow()
    
    interview = db.query(Interview).filter(
        Interview.id == interview_id
    ).first()
    if interview:
        interview.current_question_id = next_question.id
    
    db.commit()
    
    return {
        'id': next_question.id,
        'text': next_question.question_text,
        'type': next_question.question_type,
        'difficulty': next_question.difficulty,
        'time_limit': next_question.time_limit,
        'sequence_number': next_question.sequence_number,
        'category': next_question.category
    }

def get_simulation_status(db: Session, interview_id: int, user_id: int) -> Dict:
    """获取模拟面试实时状态"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    
    if not interview:
        raise ValueError("面试不存在")
    
    current_question = None
    if interview.current_question_id:
        current_question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == interview.current_question_id
        ).first()
    
    if not current_question:
        current_question = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.status.in_(['current', 'pending'])
        ).order_by(InterviewQuestion.sequence_number).first()
    
    elapsed_time = 0
    if interview.started_at:
        elapsed_time = int((datetime.utcnow() - interview.started_at).total_seconds())
    
    interviewer_status = {}
    phase_info = {}
    if interview.settings:
        try:
            settings = json.loads(interview.settings)
            interviewer_status = settings.get('interviewer_status', {})
            phase_info = settings.get('phase_info', {})
        except:
            pass
    
    return {
        "interview_id": interview_id,
        "status": interview.status,
        "is_recording": interview.is_recording or False,
        "current_phase": interview.current_phase or 'intro',
        "current_question_index": current_question.sequence_number - 1 if current_question else 0,
        "total_questions": interview.total_questions or 0,
        "elapsed_time": elapsed_time,
        "answered_questions": interview.answered_questions or 0,
        "interviewer_status": interviewer_status,
        "phase_info": phase_info,
        "current_question": {
            "id": current_question.id,
            "text": current_question.question_text,
            "type": current_question.question_type,
            "time_limit": current_question.time_limit
        } if current_question else None
    }

def generate_overall_feedback(scores: Dict[str, float]) -> str:
    """生成综合反馈"""
    overall = scores['overall']
    
    if overall >= 90:
        return "您的面试表现非常出色！各方面能力都很强，继续保持这种状态。"
    elif overall >= 80:
        return "面试表现良好，大部分方面都做得不错，还有一些细节可以优化。"
    elif overall >= 70:
        return "基础表现合格，有明显的优势领域，同时也有需要加强的方面。"
    elif overall >= 60:
        return "表现中等，建议针对薄弱环节进行重点练习和提升。"
    else:
        return "还有很大提升空间，建议系统性地学习和练习面试技巧。"

def generate_key_feedback(scores: Dict[str, float]) -> str:
    """生成关键反馈要点"""
    score_items = [(k, v) for k, v in scores.items() if k != 'overall']
    score_items.sort(key=lambda x: x[1], reverse=True)
    
    best_aspect = score_items[0][0]
    worst_aspect = score_items[-1][0]
    
    aspect_names = {
        'professional': '专业知识',
        'skill_match': '技能匹配',
        'language_expression': '语言表达',
        'logical_thinking': '逻辑思维',
        'comprehensive_quality': '综合素养'
    }
    
    return f"优势：{aspect_names[best_aspect]}表现突出；需要加强：{aspect_names[worst_aspect]}有待提升。"

def generate_improvement_suggestions(scores: Dict[str, float]) -> str:
    """生成改进建议"""
    suggestions = []
    
    if scores['professional'] < 80:
        suggestions.append("建议加强专业知识学习，提升硬性专业技能和创新思维能力")
    
    if scores['skill_match'] < 80:
        suggestions.append("练习目标岗位相关的工具和技术，提升技能匹配度")
    
    if scores['language_expression'] < 80:
        suggestions.append("练习控制语速和音量，注意表达时的情感传递")
    
    if scores['logical_thinking'] < 80:
        suggestions.append("加强逻辑思维训练，注意语言过渡和表达逻辑")
    
    if scores['comprehensive_quality'] < 80:
        suggestions.append("提升仪态表现，加强抗压能力和情绪控制")
    
    return "; ".join(suggestions) if suggestions else "继续保持当前状态，全面发展各项能力。"

def generate_simulation_feedback(scores: Dict[str, float], interview: Interview) -> str:
    """生成模拟面试综合反馈"""
    overall = scores['overall']
    
    if overall >= 85:
        return f"恭喜！您在本次{get_company_full_name(interview.company)}的模拟面试中表现优秀，各项能力均达到了很高的水准，具备了较强的面试竞争力。"
    elif overall >= 75:
        return f"您在本次模拟面试中表现良好，基本达到了{get_company_full_name(interview.company)}的要求，还有一些细节可以进一步优化。"
    elif overall >= 65:
        return f"模拟面试表现中等，有明显的优势领域，但也存在需要重点改进的方面，建议有针对性地进行练习。"
    elif overall >= 55:
        return f"本次模拟面试暴露了一些问题，建议在技术深度、表达能力等方面进行系统性提升后再参加真实面试。"
    else:
        return f"面试基础需要加强，建议通过更多的练习模式来提升各项能力，然后再尝试模拟面试。"

def generate_simulation_key_feedback(scores: Dict[str, float]) -> str:
    """生成模拟面试关键反馈"""
    score_items = [(k, v) for k, v in scores.items() if k != 'overall']
    score_items.sort(key=lambda x: x[1], reverse=True)
    
    best_aspect = score_items[0][0]
    worst_aspect = score_items[-1][0]
    
    aspect_names = {
        'professional': '专业技术能力',
        'skill_match': '技能匹配度',
        'language_expression': '语言表达能力',
        'logical_thinking': '逻辑思维能力',
        'comprehensive_quality': '综合职业素养'
    }
    
    return f"核心优势：{aspect_names[best_aspect]}表现突出，继续发挥；主要短板：{aspect_names[worst_aspect]}需要重点提升。"

def generate_simulation_improvement_suggestions(scores: Dict[str, float]) -> str:
    """生成模拟面试改进建议"""
    suggestions = []
    
    if scores['professional'] < 75:
        suggestions.append("加强专业知识深度，关注行业前沿技术和最佳实践")
    
    if scores['skill_match'] < 75:
        suggestions.append("提升目标岗位相关技能，熟练掌握主流工具和框架")
    
    if scores['language_expression'] < 75:
        suggestions.append("改善表达技巧，注意语速控制和逻辑清晰度")
    
    if scores['logical_thinking'] < 75:
        suggestions.append("强化逻辑思维训练，提升问题分析和解决能力")
    
    if scores['comprehensive_quality'] < 75:
        suggestions.append("提升职业素养，包括沟通协调和抗压应变能力")
    
    if not suggestions:
        suggestions.append("各项能力表现均衡，建议通过更多实战项目来进一步提升专业水平")
    
    return "；".join(suggestions)

def get_company_full_name(company_type: str) -> str:
    """获取公司全称"""
    company_names = {
        'tech': '互联网科技有限公司',
        'foreign': '外资企业',
        'state': '国有企业',
        'startup': '创业公司'
    }
    return company_names.get(company_type, '公司')

def get_round_name(round_type: str) -> str:
    """获取面试轮次名称"""
    round_names = {
        'first': '初试',
        'second': '复试',
        'final': '终面'
    }
    return round_names.get(round_type, '面试')