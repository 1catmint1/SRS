"""
角色管理服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class RoleService:
    """角色管理服务类"""
    
    def __init__(self, db):
        self.db = db
    
    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新角色"""
        # 检查角色名是否已存在
        for role in self.db.get("roles", []):
            if role["role_name"] == role_data["role_name"]:
                raise ValueError("角色名称已存在")
        
        # 生成角色ID
        role_id = self._generate_role_id()
        
        # 创建角色
        role = {
            "role_id": role_id,
            "role_name": role_data["role_name"],
            "role_description": role_data["role_description"],
            "permissions": role_data["permissions"],
            "is_active": role_data.get("is_active", True),
            "user_count": 0,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        self.db.setdefault("roles", []).append(role)
        
        return role
    
    def get_role(self, role_id: int) -> Optional[Dict[str, Any]]:
        """获取角色详情"""
        for role in self.db.get("roles", []):
            if role["role_id"] == role_id:
                return role
        return None
    
    def get_roles(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """查询角色列表"""
        roles = self.db.get("roles", [])
        
        # 过滤条件
        if query.get("role_name"):
            roles = [r for r in roles if query["role_name"].lower() in r["role_name"].lower()]
        
        if query.get("is_active") is not None:
            roles = [r for r in roles if r["is_active"] == query["is_active"]]
        
        # 排序（按创建时间倒序）
        roles.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 分页
        page = query.get("page", 1)
        page_size = query.get("page_size", 20)
        start = (page - 1) * page_size
        end = start + page_size
        
        total = len(roles)
        page_data = roles[start:end]
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "roles": page_data
        }
    
    def update_role(self, role_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新角色信息"""
        role = self.get_role(role_id)
        if not role:
            raise ValueError("角色不存在")
        
        # 更新字段
        if "role_name" in update_data:
            # 检查新名称是否与其他角色冲突
            for r in self.db.get("roles", []):
                if r["role_id"] != role_id and r["role_name"] == update_data["role_name"]:
                    raise ValueError("角色名称已存在")
            role["role_name"] = update_data["role_name"]
        
        if "role_description" in update_data:
            role["role_description"] = update_data["role_description"]
        
        if "permissions" in update_data:
            role["permissions"] = update_data["permissions"]
        
        if "is_active" in update_data:
            role["is_active"] = update_data["is_active"]
        
        role["updated_at"] = datetime.now()
        
        return role
    
    def delete_role(self, role_id: int, force: bool = False) -> bool:
        """删除角色"""
        roles = self.db.get("roles", [])
        role_index = None
        
        for idx, role in enumerate(roles):
            if role["role_id"] == role_id:
                role_index = idx
                break
        
        if role_index is None:
            raise ValueError("角色不存在")
        
        role = roles[role_index]
        
        # 检查是否有用户使用该角色
        if role["user_count"] > 0 and not force:
            raise ValueError(f"该角色被{role['user_count']}个用户使用，无法删除")
        
        # 删除角色
        del roles[role_index]
        
        # 清理用户角色关联
        if force:
            self._clear_user_roles(role_id)
        
        return True
    
    def _clear_user_roles(self, role_id: int):
        """清理用户角色关联"""
        users = self.db.get("users", {})
        for username, user in users.items():
            if user.get("role_id") == role_id:
                # 重置为默认角色或禁用用户
                user["role_id"] = None
                user["is_active"] = False
    
    def assign_role_to_user(self, user_id: int, role_id: int) -> bool:
        """为用户分配角色"""
        # 检查角色是否存在
        role = self.get_role(role_id)
        if not role:
            raise ValueError("角色不存在")
        
        if not role["is_active"]:
            raise ValueError("角色已禁用")
        
        # 查找用户
        users = self.db.get("users", {})
        target_user = None
        target_username = None
        
        for username, user in users.items():
            if user.get("user_id") == user_id:
                target_user = user
                target_username = username
                break
        
        if not target_user:
            raise ValueError("用户不存在")
        
        # 更新旧角色的用户计数
        old_role_id = target_user.get("role_id")
        if old_role_id:
            old_role = self.get_role(old_role_id)
            if old_role and old_role["user_count"] > 0:
                old_role["user_count"] -= 1
        
        # 分配新角色
        target_user["role_id"] = role_id
        target_user["role_name"] = role["role_name"]
        
        # 更新新角色的用户计数
        role["user_count"] += 1
        
        return True
    
    def revoke_role_from_user(self, user_id: int) -> bool:
        """撤销用户角色"""
        users = self.db.get("users", {})
        target_user = None
        
        for username, user in users.items():
            if user.get("user_id") == user_id:
                target_user = user
                break
        
        if not target_user:
            raise ValueError("用户不存在")
        
        # 更新旧角色的用户计数
        old_role_id = target_user.get("role_id")
        if old_role_id:
            old_role = self.get_role(old_role_id)
            if old_role and old_role["user_count"] > 0:
                old_role["user_count"] -= 1
        
        # 撤销角色
        target_user["role_id"] = None
        target_user["role_name"] = None
        target_user["is_active"] = False
        
        return True
    
    def get_role_permissions(self, role_id: int) -> List[str]:
        """获取角色权限列表"""
        role = self.get_role(role_id)
        if not role:
            raise ValueError("角色不存在")
        
        return role.get("permissions", [])
    
    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否拥有指定权限"""
        users = self.db.get("users", {})
        
        for user in users.values():
            if user.get("user_id") == user_id:
                role_id = user.get("role_id")
                if not role_id:
                    return False
                
                role = self.get_role(role_id)
                if not role or not role["is_active"]:
                    return False
                
                return permission in role.get("permissions", [])
        
        return False
    
    def get_all_permissions(self) -> List[Dict[str, Any]]:
        """获取所有可用权限"""
        permissions = [
            # 用户管理权限
            {
                "permission_id": "user_read",
                "permission_name": "查看用户",
                "permission_description": "查看用户列表和详情",
                "permission_group": "用户管理",
                "level": "read"
            },
            {
                "permission_id": "user_create",
                "permission_name": "创建用户",
                "permission_description": "创建新用户",
                "permission_group": "用户管理",
                "level": "write"
            },
            {
                "permission_id": "user_update",
                "permission_name": "修改用户",
                "permission_description": "修改用户信息",
                "permission_group": "用户管理",
                "level": "write"
            },
            {
                "permission_id": "user_delete",
                "permission_name": "删除用户",
                "permission_description": "删除用户",
                "permission_group": "用户管理",
                "level": "delete"
            },
            # 角色管理权限
            {
                "permission_id": "role_read",
                "permission_name": "查看角色",
                "permission_description": "查看角色列表和详情",
                "permission_group": "角色管理",
                "level": "read"
            },
            {
                "permission_id": "role_create",
                "permission_name": "创建角色",
                "permission_description": "创建新角色",
                "permission_group": "角色管理",
                "level": "write"
            },
            {
                "permission_id": "role_update",
                "permission_name": "修改角色",
                "permission_description": "修改角色信息和权限",
                "permission_group": "角色管理",
                "level": "write"
            },
            {
                "permission_id": "role_delete",
                "permission_name": "删除角色",
                "permission_description": "删除角色",
                "permission_group": "角色管理",
                "level": "delete"
            },
            # 企业管理权限
            {
                "permission_id": "enterprise_read",
                "permission_name": "查看企业",
                "permission_description": "查看企业列表和详情",
                "permission_group": "企业管理",
                "level": "read"
            },
            {
                "permission_id": "enterprise_audit",
                "permission_name": "企业审批",
                "permission_description": "审批企业备案和数据",
                "permission_group": "企业管理",
                "level": "write"
            },
            {
                "permission_id": "enterprise_modify",
                "permission_name": "修改企业数据",
                "permission_description": "修改企业上报数据",
                "permission_group": "企业管理",
                "level": "write"
            },
            {
                "permission_id": "enterprise_delete",
                "permission_name": "删除企业数据",
                "permission_description": "删除企业数据",
                "permission_group": "企业管理",
                "level": "delete"
            },
            # 数据填报权限
            {
                "permission_id": "data_submit",
                "permission_name": "数据填报",
                "permission_description": "填报企业数据",
                "permission_group": "数据填报",
                "level": "write"
            },
            {
                "permission_id": "data_query",
                "permission_name": "数据查询",
                "permission_description": "查询企业数据",
                "permission_group": "数据填报",
                "level": "read"
            },
            # 数据分析权限
            {
                "permission_id": "analysis_read",
                "permission_name": "查看分析",
                "permission_description": "查看数据分析和统计",
                "permission_group": "数据分析",
                "level": "read"
            },
            {
                "permission_id": "analysis_export",
                "permission_name": "导出数据",
                "permission_description": "导出数据到Excel",
                "permission_group": "数据分析",
                "level": "write"
            },
            # 系统管理权限
            {
                "permission_id": "system_config",
                "permission_name": "系统配置",
                "permission_description": "配置系统参数",
                "permission_group": "系统管理",
                "level": "admin"
            },
            {
                "permission_id": "system_monitor",
                "permission_name": "系统监控",
                "permission_description": "监控系统运行状态",
                "permission_group": "系统管理",
                "level": "read"
            },
            {
                "permission_id": "notification_manage",
                "permission_name": "通知管理",
                "permission_description": "发布和管理通知",
                "permission_group": "系统管理",
                "level": "write"
            },
            {
                "permission_id": "audit_log_read",
                "permission_name": "查看审计日志",
                "permission_description": "查看操作审计日志",
                "permission_group": "系统管理",
                "level": "read"
            }
        ]
        
        return permissions
    
    def initialize_default_roles(self):
        """初始化默认角色"""
        # 检查是否已初始化
        if self.db.get("roles"):
            return
        
        # 省级管理员角色
        admin_permissions = [
            "user_read", "user_create", "user_update", "user_delete",
            "role_read", "role_create", "role_update", "role_delete",
            "enterprise_read", "enterprise_audit", "enterprise_modify", "enterprise_delete",
            "analysis_read", "analysis_export",
            "system_config", "system_monitor", "notification_manage", "audit_log_read"
        ]
        
        self.create_role({
            "role_name": "省级管理员",
            "role_description": "拥有系统所有权限，可以管理所有功能和数据",
            "permissions": admin_permissions,
            "is_active": True
        })
        
        # 市级审核员角色
        city_admin_permissions = [
            "enterprise_read", "enterprise_audit",
            "analysis_read", "analysis_export",
            "notification_manage"
        ]
        
        self.create_role({
            "role_name": "市级审核员",
            "role_description": "负责企业数据审核，可以查看和导出数据",
            "permissions": city_admin_permissions,
            "is_active": True
        })
        
        # 企业用户角色
        enterprise_permissions = [
            "data_submit", "data_query"
        ]
        
        self.create_role({
            "role_name": "企业用户",
            "role_description": "负责企业数据填报和查询",
            "permissions": enterprise_permissions,
            "is_active": True
        })
    
    def _generate_role_id(self) -> int:
        """生成角色ID"""
        roles = self.db.get("roles", [])
        if not roles:
            return 1
        return max(r["role_id"] for r in roles) + 1