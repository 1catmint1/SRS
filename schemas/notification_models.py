"""
通知数据模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime


class NotificationBase(BaseModel):
    """通知基础模型"""
    title: str = Field(..., description="通知标题", max_length=200)
    content: str = Field(..., description="通知内容")
    notification_type: Literal["system", "deadline", "warning", "info"] = Field(
        ..., description="通知类型：system-系统通知, deadline-截止提醒, warning-警告通知, info-信息通知"
    )
    priority: Literal["high", "medium", "low"] = Field(
        "medium", description="优先级：high-高, medium-中, low-低"
    )
    target_audience: Literal["all", "province", "city", "enterprise"] = Field(
        "all", description="目标受众：all-全部, province-省级, city-市级, enterprise-企业"
    )
    dead_line: Optional[datetime] = Field(None, description="截止时间")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('通知标题不能为空')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('通知内容不能为空')
        return v.strip()


class NotificationCreate(NotificationBase):
    """创建通知模型"""
    sender_id: int = Field(..., description="发送者用户ID")
    sender_name: str = Field(..., description="发送者姓名")
    sender_role: str = Field(..., description="发送者角色")


class NotificationUpdate(BaseModel):
    """更新通知模型"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    notification_type: Optional[Literal["system", "deadline", "warning", "info"]] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    status: Optional[Literal["draft", "published", "cancelled"]] = None


class NotificationResponse(NotificationBase):
    """通知响应模型"""
    notification_id: int
    sender_id: int
    sender_name: str
    sender_role: str
    status: Literal["draft", "published", "cancelled"]
    distribution_status: Literal["pending", "distributing", "completed", "failed"]
    distribution_progress: int = Field(..., description="分发进度 0-100")
    created_at: datetime
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationDistribution(BaseModel):
    """通知分发记录模型"""
    distribution_id: int
    notification_id: int
    target_id: int = Field(..., description="目标ID（城市ID或企业ID）")
    target_name: str = Field(..., description="目标名称")
    target_type: Literal["city", "enterprise"] = Field(..., description="目标类型")
    target_level: Literal["province", "city", "enterprise"] = Field(..., description="目标层级")
    status: Literal["pending", "sent", "read", "failed"] = Field(..., description="分发状态")
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    read_count: int = Field(0, description="阅读次数")
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class NotificationDistributionStats(BaseModel):
    """通知分发统计模型"""
    notification_id: int
    total_targets: int
    distributed: int
    read: int
    failed: int
    read_rate: float = Field(..., description="阅读率")
    distribution_rate: float = Field(..., description="分发率")


class NotificationQuery(BaseModel):
    """通知查询模型"""
    status: Optional[Literal["draft", "published", "cancelled"]] = None
    notification_type: Optional[Literal["system", "deadline", "warning", "info"]] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    sender_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UserNotification(BaseModel):
    """用户通知模型"""
    notification_id: int
    user_id: int
    title: str
    content: str
    notification_type: Literal["system", "deadline", "warning", "info"]
    priority: Literal["high", "medium", "low"]
    is_read: bool = Field(False, description="是否已读")
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """标记通知已读模型"""
    notification_ids: List[int] = Field(..., description="通知ID列表")
    mark_all: bool = Field(False, description="是否标记全部已读")