"""
国家失业监测系统对接API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime

from services.national_system_service import (
    NationalSystemService,
    NationalSystemConfig,
    DataSyncManager,
    SyncStatus,
    NationalSystemStatus
)
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/national-system", tags=["国家系统对接"])

# 初始化服务
config = NationalSystemConfig()
national_service = NationalSystemService(config)
sync_manager = DataSyncManager(national_service)
audit_logger = AuditLogger()


@router.get("/status", summary="检查国家系统状态")
async def check_system_status(current_user: dict = Depends(get_current_user)):
    """
    检查国家失业监测系统的运行状态
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能检查国家系统状态"
        )
    
    try:
        status = national_service.check_system_status()
        
        return {
            "status": "success",
            "system_status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查系统状态失败: {str(e)}")


@router.post("/sync", summary="同步数据到国家系统")
async def sync_data(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    将就业数据同步到国家失业监测系统
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能同步数据到国家系统"
        )
    
    try:
        # 获取调查数据（这里使用模拟数据）
        # 实际应用中应该从数据库获取真实的调查数据
        mock_data = [
            {
                "enterprise_id": 1001,
                "enterprise_name": "昆明市某制造企业",
                "city_code": "5301",
                "city_name": "昆明市",
                "industry_code": "C",
                "industry": "制造业",
                "report_month": "2026-03",
                "total_employees": 1200,
                "employed_count": 1140,
                "unemployed_count": 60,
                "unemployment_rate": 5.0,
                "new_employees": 24,
                "lost_employees": 18,
                "created_at": datetime.now().isoformat()
            },
            {
                "enterprise_id": 1002,
                "enterprise_name": "大理州某服务企业",
                "city_code": "5329",
                "city_name": "大理州",
                "industry_code": "F",
                "industry": "服务业",
                "report_month": "2026-03",
                "total_employees": 800,
                "employed_count": 760,
                "unemployed_count": 40,
                "unemployment_rate": 5.0,
                "new_employees": 16,
                "lost_employees": 12,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # 创建同步任务
        sync_record = sync_manager.create_sync_task(survey_period_id, mock_data)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NATIONAL_SYSTEM_SYNC",
            resource_type="survey_period",
            resource_id=survey_period_id,
            details={
                "sync_id": sync_record["sync_id"],
                "total_records": sync_record["total_records"]
            },
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "数据同步已启动",
            "sync_record": sync_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")


@router.get("/sync/{sync_id}", summary="查询同步状态")
async def get_sync_status(
    sync_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    查询数据同步的状态
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查询同步状态"
        )
    
    try:
        sync_record = sync_manager.get_sync_record(sync_id)
        
        if not sync_record:
            raise HTTPException(status_code=404, detail="未找到同步记录")
        
        return {
            "status": "success",
            "sync_record": sync_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询同步状态失败: {str(e)}")


@router.get("/sync/history", summary="获取同步历史")
async def get_sync_history(
    survey_period_id: Optional[int] = Query(None, description="调查期ID"),
    status: Optional[str] = Query(None, description="同步状态"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    获取数据同步历史记录
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看同步历史"
        )
    
    try:
        records = sync_manager.list_sync_records(
            survey_period_id=survey_period_id,
            status=status
        )
        
        return {
            "status": "success",
            "total": len(records),
            "records": records[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取同步历史失败: {str(e)}")


@router.get("/sync/statistics", summary="获取同步统计")
async def get_sync_statistics(current_user: dict = Depends(get_current_user)):
    """
    获取数据同步统计信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看同步统计"
        )
    
    try:
        stats = sync_manager.get_sync_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取同步统计失败: {str(e)}")


@router.post("/sync/{sync_id}/retry", summary="重试同步")
async def retry_sync(
    sync_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    重试失败的同步任务
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能重试同步"
        )
    
    try:
        result = national_service.retry_sync(sync_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NATIONAL_SYSTEM_SYNC_RETRY",
            resource_type="sync",
            resource_id=sync_id,
            details={"new_sync_id": result["new_sync_id"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": result["message"],
            "new_sync_id": result["new_sync_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重试同步失败: {str(e)}")


@router.post("/sync/{sync_id}/cancel", summary="取消同步")
async def cancel_sync(
    sync_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取消正在进行的同步任务
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能取消同步"
        )
    
    try:
        result = national_service.cancel_sync(sync_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NATIONAL_SYSTEM_SYNC_CANCEL",
            resource_type="sync",
            resource_id=sync_id,
            details={},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消同步失败: {str(e)}")


@router.get("/data/query", summary="查询国家系统数据")
async def query_national_data(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    region_code: Optional[str] = Query(None, description="地区代码"),
    current_user: dict = Depends(get_current_user)
):
    """
    从国家系统查询就业数据
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查询国家系统数据"
        )
    
    try:
        result = national_service.query_national_data(start_date, end_date, region_code)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询国家系统数据失败: {str(e)}")


@router.post("/data/validate", summary="验证数据格式")
async def validate_data_format(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    验证数据格式是否符合国家系统要求
    
    权限要求：登录用户
    """
    try:
        validation_result = national_service.validate_data_format(data)
        
        return {
            "status": "success",
            "validation": validation_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证数据格式失败: {str(e)}")


@router.get("/config", summary="获取国家系统配置")
async def get_system_config(current_user: dict = Depends(get_current_user)):
    """
    获取国家系统对接配置信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看系统配置"
        )
    
    try:
        config_info = {
            "base_url": config.base_url,
            "timeout": config.timeout,
            "retry_times": config.retry_times,
            "retry_delay": config.retry_delay,
            "api_key_configured": bool(config.api_key),
            "secret_key_configured": bool(config.secret_key)
        }
        
        return {
            "status": "success",
            "config": config_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")