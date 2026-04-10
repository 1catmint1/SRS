"""
角色管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from schemas.role_models import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RolePermission,
    UserRoleAssignment,
    UserRoleResponse,
    RoleQuery
)
from services.role_service import RoleService
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/roles", tags=["角色管理"])

# 初始化服务
role_db = {
    "roles": [],
    "users": USER_DATABASE
}

role_service = RoleService(role_db)
audit_logger = AuditLogger()

# 初始化默认角色
role_service.initialize_default_roles()


@router.get("/", summary="查询角色列表")
async def get_roles(
    role_name: Optional[str] = Query(None, description="角色名称"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    查询角色列表（支持分页和多条件过滤）
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看角色列表"
        )
    
    try:
        # 构建查询条件
        query = {
            "role_name": role_name,
            "is_active": is_active,
            "page": page,
            "page_size": page_size
        }
        
        # 查询角色
        result = role_service.get_roles(query)
        
        return {
            "status": "success",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询角色列表失败: {str(e)}")


@router.get("/{role_id}", summary="获取角色详情")
async def get_role(
    role_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色详细信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看角色详情"
        )
    
    try:
        role = role_service.get_role(role_id)
        
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return {
            "status": "success",
            "role": role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色详情失败: {str(e)}")


@router.post("/", summary="创建新角色")
async def create_role(
    role: RoleCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建新的角色
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能创建角色"
        )
    
    try:
        # 创建角色
        role_data = role.dict()
        new_role = role_service.create_role(role_data)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ROLE_CREATE",
            resource_type="role",
            resource_id=new_role["role_id"],
            details={"role_name": new_role["role_name"], "permissions": new_role["permissions"]},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": f"角色【{new_role['role_name']}】创建成功",
            "role": new_role
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建角色失败: {str(e)}")


@router.put("/{role_id}", summary="更新角色信息")
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新角色信息
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能更新角色"
        )
    
    try:
        # 获取旧角色信息
        old_role = role_service.get_role(role_id)
        if not old_role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 更新角色
        update_data = role_update.dict(exclude_unset=True)
        updated_role = role_service.update_role(role_id, update_data)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ROLE_UPDATE",
            resource_type="role",
            resource_id=role_id,
            details={"role_name": updated_role["role_name"], "updates": update_data},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": f"角色【{updated_role['role_name']}】更新成功",
            "role": updated_role
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新角色失败: {str(e)}")


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    force: bool = Query(False, description="强制删除（即使有用户使用该角色）"),
    current_user: dict = Depends(get_current_user)
):
    """
    删除角色
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能删除角色"
        )
    
    try:
        # 获取角色信息
        role = role_service.get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        role_name = role["role_name"]
        
        # 删除角色
        role_service.delete_role(role_id, force=force)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ROLE_DELETE",
            resource_type="role",
            resource_id=role_id,
            details={"role_name": role_name, "force": force},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": f"角色【{role_name}】删除成功"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除角色失败: {str(e)}")


@router.post("/assign", summary="为用户分配角色")
async def assign_role_to_user(
    assignment: UserRoleAssignment,
    current_user: dict = Depends(get_current_user)
):
    """
    为用户分配角色
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能分配角色"
        )
    
    try:
        # 分配角色
        role_service.assign_role_to_user(assignment.user_id, assignment.role_id)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ROLE_ASSIGN",
            resource_type="user",
            resource_id=assignment.user_id,
            details={"role_id": assignment.role_id},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "角色分配成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配角色失败: {str(e)}")


@router.post("/revoke/{user_id}", summary="撤销用户角色")
async def revoke_role_from_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    撤销用户角色
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能撤销角色"
        )
    
    try:
        # 撤销角色
        role_service.revoke_role_from_user(user_id)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ROLE_REVOKE",
            resource_type="user",
            resource_id=user_id,
            details={},
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "角色撤销成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤销角色失败: {str(e)}")


@router.get("/{role_id}/permissions", summary="获取角色权限列表")
async def get_role_permissions(
    role_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色的权限列表
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看角色权限"
        )
    
    try:
        permissions = role_service.get_role_permissions(role_id)
        
        return {
            "status": "success",
            "role_id": role_id,
            "permissions": permissions
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色权限失败: {str(e)}")


@router.get("/permissions/all", summary="获取所有可用权限")
async def get_all_permissions(
    current_user: dict = Depends(get_current_user)
):
    """
    获取系统中所有可用的权限
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看所有权限"
        )
    
    try:
        permissions = role_service.get_all_permissions()
        
        # 按权限分组
        grouped_permissions = {}
        for perm in permissions:
            group = perm["permission_group"]
            if group not in grouped_permissions:
                grouped_permissions[group] = []
            grouped_permissions[group].append(perm)
        
        return {
            "status": "success",
            "permissions": permissions,
            "grouped_permissions": grouped_permissions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取权限列表失败: {str(e)}")


@router.get("/users/{user_id}/permissions", summary="获取用户权限列表")
async def get_user_permissions(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户的所有权限
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能查看用户权限"
        )
    
    try:
        # 获取用户角色
        users = USER_DATABASE
        target_user = None
        
        for user in users.values():
            if user.get("user_id") == user_id:
                target_user = user
                break
        
        if not target_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        role_id = target_user.get("role_id")
        if not role_id:
            return {
                "status": "success",
                "user_id": user_id,
                "role_id": None,
                "role_name": None,
                "permissions": []
            }
        
        # 获取角色权限
        permissions = role_service.get_role_permissions(role_id)
        role = role_service.get_role(role_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role["role_name"] if role else None,
            "permissions": permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户权限失败: {str(e)}")