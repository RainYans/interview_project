# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.schemas import user as user_schema # 从schemas统一导入模型
from app.services import auth_service, user_service # 导入需要的服务
from app.core import security
from app.core.config import settings

router = APIRouter()

# ===== OAuth2 标准 Token 模型 =====
class Token(BaseModel):
    access_token: str
    token_type: str

# ===== 现有的注册接口 =====
@router.post("/register", response_model=user_schema.UserResponse, status_code=status.HTTP_201_CREATED, summary="用户注册")
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户，并返回不含密码的用户信息。
    """
    # 检查用户名是否已存在
    if auth_service.get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="该用户名已被注册")
        
    # 检查邮箱是否已存在
    if auth_service.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    # 创建用户
    user = auth_service.create_user(db, user_in=user_in)
    
    # 构造不含敏感信息的返回数据
    # 新注册用户一定没有个人资料
    return user_schema.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        has_profile=False 
    )

# ===== 现有的 JSON 登录接口 =====
@router.post("/login", summary="用户登录")
def login(
    user_credentials: user_schema.UserLogin, 
    db: Session = Depends(get_db)
):
    """通过用户名和密码登录 (接收JSON)"""
    # 使用 Pydantic 模型中的字段进行验证
    user = auth_service.authenticate_user(
        db, username=user_credentials.username, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户profile是否完善
    user_data = user_service.get_user_profile_data(db, user)

    # 创建Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # 返回统一的、包含所有需要信息的响应体
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": user_data # user_data 中已经包含了 has_profile 字段
    }

# ===== 🔥 新增：Swagger OAuth2 专用登录接口 =====
@router.post("/login-form", response_model=Token, summary="OAuth2 登录（Swagger专用）")
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    OAuth2 标准登录接口，专门用于 Swagger 文档的 Authorize 功能
    接收表单格式的用户名和密码
    """
    try:
        # 使用相同的认证逻辑
        user = auth_service.authenticate_user(
            db, username=form_data.username, password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码不正确",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        
        # 🔥 返回 OAuth2 标准格式
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

# ===== 🔥 新增：Token 验证接口（可选，用于测试） =====
@router.get("/me", response_model=user_schema.UserResponse, summary="获取当前用户信息")
def get_current_user_info(
    current_user = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息
    需要在请求头中包含 Authorization: Bearer <token>
    """
    # 获取完整的用户资料
    user_data = user_service.get_user_profile_data(db, current_user)
    
    return user_schema.UserResponse(**user_data)

# ===== 🔥 新增：Token 刷新接口（可选） =====
@router.post("/refresh", response_model=Token, summary="刷新访问令牌")
def refresh_token(
    current_user = Depends(security.get_current_user)
):
    """
    刷新访问令牌
    """
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(current_user.id)}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )