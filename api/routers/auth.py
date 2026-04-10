from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
from core.security import get_password_hash, verify_password, create_access_token
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/auth", tags=["1. 身份认证中心"])
audit_logger = AuditLogger()


# ==================== 数据模型 ====================

class PasswordChangeRequest(BaseModel):
    """密码修改请求模型"""
    old_password: str = Field(..., description="旧密码", min_length=1)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=50)
    confirm_password: str = Field(..., description="确认新密码", min_length=1)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        if len(v) > 50:
            raise ValueError('密码长度不能超过50位')
        # 可以添加更多密码强度验证规则
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证两次密码是否一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


@router.post("/login", summary="用户登录与签发令牌")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录接口，支持多角色登录"""
    user = USER_DATABASE.get(form_data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="对不起，您输入的账号或密码不正确")
    
    # 验证密码
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="对不起，您输入的账号或密码不正确")
    
    # 检查用户状态
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="该账号已被禁用，请联系管理员")
    
    # 生成JWT令牌
    token_data = {
        "user_id": user["user_id"],
        "username": user["username"],
        "role_id": user["role_id"],
        "role_name": user["role_name"]
    }
    token = create_access_token(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_info": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role_name": user["role_name"],
            "full_name": user.get("full_name", "")
        }
    }


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "role_id": current_user.get("role_id"),
        "role_name": current_user.get("role_name"),
        "login_time": current_user.get("login_time")
    }


@router.post("/change-password", summary="修改用户密码")
async def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    修改当前用户的密码
    
    权限要求：登录用户
    """
    try:
        # 获取当前用户信息
        username = current_user.get("username")
        user = USER_DATABASE.get(username)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 验证旧密码
        if not verify_password(request.old_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="旧密码不正确")
        
        # 验证新旧密码是否相同
        if verify_password(request.new_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
        
        # 生成新密码哈希
        new_password_hash = get_password_hash(request.new_password)
        
        # 更新密码
        user["password_hash"] = new_password_hash
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="PASSWORD_CHANGE",
            resource_type="user",
            resource_id=user["user_id"],
            details={"username": username},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "密码修改成功，请重新登录",
            "user_id": user["user_id"],
            "username": username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"密码修改失败: {str(e)}")