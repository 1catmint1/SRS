from datetime import datetime
from typing import Dict, Any, Optional
from db.mock_db import t_operation_log


class AuditLogger:
    """强制审计留痕记录器"""
    
    def __init__(self):
        self.log_table = t_operation_log
    
    def log_operation(
        self,
        user_id: int,
        operation_type: str,
        table_name: str,
        record_id: int,
        old_value: str,
        new_value: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        记录操作审计日志
        
        Args:
            user_id: 操作用户ID
            operation_type: 操作类型
            table_name: 操作的表名
            record_id: 记录ID
            old_value: 修改前的值
            new_value: 修改后的值
            reason: 操作原因
            ip_address: 客户端IP地址
            user_agent: 用户代理信息
        
        Returns:
            审计日志记录
        """
        log_entry = {
            "user_id": user_id,
            "operation_type": operation_type,
            "table_name": table_name,
            "record_id": record_id,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "log_id": len(self.log_table) + 1
        }
        
        self.log_table.append(log_entry)
        return log_entry
    
    def get_logs(
        self,
        user_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        table_name: Optional[str] = None,
        record_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        查询审计日志
        
        Args:
            user_id: 按用户ID筛选
            operation_type: 按操作类型筛选
            table_name: 按表名筛选
            record_id: 按记录ID筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回记录数量限制
        
        Returns:
            审计日志列表
        """
        logs = self.log_table.copy()
        
        # 按条件筛选
        if user_id:
            logs = [log for log in logs if log.get("user_id") == user_id]
        if operation_type:
            logs = [log for log in logs if log.get("operation_type") == operation_type]
        if table_name:
            logs = [log for log in logs if log.get("table_name") == table_name]
        if record_id:
            logs = [log for log in logs if log.get("record_id") == record_id]
        if start_date:
            logs = [log for log in logs if log.get("operation_time", "") >= start_date]
        if end_date:
            logs = [log for log in logs if log.get("operation_time", "") <= end_date]
        
        # 按时间倒序排列
        logs = sorted(logs, key=lambda x: x.get("operation_time", ""), reverse=True)
        
        return logs[:limit]
    
    def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """根据日志ID获取单条日志"""
        for log in self.log_table:
            if log.get("log_id") == log_id:
                return log
        return None


class DataProtection:
    """数据修改保护机制"""
    
    # 定义不可修改的字段
    PROTECTED_FIELDS = {
        "t_enterprise_info": ["enterprise_id"],  # 企业ID不可修改
        "t_survey_period": ["period_id"],        # 调查期ID不可修改
        "USER_DATABASE": ["user_id"]            # 用户ID不可修改
    }
    
    # 定义不可删除的记录
    PROTECTED_RECORDS = {
        "t_survey_period": lambda x: x.get("status") == "active",  # 活跃的调查期不可删除
    }
    
    # 定义需要特殊权限的操作
    SENSITIVE_OPERATIONS = {
        "DELETE_USER": "删除用户需要PRO_ADMIN权限",
        "DELETE_ACTIVE_PERIOD": "删除活跃调查期需要PRO_ADMIN权限",
        "MODIFY_PROTECTED_FIELD": "修改保护字段需要特殊权限"
    }
    
    @staticmethod
    def check_field_modification(table_name: str, field_name: str) -> bool:
        """
        检查字段是否可以修改
        
        Args:
            table_name: 表名
            field_name: 字段名
        
        Returns:
            True表示可以修改，False表示不可修改
        """
        protected_fields = DataProtection.PROTECTED_FIELDS.get(table_name, [])
        return field_name not in protected_fields
    
    @staticmethod
    def check_record_deletion(table_name: str, record_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        检查记录是否可以删除
        
        Args:
            table_name: 表名
            record_data: 记录数据
        
        Returns:
            (是否可以删除, 原因说明)
        """
        protection_rule = DataProtection.PROTECTED_RECORDS.get(table_name)
        if protection_rule and protection_rule(record_data):
            return False, f"该记录处于保护状态，不可删除"
        
        return True, ""
    
    @staticmethod
    def validate_data_change(
        table_name: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        user_role: str
    ) -> tuple[bool, str]:
        """
        验证数据变更的合法性
        
        Args:
            table_name: 表名
            old_data: 旧数据
            new_data: 新数据
            user_role: 用户角色
        
        Returns:
            (是否合法, 错误信息)
        """
        # 检查是否有被保护字段被修改
        for field_name in new_data:
            if not DataProtection.check_field_modification(table_name, field_name):
                if old_data.get(field_name) != new_data.get(field_name):
                    return False, f"字段【{field_name}】为保护字段，不可修改"
        
        # 检查敏感操作
        if "status" in new_data and new_data["status"] != old_data.get("status"):
            if table_name == "t_enterprise_info":
                # 企业状态变更需要特殊权限
                if user_role not in ["省级管理员"]:
                    return False, "企业状态变更需要省级管理员权限"
        
        return True, ""
    
    @staticmethod
    def check_data_integrity(table_name: str, record_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        检查数据完整性
        
        Args:
            table_name: 表名
            record_data: 记录数据
        
        Returns:
            (数据是否完整, 错误信息)
        """
        # 企业信息完整性检查
        if table_name == "t_enterprise_info":
            required_fields = ["enterprise_name", "filing_status"]
            for field in required_fields:
                if field not in record_data or record_data[field] is None:
                    return False, f"企业信息缺少必要字段: {field}"
            
            # 检查状态值是否合法
            valid_statuses = [0, 1, 2]  # 0:待备案, 1:已备案, 2:已退回
            if record_data.get("filing_status") not in valid_statuses:
                return False, f"企业状态值不合法: {record_data.get('filing_status')}"
        
        # 调查期完整性检查
        elif table_name == "t_survey_period":
            required_fields = ["period_name", "start_date", "end_date", "status"]
            for field in required_fields:
                if field not in record_data or record_data[field] is None:
                    return False, f"调查期信息缺少必要字段: {field}"
            
            # 检查状态值是否合法
            valid_statuses = ["active", "closed", "pending"]
            if record_data.get("status") not in valid_statuses:
                return False, f"调查期状态值不合法: {record_data.get('status')}"
        
        return True, ""


# 创建全局审计记录器实例
audit_logger = AuditLogger()

# 创建全局数据保护实例
data_protection = DataProtection()