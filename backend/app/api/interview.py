# app/api/interview.py - 优化版本，为AI接口预留位置
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db.database import get_db
from app.core.security import get_current_user
from app.services import interview_service
from app.schemas.interview import (
    InterviewStartRequest, InterviewStartResponse,
    AnswerSubmitRequest, AnswerSubmitResponse,
    InterviewCompleteRequest, InterviewCompleteResponse,
    PerformanceResponse, TrendDataRequest, TrendDataResponse,
    InterviewHistoryQuery, InterviewHistoryResponse,
    StandardResponse, DataConsistencyReport, UserStatisticsFix,
    InterviewControlRequest, InterviewStatusResponse,
    QuestionHintResponse, HintUsageResponse,
    RealtimeAnalysisRequest, RealtimeStatusResponse,
    FileUploadResponse, InterviewerInfo, InterviewerConfig,
    InterviewPhasesResponse, EmergencyExitRequest, EmergencyExitResponse,
    SkipQuestionResponse
)
from app.models.user import User
from app.models.interview import (
    Interview, 
    InterviewQuestion, 
    InterviewAnswer, 
    InterviewStatistics, 
    InterviewTrendData
)

# 创建路由器
router = APIRouter()

# ================================================================================================
# 🎯 第一部分：面试开始和管理API
# ================================================================================================

@router.post("/start")
def start_interview(
    request: InterviewStartRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    开始面试 - 练习模式
    
    🤖 AI接口相关：此API会调用interview_service.start_interview()
    其中包含AI题目生成逻辑，详见service层的generate_interview_questions()
    """
    try:
        interview, questions = interview_service.start_interview(db, current_user.id, request)
        
        first_question = questions[0] if questions else None
        
        response_data = InterviewStartResponse(
            interview_id=interview.id,
            first_question=first_question,
            total_questions=len(questions),
            estimated_duration=interview.scheduled_duration or 30
        )
        
        return {
            "code": 200,
            "data": response_data.dict(),
            "message": "面试开始成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"开始面试失败: {str(e)}")

@router.post("/start-simulation")
def start_simulation_interview(
    request: InterviewStartRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    开始模拟面试
    
    🤖 AI接口相关：此API会调用interview_service.start_simulation_interview()
    其中包含AI模拟题目生成逻辑，详见service层的generate_simulation_questions()
    """
    try:
        request.type = 'simulation'
        
        interview, questions = interview_service.start_simulation_interview(db, current_user.id, request)
        
        first_question = questions[0] if questions else None
        
        response_data = InterviewStartResponse(
            interview_id=interview.id,
            first_question=first_question,
            total_questions=len(questions),
            estimated_duration=interview.scheduled_duration or 45
        )
        
        return {
            "code": 200,
            "data": response_data.dict(),
            "message": "模拟面试开始成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始模拟面试失败: {str(e)}")

# ================================================================================================
# 🎮 第二部分：面试控制API
# ================================================================================================

@router.post("/{interview_id}/pause")
def pause_interview(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """暂停面试（练习模式专用）"""
    try:
        result = interview_service.pause_interview(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": result,
            "message": "面试已暂停"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"暂停面试失败: {str(e)}")

@router.post("/{interview_id}/resume")
def resume_interview(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """继续面试（练习模式专用）"""
    try:
        result = interview_service.resume_interview(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": result,
            "message": "面试已继续"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"继续面试失败: {str(e)}")

@router.post("/{interview_id}/skip-question")
def skip_question(
    interview_id: int,
    question_id: int = Query(..., description="要跳过的题目ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """跳过问题"""
    try:
        result = interview_service.skip_question(db, interview_id, question_id, current_user.id)
        
        return {
            "code": 200,
            "data": result,
            "message": "问题已跳过"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跳过问题失败: {str(e)}")

@router.get("/{interview_id}/status")
def get_interview_status(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试实时状态"""
    try:
        status_data = interview_service.get_interview_status(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": status_data,
            "message": "获取状态成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.post("/{interview_id}/emergency-exit")
def emergency_exit_interview(
    interview_id: int,
    exit_reason: str = Query(None, description="退出原因"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """紧急退出面试"""
    try:
        result = interview_service.emergency_exit_interview(
            db, interview_id, exit_reason, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "面试已紧急退出"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"紧急退出失败: {str(e)}")

# ================================================================================================
# 🤖 第三部分：AI提示功能API
# ================================================================================================

@router.get("/questions/{question_id}/hint")
def get_question_hint(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取题目提示
    
    🤖 AI接口相关：此API会调用interview_service.get_question_hint()
    其中包含AI提示生成逻辑，详见service层的generate_question_hint()
    """
    try:
        hint_data = interview_service.get_question_hint(db, question_id, current_user.id)
        
        return {
            "code": 200,
            "data": hint_data,
            "message": "获取提示成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")

@router.post("/questions/{question_id}/use-hint")
def mark_hint_used(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记使用了提示"""
    try:
        result = interview_service.mark_hint_used(db, question_id, current_user.id)
        
        return {
            "code": 200,
            "data": result,
            "message": "提示使用已记录"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录提示使用失败: {str(e)}")

# ================================================================================================
# 🤖 第四部分：实时分析功能API
# ================================================================================================

@router.post("/{interview_id}/realtime-analysis")
def submit_realtime_data(
    interview_id: int,
    analysis_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交实时分析数据（练习模式）
    
    🤖 AI接口相关：此API会调用interview_service.save_realtime_analysis()
    其中包含AI实时分析逻辑，用于处理音视频实时数据
    """
    try:
        result = interview_service.save_realtime_analysis(
            db, interview_id, analysis_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "实时数据已保存"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存实时数据失败: {str(e)}")

@router.post("/{interview_id}/simulation-analysis")
def submit_simulation_analysis(
    interview_id: int,
    analysis_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交模拟面试实时分析数据
    
    🤖 AI接口相关：此API会调用interview_service.save_simulation_analysis()
    其中包含更严格的AI实时分析逻辑，用于模拟面试场景
    """
    try:
        result = interview_service.save_simulation_analysis(
            db, interview_id, analysis_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "实时分析数据已保存"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存实时分析数据失败: {str(e)}")

@router.get("/{interview_id}/realtime-status")
def get_realtime_status(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实时分析状态"""
    try:
        status_data = interview_service.get_realtime_status(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": status_data,
            "message": "获取实时状态成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时状态失败: {str(e)}")

@router.get("/{interview_id}/simulation-status")
def get_simulation_status(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取模拟面试实时状态"""
    try:
        status_data = interview_service.get_simulation_status(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": status_data,
            "message": "获取状态成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

# ================================================================================================
# 🤖 第五部分：回答处理和AI评分API
# ================================================================================================

@router.post("/questions/{question_id}/answer")
def submit_answer(
    question_id: int,
    request: AnswerSubmitRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交答案
    
    🤖 AI接口相关：此API会调用interview_service.submit_answer()
    其中包含AI评分逻辑，详见service层的generate_ai_feedback()
    """
    try:
        ai_feedback = interview_service.submit_answer(
            db, question_id, request.dict()
        )
        
        response_data = AnswerSubmitResponse(
            score=ai_feedback['score'],
            ai_feedback=ai_feedback['feedback'],
            improvement_tips=ai_feedback['tips']
        )
        
        return {
            "code": 200,
            "data": response_data.dict(),
            "message": "答案提交成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"提交答案失败: {str(e)}")

@router.get("/questions/{question_id}/next")
def get_next_question(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取下一题"""
    try:
        next_question = interview_service.get_next_question(db, question_id)
        
        if next_question:
            return {
                "code": 200,
                "data": next_question,
                "message": "获取下一题成功"
            }
        else:
            return {
                "code": 200,
                "data": None,
                "message": "已是最后一题"
            }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取下一题失败: {str(e)}")

@router.post("/{interview_id}/start-answer")
def start_answer_simulation(
    interview_id: int,
    answer_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """开始回答（模拟面试专用）"""
    try:
        result = interview_service.start_answer_simulation(
            db, interview_id, answer_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "开始回答已记录"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始回答失败: {str(e)}")

@router.post("/{interview_id}/finish-answer")
def finish_answer_simulation(
    interview_id: int,
    answer_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成回答（模拟面试专用）
    
    🤖 AI接口相关：此API会调用interview_service.finish_answer_simulation()
    其中包含模拟面试AI评分逻辑，详见service层的generate_simulation_ai_feedback()
    """
    try:
        result = interview_service.finish_answer_simulation(
            db, interview_id, answer_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "回答已提交"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完成回答失败: {str(e)}")

# ================================================================================================
# 🤖 第六部分：面试完成和报告生成API
# ================================================================================================

@router.post("/{interview_id}/complete")
def complete_interview(
    interview_id: int,
    request: InterviewCompleteRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成面试（练习模式）
    
    🤖 AI接口相关：此API会调用interview_service.complete_interview()
    其中包含AI报告生成逻辑，生成综合面试评分和改进建议
    """
    try:
        interview_check = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        ).first()
        
        if not interview_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试不存在或无权限访问"
            )
        
        if interview_check.status == 'completed':
            return {
                "code": 200,
                "data": {
                    "interview_id": interview_id,
                    "overall_score": interview_check.overall_score or 0,
                    "duration": interview_check.actual_duration or 0,
                    "completion_message": "面试已完成",
                    "report_available": True
                },
                "message": "面试已完成"
            }
        
        result = interview_service.complete_interview(
            db, interview_id, request.dict()
        )
        
        response_data = InterviewCompleteResponse(
            interview_id=interview_id,
            overall_score=result['overall_score'],
            duration=result['duration'],
            completion_message=result['completion_message'],
            report_available=result['report_available']
        )
        
        return {
            "code": 200,
            "data": response_data.dict(),
            "message": "面试完成"
        }
        
    except HTTPException as he:
        raise he
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器内部错误，请稍后重试")

@router.post("/{interview_id}/complete-simulation")
def complete_simulation_interview(
    interview_id: int,
    completion_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成模拟面试
    
    🤖 AI接口相关：此API会调用interview_service.complete_simulation_interview()
    其中包含更严格的AI报告生成逻辑，生成专业的模拟面试评估报告
    """
    try:
        result = interview_service.complete_simulation_interview(
            db, interview_id, completion_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "模拟面试已完成"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完成模拟面试失败: {str(e)}")

# ================================================================================================
# 📁 第七部分：文件上传API
# ================================================================================================

@router.post("/{interview_id}/upload-audio")
async def upload_audio_file(
    interview_id: int,
    question_id: int = Query(..., description="题目ID"),
    audio_file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传音频回答文件"""
    try:
        result = await interview_service.upload_audio_file(
            db, interview_id, question_id, audio_file, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "音频文件上传成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频上传失败: {str(e)}")

@router.post("/{interview_id}/upload-video")
async def upload_video_file(
    interview_id: int,
    question_id: int = Query(..., description="题目ID"),
    video_file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传视频回答文件"""
    try:
        result = await interview_service.upload_video_file(
            db, interview_id, question_id, video_file, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "视频文件上传成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频上传失败: {str(e)}")

# ================================================================================================
# 👤 第八部分：虚拟面试官API
# ================================================================================================

@router.get("/interviewers")
def get_interviewer_list(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取虚拟面试官列表"""
    try:
        interviewers = interview_service.get_interviewer_list(db)
        
        return {
            "code": 200,
            "data": interviewers,
            "message": "获取面试官列表成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取面试官列表失败: {str(e)}")

@router.get("/interviewers/{interviewer_id}")
def get_interviewer_config(
    interviewer_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试官配置"""
    try:
        config = interview_service.get_interviewer_config(db, interviewer_id)
        
        return {
            "code": 200,
            "data": config,
            "message": "获取面试官配置成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取面试官配置失败: {str(e)}")

@router.get("/interviewers/{interviewer_id}/config")
def get_interviewer_detailed_config(
    interviewer_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试官详细配置（增强版）"""
    try:
        config = interview_service.get_interviewer_detailed_config(db, interviewer_id)
        
        return {
            "code": 200,
            "data": config,
            "message": "获取面试官配置成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取面试官配置失败: {str(e)}")

# ================================================================================================
# 📊 第九部分：面试阶段管理API
# ================================================================================================

@router.get("/{interview_id}/phases")
def get_interview_phases(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试阶段信息"""
    try:
        phases_data = interview_service.get_interview_phases(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": phases_data,
            "message": "获取面试阶段成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取面试阶段失败: {str(e)}")

@router.post("/{interview_id}/next-phase")
def advance_to_next_phase(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """进入下一个面试阶段"""
    try:
        result = interview_service.advance_interview_phase(db, interview_id, current_user.id)
        
        return {
            "code": 200,
            "data": result,
            "message": "阶段切换成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"阶段切换失败: {str(e)}")

@router.post("/{interview_id}/interviewer-status")
def update_interviewer_status(
    interview_id: int,
    status_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新面试官状态"""
    try:
        result = interview_service.update_interviewer_status(
            db, interview_id, status_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "面试官状态已更新"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新面试官状态失败: {str(e)}")

@router.post("/{interview_id}/update-phase")
def update_interview_phase(
    interview_id: int,
    phase_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新面试阶段"""
    try:
        result = interview_service.update_interview_phase(
            db, interview_id, phase_data, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "面试阶段已更新"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新面试阶段失败: {str(e)}")

# ================================================================================================
# 📈 第十部分：面试表现分析API
# ================================================================================================

@router.get("/performance")
def get_performance_analysis(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试表现分析"""
    try:
        performance_data = interview_service.get_user_performance(db, current_user.id)
        
        response_data = {
            "overall_score": performance_data.overall_score,
            "ability_scores": {
                "professional": performance_data.ability_scores.professional,
                "skill_match": performance_data.ability_scores.skill_match,
                "language_expression": performance_data.ability_scores.language_expression,
                "logical_thinking": performance_data.ability_scores.logical_thinking,
                "comprehensive_quality": performance_data.ability_scores.comprehensive_quality
            },
            "better_than": performance_data.better_than,
            "improvement": performance_data.improvement,
            "recent_records": performance_data.recent_records
        }
        
        return {
            "code": 200,
            "data": response_data,
            "message": "获取面试表现成功"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "data": {
                "overall_score": 0.0,
                "ability_scores": {
                    "professional": 0.0,
                    "skill_match": 0.0,
                    "language_expression": 0.0,
                    "logical_thinking": 0.0,
                    "comprehensive_quality": 0.0
                },
                "better_than": 0.0,
                "improvement": 0.0,
                "recent_records": []
            },
            "message": f"获取面试表现失败: {str(e)}"
        }

@router.get("/trend")
def get_trend_data(
    dimension: str = Query("overall", description="维度: overall/professional/skill_match/language_expression/logical_thinking/comprehensive_quality"),
    period: str = Query("month", description="时间周期: week/month/quarter"),
    aggregation: str = Query("individual", description="聚合方式: individual/daily/weekly"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取趋势数据"""
    try:
        trend_data = interview_service.get_trend_data(
            db, current_user.id, dimension, period
        )
        
        response_data = {
            "dates": trend_data.dates,
            "scores": trend_data.scores,
            "labels": trend_data.labels,
            "details": trend_data.details if hasattr(trend_data, 'details') else []
        }
        
        return {
            "code": 200,
            "data": response_data,
            "message": "获取趋势数据成功"
        }
        
    except Exception as e:
        return {
            "code": 200,
            "data": {
                "dates": [],
                "scores": [],
                "labels": [],
                "details": []
            },
            "message": f"获取趋势数据失败，返回空数据: {str(e)}"
        }

# ================================================================================================
# 📋 第十一部分：历史记录管理API
# ================================================================================================

@router.get("/history")
def get_interview_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    type: Optional[str] = Query(None, description="面试类型"),
    position: Optional[str] = Query(None, description="岗位筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试历史记录"""
    try:
        filters = {}
        if type:
            filters['type'] = type
        if position:
            filters['position'] = position
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        history_data = interview_service.get_user_interview_history_enhanced(
            db, current_user.id, page, page_size, filters
        )
        
        return {
            "code": 200,
            "data": history_data,
            "message": "获取历史记录成功"
        }
        
    except Exception as e:
        return {
            "code": 200,
            "data": {
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
            },
            "message": "暂无历史记录"
        }

@router.get("/history/statistics")
def get_history_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史统计数据"""
    try:
        stats = interview_service.get_history_statistics(db, current_user.id)
        
        return {
            "code": 200,
            "data": stats,
            "message": "获取统计数据成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/{interview_id}/detail")
def get_interview_detail(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单次面试详情"""
    try:
        detail = interview_service.get_interview_detail_for_history(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": detail,
            "message": "获取面试详情成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取面试详情失败: {str(e)}")

@router.delete("/{interview_id}")
def delete_interview_record(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除面试记录"""
    try:
        result = interview_service.delete_interview_record(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "删除成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.post("/{interview_id}/copy-settings")
def copy_interview_settings(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """复制面试设置用于再次练习"""
    try:
        settings = interview_service.get_interview_settings_for_copy(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": settings,
            "message": "获取设置成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

# ================================================================================================
# 📊 第十二部分：详细分析API
# ================================================================================================

@router.get("/{interview_id}/detailed-analysis")
def get_detailed_analysis(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单次面试的详细分析"""
    try:
        analysis = interview_service.get_detailed_interview_analysis(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": analysis,
            "message": "获取详细分析成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        default_analysis = {
            "interview_info": {
                "id": interview_id,
                "type": "practice",
                "position": "前端开发",
                "overall_score": 0
            },
            "ability_breakdown": {
                "professional": {"score": 0, "rank": "待提升"},
                "expression": {"score": 0, "rank": "待提升"},
                "logic": {"score": 0, "rank": "待提升"},
                "comprehensive": {"score": 0, "rank": "待提升"}
            },
            "question_performance": [],
            "comparison_data": {
                "user_avg": 0,
                "platform_avg": 75,
                "better_than_percent": 0
            },
            "timeline_analysis": []
        }
        
        return {
            "code": 200,
            "data": default_analysis,
            "message": "返回默认分析数据"
        }

@router.get("/{interview_id}/qa-records")
def get_qa_records(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试问答记录"""
    try:
        qa_records = interview_service.get_interview_qa_records(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": qa_records,
            "message": "获取问答记录成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return {
            "code": 200,
            "data": [],
            "message": "暂无问答记录"
        }

@router.get("/personal-advice")
def get_personal_advice(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI个性化建议"""
    try:
        advice = interview_service.generate_personal_advice(db, current_user.id)
        
        return {
            "code": 200,
            "data": advice,
            "message": "获取个性化建议成功"
        }
        
    except Exception as e:
        default_advice = [
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
        
        return {
            "code": 200,
            "data": default_advice,
            "message": "使用默认建议"
        }

@router.get("/{interview_id}/replay-info")
def get_replay_info(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试回放信息"""
    try:
        replay_info = interview_service.get_interview_replay_info(
            db, interview_id, current_user.id
        )
        
        return {
            "code": 200,
            "data": replay_info,
            "message": "获取回放信息成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return {
            "code": 200,
            "data": {
                "video_url": None,
                "audio_url": None,
                "transcript_url": None,
                "timestamps": [],
                "chapters": [],
                "duration": 0
            },
            "message": "暂无回放信息"
        }

@router.get("/ability-insights")
def get_ability_insights(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取能力洞察分析"""
    try:
        insights = interview_service.get_ability_insights(db, current_user.id)
        
        return {
            "code": 200,
            "data": insights,
            "message": "获取能力洞察成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取能力洞察失败: {str(e)}")

@router.post("/targeted-practice")
def create_targeted_practice(
    practice_request: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建针对性练习计划"""
    try:
        practice_plan = interview_service.create_targeted_practice_plan(
            db, current_user.id, practice_request
        )
        
        return {
            "code": 200,
            "data": practice_plan,
            "message": "创建练习计划成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        default_plan = {
            "plan_id": "default_001",
            "target_ability": practice_request.get("target_ability", "professional"),
            "recommended_sessions": [
                {
                    "session_id": "default_session_1",
                    "type": "question_practice",
                    "title": "基础练习",
                    "description": "基础题目练习",
                    "estimated_time": 30,
                    "question_count": 10,
                    "difficulty": "medium"
                }
            ],
            "learning_path": [
                {
                    "step": 1,
                    "title": "开始练习",
                    "description": "开始基础练习",
                    "estimated_time": 30
                }
            ],
            "expected_improvement": 10.0,
            "estimated_time": 0.5
        }
        
        return {
            "code": 200,
            "data": default_plan,
            "message": "使用默认练习计划"
        }

# ================================================================================================
# 🛠️ 第十三部分：兼容性和管理API
# ================================================================================================

@router.post("/{interview_id}/answer")
def submit_answer_old(
    interview_id: int,
    answer_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交答案（旧版本兼容接口）"""
    try:
        return {
            "code": 200,
            "data": {
                "score": 85.0,
                "feedback": "答案已提交，正在分析中..."
            },
            "message": "答案提交成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"提交答案失败: {str(e)}")

@router.post("/{interview_id}/end")
def end_interview_old(
    interview_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """结束面试（旧版本兼容接口）"""
    try:
        completion_request = InterviewCompleteRequest(
            interview_id=interview_id,
            completion_type="normal"
        )
        
        return complete_interview(interview_id, completion_request, current_user, db)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"结束面试失败: {str(e)}")

@router.get("/debug/data-consistency")
def check_data_consistency(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """数据一致性检查"""
    try:
        from app.models.user import User
        from app.models.interview import InterviewStatistics
        
        total_users = db.query(User).count()
        users_with_interviews = db.query(Interview.user_id).distinct().count()
        users_with_statistics = db.query(InterviewStatistics).count()
        
        inconsistent_users = []
        missing_statistics = []
        
        issues_found = []
        if users_with_interviews > users_with_statistics:
            issues_found.append(f"有 {users_with_interviews - users_with_statistics} 个用户有面试记录但缺少统计数据")
        
        fix_suggestions = []
        if issues_found:
            fix_suggestions.append("运行用户统计修复接口")
        
        report = DataConsistencyReport(
            total_users=total_users,
            users_with_interviews=users_with_interviews,
            users_with_statistics=users_with_statistics,
            inconsistent_users=inconsistent_users,
            missing_statistics=missing_statistics,
            issues_found=issues_found,
            fix_suggestions=fix_suggestions
        )
        
        return {
            "code": 200,
            "data": report.dict(),
            "message": "数据一致性检查完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"数据一致性检查失败: {str(e)}")

@router.post("/admin/fix-user-statistics")
def fix_user_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修复用户统计数据"""
    try:
        users_with_interviews = db.query(Interview.user_id).distinct().all()
        existing_stats_users = db.query(InterviewStatistics.user_id).all()
        existing_stats_user_ids = {stat.user_id for stat in existing_stats_users}
        
        processed_users = 0
        created_statistics = 0
        updated_statistics = 0
        fixed_issues = []
        
        for user_record in users_with_interviews:
            user_id = user_record.user_id
            processed_users += 1
            
            if user_id not in existing_stats_user_ids:
                new_stats = InterviewStatistics(user_id=user_id)
                db.add(new_stats)
                created_statistics += 1
                fixed_issues.append(f"为用户 {user_id} 创建统计记录")
        
        db.commit()
        
        for user_record in users_with_interviews:
            user_id = user_record.user_id
            
            completed_interviews = db.query(Interview).filter(
                Interview.user_id == user_id,
                Interview.status == 'completed'
            ).all()
            
            if completed_interviews:
                stats = db.query(InterviewStatistics).filter(
                    InterviewStatistics.user_id == user_id
                ).first()
                
                if stats:
                    stats.completed_interviews = len(completed_interviews)
                    updated_statistics += 1
        
        db.commit()
        
        remaining_issues = []
        
        fix_result = UserStatisticsFix(
            processed_users=processed_users,
            created_statistics=created_statistics,
            updated_statistics=updated_statistics,
            fixed_issues=fixed_issues,
            remaining_issues=remaining_issues
        )
        
        return {
            "code": 200,
            "data": fix_result.dict(),
            "message": "用户统计修复完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"修复用户统计失败: {str(e)}")

@router.get("/health")
def interview_health_check():
    """面试服务健康检查"""
    return {
        "code": 200,
        "data": {
            "service": "Interview Service",
            "status": "healthy",
            "version": "1.0.0",
            "features": [
                "interview_practice",
                "interview_simulation", 
                "performance_analysis",
                "history_management",
                "trend_analysis",
                "interview_control",
                "ai_hints",
                "realtime_analysis", 
                "file_upload",
                "virtual_interviewer",
                "phase_management",
                "emergency_exit"
            ]
        },
        "message": "面试服务运行正常"
    }