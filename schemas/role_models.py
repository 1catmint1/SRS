"""
角色管理数据模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PermissionLevel(str, Enum):
    """权限级别"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class RoleCreate(BaseModel):
    """创建角色模型"""
    role_name: str = Field(..., description="角色名称", min_length=1, max_length=50)
    role_description: str = Field(..., description="角色描述", max_length=200)
    permissions: List[str] = Field(..., description="权限列表")
    is_active: bool = Field(True, description="是否启用")
    
    @validator('role_name')
    def validate_role_name(cls, v):
        if not v or not v.strip():
            raise ValueError('角色名称不能为空')
        return v.strip()
    
    @validator('permissions')
    def validate_permissions(cls, v):
        if not v:
            raise ValueError('权限列表不能为空')
        return v


class RoleUpdate(BaseModel):
    """更新角色模型"""
    role_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role_description: Optional[str] = Field(None, max_length=200)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    """角色响应模型"""
    role_id: int
    role_name: str
    role_description: str
    permissions: List[str]
    user_count: int = Field(0, description="使用该角色的用户数量")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RolePermission(BaseModel):
    """角色权限模型"""
    permission_id: str = Field(..., description="权限ID")
    permission_name: str = Field(..., description="权限名称")
    permission_description: str = Field(..., description="权限描述")
    permission_group: str = Field(..., description="权限分组")
    level: str = Field(..., description="权限级别")


class UserRoleAssignment(BaseModel):
    """用户角色分配模型"""
    user_id: int
    role_id: int


class UserRoleResponse(BaseModel):
    """用户角色响应模型"""
    user_id: int
    username: str
    full_name: Optional[str] = None
    role_id: int
    role_name: str
    role_description: Optional[str] = None
    assigned_at: datetime
    
    class Config:
        from_attributes = True


class RoleQuery(BaseModel):
    """角色查询模型"""
    role_name: Optional[str] = Field(None, description="角色名称")
    is_active: Optional[bool] = Field(None, description="是否启用")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)