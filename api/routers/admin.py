from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List, Optional
from core.dependencies import PermissionChecker, get_current_user
from db.mock_db import t_survey_period, USER_DATABASE, t_operation_log
from pydantic import BaseModel, Field

router = APIRouter(prefix="/admin", tags=["3. 系统管理中心"])


# ==================== 数据模型 ====================

class SurveyPeriodCreate(BaseModel):
    period_name: str = Field(..., description="调查期名称")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")

class SurveyPeriodUpdate(BaseModel):
    period_name: Optional[str] = Field(None, description="调查期名称")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    status: Optional[str] = Field(None, description="状态: active, closed, pending")

class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    full_name: str = Field(..., description="真实姓名")
    role_id: int = Field(..., description="角色ID: 1-省级管理员, 2-市级审核员, 3-企业用户")

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="真实姓名")
    role_id: Optional[int] = Field(None, description="角色ID")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ==================== 调查期管理 ====================

@router.get("/survey-periods", 
            summary="获取所有调查期列表",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_survey_periods(current_user: dict = Depends(get_current_user)):
    """获取系统中所有调查期的配置信息"""
    periods = []
    for period_id, period_data in t_survey_period.items():
        periods.append({
            "period_id": period_id,
            "period_name": period_data["period_name"],
            "start_date": period_data["start_date"],
            "end_date": period_data["end_date"],
            "status": period_data["status"]
        })
    
    return {
        "total": len(periods),
        "periods": periods
    }


@router.get("/survey-periods/{period_id}",
            summary="获取指定调查期详情",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_survey_period(period_id: int, current_user: dict = Depends(get_current_user)):
    """获取指定调查期的详细信息"""
    period = t_survey_period.get(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="未找到指定的调查期")
    
    return {
        "period_id": period_id,
        **period
    }


@router.post("/survey-periods",
             summary="创建新调查期",
             dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def create_survey_period(req: SurveyPeriodCreate, current_user: dict = Depends(get_current_user)):
    """创建新的调查期配置"""
    # 生成新的调查期ID
    new_period_id = max(t_survey_period.keys()) + 1 if t_survey_period else 1
    
    # 验证日期格式
    try:
        datetime.strptime(req.start_date, "%Y-%m-%d")
        datetime.strptime(req.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    # 创建调查期
    t_survey_period[new_period_id] = {
        "period_id": new_period_id,
        "period_name": req.period_name,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "status": "pending"
    }
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "CREATE_SURVEY_PERIOD",
        "table_name": "t_survey_period",
        "record_id": new_period_id,
        "old_value": "",
        "new_value": req.period_name,
        "reason": "创建新调查期",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"调查期【{req.period_name}】创建成功",
        "period_id": new_period_id,
        "audit_log": log_entry
    }


@router.put("/survey-periods/{period_id}",
            summary="更新调查期信息",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def update_survey_period(period_id: int, req: SurveyPeriodUpdate, current_user: dict = Depends(get_current_user)):
    """更新指定调查期的信息"""
    period = t_survey_period.get(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="未找到指定的调查期")
    
    # 记录旧值
    old_values = period.copy()
    
    # 更新字段
    if req.period_name:
        period["period_name"] = req.period_name
    if req.start_date:
        try:
            datetime.strptime(req.start_date, "%Y-%m-%d")
            period["start_date"] = req.start_date
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式不正确")
    if req.end_date:
        try:
            datetime.strptime(req.end_date, "%Y-%m-%d")
            period["end_date"] = req.end_date
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式不正确")
    if req.status:
        if req.status not in ["active", "closed", "pending"]:
            raise HTTPException(status_code=400, detail="状态值不正确，可选值: active, closed, pending")
        period["status"] = req.status
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "UPDATE_SURVEY_PERIOD",
        "table_name": "t_survey_period",
        "record_id": period_id,
        "old_value": str(old_values),
        "new_value": str(period),
        "reason": "更新调查期信息",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"调查期【{period['period_name']}】更新成功",
        "period": period,
        "audit_log": log_entry
    }


@router.delete("/survey-periods/{period_id}",
               summary="删除调查期",
               dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def delete_survey_period(period_id: int, current_user: dict = Depends(get_current_user)):
    """删除指定的调查期"""
    period = t_survey_period.get(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="未找到指定的调查期")
    
    if period["status"] == "active":
        raise HTTPException(status_code=400, detail="无法删除正在使用的调查期")
    
    period_name = period["period_name"]
    del t_survey_period[period_id]
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "DELETE_SURVEY_PERIOD",
        "table_name": "t_survey_period",
        "record_id": period_id,
        "old_value": period_name,
        "new_value": "",
        "reason": "删除调查期",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"调查期【{period_name}】删除成功",
        "audit_log": log_entry
    }


# ==================== 用户管理 ====================

@router.get("/users",
            summary="获取所有用户列表",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_users(current_user: dict = Depends(get_current_user)):
    """获取系统中所有用户的信息"""
    users = []
    for username, user_data in USER_DATABASE.items():
        users.append({
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "full_name": user_data.get("full_name", ""),
            "role_id": user_data["role_id"],
            "role_name": user_data["role_name"],
            "is_active": user_data.get("is_active", True)
        })
    
    return {
        "total": len(users),
        "users": users
    }


@router.get("/users/{user_id}",
            summary="获取指定用户详情",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """获取指定用户的详细信息"""
    for user_data in USER_DATABASE.values():
        if user_data["user_id"] == user_id:
            return {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "full_name": user_data.get("full_name", ""),
                "role_id": user_data["role_id"],
                "role_name": user_data["role_name"],
                "is_active": user_data.get("is_active", True)
            }
    
    raise HTTPException(status_code=404, detail="未找到指定的用户")


@router.post("/users",
             summary="创建新用户",
             dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def create_user(req: UserCreate, current_user: dict = Depends(get_current_user)):
    """创建新的系统用户"""
    # 检查用户名是否已存在
    if req.username in USER_DATABASE:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证角色ID
    if req.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="角色ID不正确，可选值: 1-省级管理员, 2-市级审核员, 3-企业用户")
    
    # 生成新的用户ID
    new_user_id = max(user["user_id"] for user in USER_DATABASE.values()) + 1
    
    # 密码加密
    from core.security import get_password_hash
    password_hash = get_password_hash(req.password)
    
    # 角色名称映射
    role_names = {1: "省级管理员", 2: "市级审核员", 3: "企业用户"}
    
    # 创建用户
    USER_DATABASE[req.username] = {
        "user_id": new_user_id,
        "username": req.username,
        "password_hash": password_hash,
        "role_id": req.role_id,
        "role_name": role_names[req.role_id],
        "full_name": req.full_name,
        "is_active": True
    }
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "CREATE_USER",
        "table_name": "USER_DATABASE",
        "record_id": new_user_id,
        "old_value": "",
        "new_value": req.username,
        "reason": f"创建新用户: {req.full_name}",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"用户【{req.username}】创建成功",
        "user_id": new_user_id,
        "audit_log": log_entry
    }


@router.put("/users/{user_id}",
            summary="更新用户信息",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def update_user(user_id: int, req: UserUpdate, current_user: dict = Depends(get_current_user)):
    """更新指定用户的信息"""
    target_user = None
    target_username = None
    
    for username, user_data in USER_DATABASE.items():
        if user_data["user_id"] == user_id:
            target_user = user_data
            target_username = username
            break
    
    if not target_user:
        raise HTTPException(status_code=404, detail="未找到指定的用户")
    
    # 记录旧值
    old_values = {
        "full_name": target_user.get("full_name", ""),
        "role_id": target_user["role_id"],
        "is_active": target_user.get("is_active", True)
    }
    
    # 更新字段
    if req.full_name:
        target_user["full_name"] = req.full_name
    if req.role_id:
        if req.role_id not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="角色ID不正确")
        role_names = {1: "省级管理员", 2: "市级审核员", 3: "企业用户"}
        target_user["role_id"] = req.role_id
        target_user["role_name"] = role_names[req.role_id]
    if req.is_active is not None:
        target_user["is_active"] = req.is_active
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "UPDATE_USER",
        "table_name": "USER_DATABASE",
        "record_id": user_id,
        "old_value": str(old_values),
        "new_value": str({
            "full_name": target_user.get("full_name", ""),
            "role_id": target_user["role_id"],
            "is_active": target_user.get("is_active", True)
        }),
        "reason": "更新用户信息",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"用户【{target_username}】信息更新成功",
        "user": {
            "user_id": target_user["user_id"],
            "username": target_user["username"],
            "full_name": target_user.get("full_name", ""),
            "role_id": target_user["role_id"],
            "role_name": target_user["role_name"],
            "is_active": target_user.get("is_active", True)
        },
        "audit_log": log_entry
    }


@router.delete("/users/{user_id}",
               summary="删除用户",
               dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """删除指定的用户"""
    target_username = None
    
    for username, user_data in USER_DATABASE.items():
        if user_data["user_id"] == user_id:
            # 不允许删除自己
            if user_id == current_user.get("user_id"):
                raise HTTPException(status_code=400, detail="不能删除当前登录的用户")
            target_username = username
            break
    
    if not target_username:
        raise HTTPException(status_code=404, detail="未找到指定的用户")
    
    full_name = USER_DATABASE[target_username].get("full_name", "")
    del USER_DATABASE[target_username]
    
    # 记录操作日志
    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": "DELETE_USER",
        "table_name": "USER_DATABASE",
        "record_id": user_id,
        "old_value": f"{target_username} ({full_name})",
        "new_value": "",
        "reason": "删除用户",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)
    
    return {
        "status": "success",
        "msg": f"用户【{target_username}】删除成功",
        "audit_log": log_entry
    }


@router.get("/audit-logs",
            summary="获取操作审计日志",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_audit_logs(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """获取系统操作审计日志"""
    logs = sorted(t_operation_log, key=lambda x: x["operation_time"], reverse=True)[:limit]
    
    return {
        "total": len(t_operation_log),
        "logs": logs
    }