from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from core.dependencies import PermissionChecker, get_current_user
from core.audit import audit_logger, data_protection
from pydantic import BaseModel, Field

router = APIRouter(prefix="/audit", tags=["4. 审计日志查询"])

# ==================== 数据模型 ====================

class AuditLogQuery(BaseModel):
    """审计日志查询参数"""
    user_id: Optional[int] = Field(None, description="按用户ID筛选")
    operation_type: Optional[str] = Field(None, description="按操作类型筛选")
    table_name: Optional[str] = Field(None, description="按表名筛选")
    record_id: Optional[int] = Field(None, description="按记录ID筛选")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    limit: int = Field(100, ge=1, le=1000, description="返回记录数量限制")


# ==================== 审计日志查询接口 ====================

@router.get("/logs",
            summary="查询审计日志",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def query_audit_logs(
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    operation_type: Optional[str] = Query(None, description="按操作类型筛选"),
    table_name: Optional[str] = Query(None, description="按表名筛选"),
    record_id: Optional[int] = Query(None, description="按记录ID筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """
    查询系统审计日志
    
    权限要求: PRO_ADMIN (省级管理员)
    支持多条件组合查询
    """
    logs = audit_logger.get_logs(
        user_id=user_id,
        operation_type=operation_type,
        table_name=table_name,
        record_id=record_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return {
        "total": len(logs),
        "query_params": {
            "user_id": user_id,
            "operation_type": operation_type,
            "table_name": table_name,
            "record_id": record_id,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        },
        "logs": logs
    }


@router.get("/logs/{log_id}",
            summary="获取单条审计日志详情",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_audit_log_detail(log_id: int, current_user: dict = Depends(get_current_user)):
    """
    获取指定审计日志的详细信息
    
    权限要求: PRO_ADMIN (省级管理员)
    """
    log = audit_logger.get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="未找到指定的审计日志")
    
    return {
        "log": log
    }


@router.get("/logs/enterprise/{enterprise_id}",
            summary="查询企业相关操作日志",
            dependencies=[Depends(PermissionChecker("PRO_AUDIT"))])
async def get_enterprise_audit_logs(
    enterprise_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    查询指定企业的所有操作日志
    
    权限要求: PRO_AUDIT (省级审核权限)
    """
    logs = audit_logger.get_logs(
        table_name="t_enterprise_info",
        record_id=enterprise_id,
        limit=100
    )
    
    return {
        "enterprise_id": enterprise_id,
        "total_operations": len(logs),
        "logs": logs
    }


@router.get("/logs/user/{user_id}",
            summary="查询用户操作日志",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_user_audit_logs(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    查询指定用户的所有操作日志
    
    权限要求: PRO_ADMIN (省级管理员)
    """
    logs = audit_logger.get_logs(
        user_id=user_id,
        limit=100
    )
    
    return {
        "user_id": user_id,
        "total_operations": len(logs),
        "logs": logs
    }


@router.get("/statistics",
            summary="获取审计统计信息",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_audit_statistics(current_user: dict = Depends(get_current_user)):
    """
    获取审计日志的统计信息
    
    权限要求: PRO_ADMIN (省级管理员)
    """
    all_logs = audit_logger.get_logs(limit=10000)
    
    # 按操作类型统计
    operation_stats = {}
    for log in all_logs:
        op_type = log.get("operation_type", "UNKNOWN")
        operation_stats[op_type] = operation_stats.get(op_type, 0) + 1
    
    # 按表名统计
    table_stats = {}
    for log in all_logs:
        table_name = log.get("table_name", "UNKNOWN")
        table_stats[table_name] = table_stats.get(table_name, 0) + 1
    
    # 按用户统计
    user_stats = {}
    for log in all_logs:
        user_id = log.get("user_id", 0)
        user_stats[user_id] = user_stats.get(user_id, 0) + 1
    
    return {
        "total_logs": len(all_logs),
        "operation_statistics": operation_stats,
        "table_statistics": table_stats,
        "user_statistics": user_stats,
        "recent_activities": all_logs[:10]  # 最近10条活动
    }


@router.get("/data-protection/rules",
            summary="获取数据保护规则",
            dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def get_data_protection_rules(current_user: dict = Depends(get_current_user)):
    """
    获取数据保护规则信息
    
    权限要求: PRO_ADMIN (省级管理员)
    """
    return {
        "protected_fields": data_protection.PROTECTED_FIELDS,
        "protected_records": list(data_protection.PROTECTED_RECORDS.keys()),
        "sensitive_operations": data_protection.SENSITIVE_OPERATIONS,
        "description": "这些字段和记录受到特别保护，修改或删除需要特殊权限"
    }


class DataValidationRequest(BaseModel):
    """数据验证请求模型"""
    table_name: str = Field(..., description="表名")
    old_data: dict = Field(..., description="旧数据")
    new_data: dict = Field(..., description="新数据")


@router.post("/data-protection/validate",
             summary="验证数据变更合法性",
             dependencies=[Depends(PermissionChecker("PRO_ADMIN"))])
async def validate_data_change(
    req: DataValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    验证数据变更是否符合保护规则
    
    权限要求: PRO_ADMIN (省级管理员)
    """
    user_role = current_user.get("role_name", "")
    
    # 验证数据变更
    is_valid, error_message = data_protection.validate_data_change(
        table_name=req.table_name,
        old_data=req.old_data,
        new_data=req.new_data,
        user_role=user_role
    )
    
    if not is_valid:
        return {
            "valid": False,
            "error": error_message,
            "suggestion": "请检查数据变更是否符合保护规则"
        }
    
    # 验证数据完整性
    is_complete, integrity_error = data_protection.check_data_integrity(
        table_name=req.table_name,
        record_data=req.new_data
    )
    
    if not is_complete:
        return {
            "valid": False,
            "error": integrity_error,
            "suggestion": "请确保数据完整性"
        }
    
    return {
        "valid": True,
        "message": "数据变更符合所有保护规则",
        "checks_passed": [
            "字段修改权限检查",
            "数据完整性检查",
            "敏感操作权限检查"
        ]
    }