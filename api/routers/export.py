"""
数据导出API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import date

from services.export_service import ExcelExportService
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE, t_enterprise_info

router = APIRouter(prefix="/export", tags=["数据导出"])

export_service = ExcelExportService()
audit_logger = AuditLogger()


@router.get("/enterprises", summary="导出企业列表")
async def export_enterprises(
    format: str = Query("excel", description="导出格式：excel, csv"),
    current_user: dict = Depends(get_current_user)
):
    """
    导出企业列表数据
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能导出企业列表"
        )
    
    try:
        # 获取企业数据
        enterprises = []
        for enterprise_id, info in t_enterprise_info.items():
            enterprise_data = {
                "enterprise_id": enterprise_id,
                "enterprise_name": info.get("enterprise_name", ""),
                "organization_code": info.get("organization_code", ""),
                "enterprise_nature": info.get("enterprise_nature", ""),
                "industry": info.get("industry", ""),
                "main_business": info.get("main_business", ""),
                "contact_person": info.get("contact_person", ""),
                "contact_address": info.get("contact_address", ""),
                "postal_code": info.get("postal_code", ""),
                "contact_phone": info.get("contact_phone", ""),
                "fax": info.get("fax", ""),
                "contact_email": info.get("contact_email", ""),
                "filing_status": info.get("filing_status", 0),
                "region_name": info.get("region_name", ""),
                "created_at": info.get("created_at", "")
            }
            enterprises.append(enterprise_data)
        
        if not enterprises:
            raise HTTPException(status_code=404, detail="没有可导出的企业数据")
        
        # 导出数据
        output = export_service.export_enterprise_list(enterprises)
        filename = export_service.generate_filename("企业列表")
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="EXPORT_ENTERPRISES",
            resource_type="enterprise",
            resource_id=0,
            details={"count": len(enterprises), "format": format},
            ip_address="127.0.0.1"
        )
        
        # 返回文件
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出企业列表失败: {str(e)}")


@router.get("/survey-data", summary="导出调查数据")
async def export_survey_data(
    survey_period_id: int = Query(..., description="调查期ID"),
    survey_period_name: str = Query("", description="调查期名称"),
    format: str = Query("excel", description="导出格式：excel, csv"),
    current_user: dict = Depends(get_current_user)
):
    """
    导出调查数据
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能导出调查数据"
        )
    
    try:
        # 获取调查数据（这里使用模拟数据）
        # 实际应用中应该从数据库获取真实的调查数据
        survey_data = [
            {
                "survey_id": 1,
                "enterprise_id": 1001,
                "enterprise_name": "昆明市某制造企业",
                "survey_period_id": survey_period_id,
                "report_month": "2026-03",
                "total_employees": 1200,
                "employed_count": 1140,
                "unemployed_count": 60,
                "unemployment_rate": 5.0,
                "new_employees": 24,
                "lost_employees": 18,
                "net_change": 6,
                "industry": "制造业",
                "business_scale": "中型",
                "contact_person": "张三",
                "contact_phone": "13800138000",
                "submit_time": "2026-03-30 10:00:00",
                "status": "已审核"
            },
            {
                "survey_id": 2,
                "enterprise_id": 1002,
                "enterprise_name": "大理州某服务企业",
                "survey_period_id": survey_period_id,
                "report_month": "2026-03",
                "total_employees": 800,
                "employed_count": 760,
                "unemployed_count": 40,
                "unemployment_rate": 5.0,
                "new_employees": 16,
                "lost_employees": 12,
                "net_change": 4,
                "industry": "服务业",
                "business_scale": "小型",
                "contact_person": "李四",
                "contact_phone": "13900139000",
                "submit_time": "2026-03-30 11:00:00",
                "status": "已审核"
            }
        ]
        
        if not survey_data:
            raise HTTPException(status_code=404, detail="没有可导出的调查数据")
        
        # 导出数据
        output = export_service.export_survey_data(survey_data, survey_period_name)
        filename = export_service.generate_filename(f"调查数据_{survey_period_name}")
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="EXPORT_SURVEY_DATA",
            resource_type="survey_data",
            resource_id=survey_period_id,
            details={"survey_period_id": survey_period_id, "count": len(survey_data)},
            ip_address="127.0.0.1"
        )
        
        # 返回文件
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出调查数据失败: {str(e)}")


@router.get("/summary-statistics", summary="导出汇总统计数据")
async def export_summary_statistics(
    survey_period_id: int = Query(..., description="调查期ID"),
    survey_period_name: str = Query("", description="调查期名称"),
    format: str = Query("excel", description="导出格式：excel, csv"),
    current_user: dict = Depends(get_current_user)
):
    """
    导出汇总统计数据
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能导出汇总统计"
        )
    
    try:
        # 获取汇总统计数据（这里使用模拟数据）
        summary_data = {
            "overall_statistics": {
                "total_enterprises": 1250,
                "total_employees": 87000,
                "employed_count": 82650,
                "unemployed_count": 4350,
                "unemployment_rate": 5.0,
                "new_employees": 1740,
                "lost_employees": 1305,
                "net_change": 435
            },
            "dimension_statistics": [
                {
                    "dimension_name": "region",
                    "dimension_value": "昆明市",
                    "total_enterprises": 300,
                    "total_employees": 30000,
                    "employed_count": 28500,
                    "unemployed_count": 1500,
                    "unemployment_rate": 5.0,
                    "new_employees": 600,
                    "lost_employees": 450,
                    "net_change": 150
                },
                {
                    "dimension_name": "region",
                    "dimension_value": "大理州",
                    "total_enterprises": 200,
                    "total_employees": 20000,
                    "employed_count": 19000,
                    "unemployed_count": 1000,
                    "unemployment_rate": 5.0,
                    "new_employees": 400,
                    "lost_employees": 300,
                    "net_change": 100
                }
            ],
            "time_series_data": [
                {
                    "period": "2026-01",
                    "total_employees": 85000,
                    "employed_count": 80750,
                    "unemployed_count": 4250,
                    "unemployment_rate": 5.0,
                    "new_employees": 1700,
                    "lost_employees": 1275,
                    "net_change": 425
                },
                {
                    "period": "2026-02",
                    "total_employees": 86000,
                    "employed_count": 81700,
                    "unemployed_count": 4300,
                    "unemployment_rate": 5.0,
                    "new_employees": 1720,
                    "lost_employees": 1290,
                    "net_change": 430
                }
            ]
        }
        
        # 导出数据
        output = export_service.export_summary_statistics(summary_data, survey_period_name)
        filename = export_service.generate_filename(f"汇总统计_{survey_period_name}")
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="EXPORT_SUMMARY_STATISTICS",
            resource_type="summary_statistics",
            resource_id=survey_period_id,
            details={"survey_period_id": survey_period_id},
            ip_address="127.0.0.1"
        )
        
        # 返回文件
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出汇总统计失败: {str(e)}")


@router.get("/audit-logs", summary="导出审计日志")
async def export_audit_logs(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    format: str = Query("excel", description="导出格式：excel, csv"),
    current_user: dict = Depends(get_current_user)
):
    """
    导出审计日志
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能导出审计日志"
        )
    
    try:
        # 获取审计日志（这里使用模拟数据）
        audit_logs = [
            {
                "log_id": 1,
                "user_id": 1,
                "username": "admin",
                "operation": "CREATE_USER",
                "resource_type": "user",
                "resource_id": 4,
                "details": "新增用户",
                "ip_address": "127.0.0.1",
                "created_at": "2026-03-30 10:00:00"
            },
            {
                "log_id": 2,
                "user_id": 1,
                "username": "admin",
                "operation": "SURVEY_SUBMIT",
                "resource_type": "survey",
                "resource_id": 1,
                "details": "提交调查数据",
                "ip_address": "127.0.0.1",
                "created_at": "2026-03-30 11:00:00"
            }
        ]
        
        if not audit_logs:
            raise HTTPException(status_code=404, detail="没有可导出的审计日志")
        
        # 导出数据
        output = export_service.export_audit_logs(audit_logs)
        filename = export_service.generate_filename("审计日志")
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="EXPORT_AUDIT_LOGS",
            resource_type="audit_log",
            resource_id=0,
            details={"count": len(audit_logs)},
            ip_address="127.0.0.1"
        )
        
        # 返回文件
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出审计日志失败: {str(e)}")


@router.get("/notifications", summary="导出通知列表")
async def export_notifications(
    format: str = Query("excel", description="导出格式：excel, csv"),
    current_user: dict = Depends(get_current_user)
):
    """
    导出通知列表
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能导出通知列表"
        )
    
    try:
        # 获取通知数据（这里使用模拟数据）
        notifications = [
            {
                "notification_id": 1,
                "title": "关于2026年第一季度数据填报的通知",
                "content": "请各企业在规定时间内完成数据填报",
                "notification_type": "deadline",
                "priority": "high",
                "sender_name": "系统管理员",
                "status": "published",
                "distribution_progress": 100,
                "created_at": "2026-03-01 10:00:00",
                "published_at": "2026-03-01 10:05:00"
            },
            {
                "notification_id": 2,
                "title": "关于系统维护的通知",
                "content": "系统将于本周六进行维护",
                "notification_type": "system",
                "priority": "medium",
                "sender_name": "系统管理员",
                "status": "published",
                "distribution_progress": 100,
                "created_at": "2026-03-15 14:00:00",
                "published_at": "2026-03-15 14:05:00"
            }
        ]
        
        if not notifications:
            raise HTTPException(status_code=404, detail="没有可导出的通知数据")
        
        # 导出数据
        output = export_service.export_notification_list(notifications)
        filename = export_service.generate_filename("通知列表")
        
        # 记录审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="EXPORT_NOTIFICATIONS",
            resource_type="notification",
            resource_id=0,
            details={"count": len(notifications)},
            ip_address="127.0.0.1"
        )
        
        # 返回文件
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出通知列表失败: {str(e)}")