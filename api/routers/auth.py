from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from core.security import get_password_hash, verify_password, create_access_token
from core.dependencies import get_current_user
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/auth", tags=["1. 身份认证中心"])


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