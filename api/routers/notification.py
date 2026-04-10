"""
通知发布与三级分发流转API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from schemas.notification_models import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationDistribution,
    NotificationDistributionStats,
    NotificationQuery,
    UserNotification,
    NotificationMarkRead
)
from services.notification_service import NotificationService
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/notification", tags=["通知发布与三级分发流转"])

# 初始化数据库和服务
notification_db = {
    "notifications": {},
    "distributions": [],
    "users": USER_DATABASE,
    "enterprises": {}
}

notification_service = NotificationService(notification_db)
audit_logger = AuditLogger()


@router.post("/create", summary="创建通知")
async def create_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建新通知（草稿状态）
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能创建通知"
        )
    
    try:
        # 创建通知
        notification_data = notification.dict()
        notification_data["sender_id"] = current_user["user_id"]
        notification_data["sender_name"] = current_user.get("full_name", current_user["username"])
        notification_data["sender_role"] = current_user["role_name"]
        
        notification = notification_service.create_notification(notification_data)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NOTIFICATION_CREATE",
            resource_type="notification",
            resource_id=notification["notification_id"],
            details={"title": notification["title"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "通知创建成功",
            "notification": notification
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建通知失败: {str(e)}")


@router.post("/{notification_id}/publish", summary="发布通知")
async def publish_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    发布通知并开始三级分发流转
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能发布通知"
        )
    
    try:
        # 发布通知
        notification = notification_service.publish_notification(notification_id)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NOTIFICATION_PUBLISH",
            resource_type="notification",
            resource_id=notification_id,
            details={"title": notification["title"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "通知发布成功，三级分发已启动",
            "notification": notification
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布通知失败: {str(e)}")


@router.get("/{notification_id}", summary="获取通知详情")
async def get_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取通知详细信息"""
    try:
        notification = notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        # 获取分发统计
        stats = notification_service.get_distribution_stats(notification_id)
        
        return {
            "status": "success",
            "notification": notification,
            "distribution_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通知失败: {str(e)}")


@router.get("/", summary="查询通知列表")
async def get_notifications(
    status: Optional[str] = Query(None, description="通知状态"),
    notification_type: Optional[str] = Query(None, description="通知类型"),
    priority: Optional[str] = Query(None, description="优先级"),
    sender_id: Optional[int] = Query(None, description="发送者ID"),
    keyword: Optional[str] = Query(None, description="关键词"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    查询通知列表（支持分页和多条件过滤）
    
    权限要求：登录用户
    """
    try:
        # 构建查询条件
        query = {
            "status": status,
            "notification_type": notification_type,
            "priority": priority,
            "sender_id": sender_id,
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        
        # 处理日期
        if start_date:
            query["start_date"] = datetime.fromisoformat(start_date)
        if end_date:
            query["end_date"] = datetime.fromisoformat(end_date)
        
        # 查询通知
        result = notification_service.get_notifications(query)
        
        return {
            "status": "success",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询通知失败: {str(e)}")


@router.get("/{notification_id}/distributions", summary="获取通知分发列表")
async def get_notification_distributions(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取通知的分发记录列表
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看分发记录"
        )
    
    try:
        # 获取通知的分发记录
        distributions = [
            d for d in notification_db["distributions"]
            if d["notification_id"] == notification_id
        ]
        
        return {
            "status": "success",
            "notification_id": notification_id,
            "total": len(distributions),
            "distributions": distributions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分发记录失败: {str(e)}")


@router.get("/{notification_id}/stats", summary="获取通知分发统计")
async def get_notification_stats(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取通知的分发统计信息
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看统计信息"
        )
    
    try:
        stats = notification_service.get_distribution_stats(notification_id)
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/user/my-notifications", summary="获取我的通知")
async def get_my_notifications(
    unread_only: bool = Query(False, description="只显示未读通知"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的未读通知列表
    
    权限要求：登录用户
    """
    try:
        user_id = current_user["user_id"]
        user_role = current_user["role_name"]
        
        # 获取用户通知
        notifications = notification_service.get_user_notifications(user_id, user_role)
        
        # 过滤未读通知
        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]
        
        return {
            "status": "success",
            "total": len(notifications),
            "unread_count": len([n for n in notifications if not n["is_read"]]),
            "notifications": notifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通知失败: {str(e)}")


@router.post("/mark-read", summary="标记通知已读")
async def mark_notification_read(
    mark_data: NotificationMarkRead,
    current_user: dict = Depends(get_current_user)
):
    """
    标记通知为已读
    
    权限要求：登录用户
    """
    try:
        user_id = current_user["user_id"]
        
        if mark_data.mark_all:
            # 标记所有通知为已读
            user_role = current_user["role_name"]
            notifications = notification_service.get_user_notifications(user_id, user_role)
            
            for notification in notifications:
                if not notification["is_read"]:
                    notification_service.mark_notification_read(
                        user_id, notification["notification_id"]
                    )
            
            return {
                "status": "success",
                "message": f"已标记{len(notifications)}条通知为已读"
            }
        else:
            # 标记指定通知为已读
            for notification_id in mark_data.notification_ids:
                notification_service.mark_notification_read(user_id, notification_id)
            
            return {
                "status": "success",
                "message": f"已标记{len(mark_data.notification_ids)}条通知为已读"
            }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标记通知失败: {str(e)}")


@router.put("/{notification_id}", summary="更新通知")
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新通知信息（只能更新草稿状态的通知）
    
    权限要求：通知创建者
    """
    try:
        notification = notification_service.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        # 权限检查
        if notification["sender_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="只有通知创建者才能更新通知"
            )
        
        # 只能更新草稿状态的通知
        if notification["status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail="只能更新草稿状态的通知"
            )
        
        # 更新通知
        update_data = notification_update.dict(exclude_unset=True)
        notification.update(update_data)
        notification["updated_at"] = datetime.now()
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NOTIFICATION_UPDATE",
            resource_type="notification",
            resource_id=notification_id,
            details={"title": notification["title"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "通知更新成功",
            "notification": notification
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新通知失败: {str(e)}")


@router.post("/{notification_id}/cancel", summary="取消通知")
async def cancel_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    取消已发布的通知
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能取消通知"
        )
    
    try:
        notification = notification_service.cancel_notification(notification_id)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="NOTIFICATION_CANCEL",
            resource_type="notification",
            resource_id=notification_id,
            details={"title": notification["title"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "通知已取消",
            "notification": notification
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消通知失败: {str(e)}")