"""
系统监控API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from services.monitor_service import SystemMonitorService
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/monitor", tags=["系统监控"])

# 初始化服务
monitor_service = SystemMonitorService()
audit_logger = AuditLogger()


@router.get("/health", summary="健康检查")
async def health_check(current_user: dict = Depends(get_current_user)):
    """
    系统健康检查
    
    权限要求：登录用户
    """
    try:
        health_status = monitor_service.get_health_check()
        
        return {
            "status": "success",
            "health": health_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/system-info", summary="获取系统信息")
async def get_system_info(current_user: dict = Depends(get_current_user)):
    """
    获取系统基本信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看系统信息"
        )
    
    try:
        system_info = monitor_service.get_system_info()
        
        return {
            "status": "success",
            "system_info": system_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")


@router.get("/resources", summary="获取资源使用情况")
async def get_resource_usage(current_user: dict = Depends(get_current_user)):
    """
    获取系统资源使用情况
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看资源使用情况"
        )
    
    try:
        resource_usage = monitor_service.get_resource_usage()
        
        # 格式化字节数
        resource_usage["memory"]["total_formatted"] = monitor_service.format_bytes(resource_usage["memory"]["total"])
        resource_usage["memory"]["used_formatted"] = monitor_service.format_bytes(resource_usage["memory"]["used"])
        resource_usage["memory"]["free_formatted"] = monitor_service.format_bytes(resource_usage["memory"]["free"])
        
        resource_usage["disk"]["total_formatted"] = monitor_service.format_bytes(resource_usage["disk"]["total"])
        resource_usage["disk"]["used_formatted"] = monitor_service.format_bytes(resource_usage["disk"]["used"])
        resource_usage["disk"]["free_formatted"] = monitor_service.format_bytes(resource_usage["disk"]["free"])
        
        return {
            "status": "success",
            "resource_usage": resource_usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资源使用情况失败: {str(e)}")


@router.get("/application", summary="获取应用状态")
async def get_application_status(current_user: dict = Depends(get_current_user)):
    """
    获取应用系统状态
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看应用状态"
        )
    
    try:
        app_status = monitor_service.get_application_status()
        
        return {
            "status": "success",
            "application": app_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取应用状态失败: {str(e)}")


@router.get("/database", summary="获取数据库状态")
async def get_database_status(current_user: dict = Depends(get_current_user)):
    """
    获取数据库状态
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看数据库状态"
        )
    
    try:
        # 传递数据库对象
        db = {
            "users": USER_DATABASE,
            "enterprises": {},
            "survey_periods": {},
            "survey_data": {},
            "notifications": {},
            "audit_logs": []
        }
        
        db_status = monitor_service.get_database_status(db)
        
        return {
            "status": "success",
            "database": db_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库状态失败: {str(e)}")


@router.get("/performance", summary="获取性能指标")
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="查询最近N小时的数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取系统性能指标
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看性能指标"
        )
    
    try:
        performance_metrics = monitor_service.get_performance_metrics(hours)
        
        return {
            "status": "success",
            "performance": performance_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")


@router.get("/alerts", summary="获取系统告警")
async def get_alerts(current_user: dict = Depends(get_current_user)):
    """
    获取系统告警信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看系统告警"
        )
    
    try:
        alerts = monitor_service.get_alerts()
        
        # 统计告警数量
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a["level"] == "critical"])
        warning_alerts = len([a for a in alerts if a["level"] == "warning"])
        error_alerts = len([a for a in alerts if a["level"] == "error"])
        
        return {
            "status": "success",
            "total": total_alerts,
            "critical": critical_alerts,
            "warning": warning_alerts,
            "error": error_alerts,
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统告警失败: {str(e)}")


@router.get("/dashboard", summary="获取监控仪表盘数据")
async def get_monitor_dashboard(current_user: dict = Depends(get_current_user)):
    """
    获取监控仪表盘的综合数据
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看监控仪表盘"
        )
    
    try:
        # 获取各类数据
        health = monitor_service.get_health_check()
        resources = monitor_service.get_resource_usage()
        app_status = monitor_service.get_application_status()
        alerts = monitor_service.get_alerts()
        
        # 格式化资源数据
        resources["memory"]["total_formatted"] = monitor_service.format_bytes(resources["memory"]["total"])
        resources["memory"]["used_formatted"] = monitor_service.format_bytes(resources["memory"]["used"])
        resources["disk"]["total_formatted"] = monitor_service.format_bytes(resources["disk"]["total"])
        resources["disk"]["used_formatted"] = monitor_service.format_bytes(resources["disk"]["used"])
        
        return {
            "status": "success",
            "dashboard": {
                "health": health,
                "resources": resources,
                "application": app_status,
                "alerts": {
                    "total": len(alerts),
                    "critical": len([a for a in alerts if a["level"] == "critical"]),
                    "warning": len([a for a in alerts if a["level"] == "warning"]),
                    "error": len([a for a in alerts if a["level"] == "error"]),
                    "list": alerts
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控仪表盘失败: {str(e)}")