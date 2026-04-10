"""
通知发布与三级分发流转服务
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class DistributionLevel(Enum):
    """分发层级"""
    PROVINCE = "province"
    CITY = "city"
    ENTERPRISE = "enterprise"


class DistributionStatus(Enum):
    """分发状态"""
    PENDING = "pending"
    DISTRIBUTING = "distributing"
    COMPLETED = "completed"
    FAILED = "failed"


class NotificationService:
    """通知服务类"""
    
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建通知"""
        notification_id = self._generate_notification_id()
        
        notification = {
            "notification_id": notification_id,
            "title": notification_data["title"],
            "content": notification_data["content"],
            "notification_type": notification_data["notification_type"],
            "priority": notification_data["priority"],
            "target_audience": notification_data["target_audience"],
            "sender_id": notification_data["sender_id"],
            "sender_name": notification_data["sender_name"],
            "sender_role": notification_data["sender_role"],
            "status": "draft",
            "distribution_status": "pending",
            "distribution_progress": 0,
            "created_at": datetime.now(),
            "published_at": None,
            "updated_at": None,
            "deadline": notification_data.get("dead_line")
        }
        
        self.db["notifications"][notification_id] = notification
        return notification
    
    def publish_notification(self, notification_id: int) -> Dict[str, Any]:
        """发布通知并开始三级分发"""
        notification = self.db["notifications"].get(notification_id)
        if not notification:
            raise ValueError("通知不存在")
        
        if notification["status"] != "draft":
            raise ValueError("只能发布草稿状态的通知")
        
        # 更新通知状态
        notification["status"] = "published"
        notification["published_at"] = datetime.now()
        notification["updated_at"] = datetime.now()
        notification["distribution_status"] = "distributing"
        
        # 开始三级分发
        self._start_three_level_distribution(notification_id)
        
        return notification
    
    def _start_three_level_distribution(self, notification_id: int):
        """开始三级分发流转"""
        notification = self.db["notifications"][notification_id]
        target_audience = notification["target_audience"]
        
        # 确定分发目标
        targets = self._get_distribution_targets(target_audience)
        
        # 创建分发记录
        total_targets = len(targets)
        distributed_count = 0
        
        for target in targets:
            distribution_record = {
                "distribution_id": self._generate_distribution_id(),
                "notification_id": notification_id,
                "target_id": target["target_id"],
                "target_name": target["target_name"],
                "target_type": target["target_type"],
                "target_level": target["target_level"],
                "status": "pending",
                "sent_at": None,
                "read_at": None,
                "read_count": 0,
                "error_message": None
            }
            
            self.db["distributions"].append(distribution_record)
            
            # 模拟分发过程
            try:
                self._send_to_target(distribution_record)
                distributed_count += 1
                
                # 更新分发进度
                progress = int((distributed_count / total_targets) * 100)
                notification["distribution_progress"] = progress
                
            except Exception as e:
                distribution_record["status"] = "failed"
                distribution_record["error_message"] = str(e)
        
        # 更新分发状态
        if distributed_count == total_targets:
            notification["distribution_status"] = "completed"
        elif distributed_count > 0:
            notification["distribution_status"] = "completed"
        else:
            notification["distribution_status"] = "failed"
        
        notification["updated_at"] = datetime.now()
    
    def _get_distribution_targets(self, target_audience: str) -> List[Dict[str, Any]]:
        """获取分发目标列表"""
        targets = []
        
        if target_audience == "all":
            # 分发给所有级别的用户
            targets.extend(self._get_province_targets())
            targets.extend(self._get_city_targets())
            targets.extend(self._get_enterprise_targets())
        elif target_audience == "province":
            targets.extend(self._get_province_targets())
        elif target_audience == "city":
            targets.extend(self._get_city_targets())
        elif target_audience == "enterprise":
            targets.extend(self._get_enterprise_targets())
        
        return targets
    
    def _get_province_targets(self) -> List[Dict[str, Any]]:
        """获取省级目标"""
        # 从用户数据库中获取省级管理员
        targets = []
        for username, user in self.db.get("users", {}).items():
            if user.get("role_id") == 1:  # 省级管理员
                targets.append({
                    "target_id": user["user_id"],
                    "target_name": user.get("full_name", user["username"]),
                    "target_type": "province",
                    "target_level": "province"
                })
        return targets
    
    def _get_city_targets(self) -> List[Dict[str, Any]]:
        """获取市级目标"""
        targets = []
        # 假设我们有城市列表
        cities = [
            {"city_id": 101, "city_name": "昆明市"},
            {"city_id": 102, "city_name": "大理州"},
            {"city_id": 103, "city_name": "曲靖市"},
            {"city_id": 104, "city_name": "玉溪市"},
            {"city_id": 105, "city_name": "保山市"}
        ]
        
        for city in cities:
            targets.append({
                "target_id": city["city_id"],
                "target_name": city["city_name"],
                "target_type": "city",
                "target_level": "city"
            })
        
        return targets
    
    def _get_enterprise_targets(self) -> List[Dict[str, Any]]:
        """获取企业目标"""
        targets = []
        # 从企业信息表中获取企业
        for enterprise_id, enterprise_info in self.db.get("enterprises", {}).items():
            targets.append({
                "target_id": enterprise_id,
                "target_name": enterprise_info.get("enterprise_name", f"企业{enterprise_id}"),
                "target_type": "enterprise",
                "target_level": "enterprise"
            })
        
        return targets
    
    def _send_to_target(self, distribution_record: Dict[str, Any]):
        """发送通知到目标"""
        # 模拟发送过程
        distribution_record["status"] = "sent"
        distribution_record["sent_at"] = datetime.now()
        
        # 在实际应用中，这里会调用消息推送服务
        # 例如：WebSocket推送、短信、邮件等
        pass
    
    def get_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """获取通知详情"""
        return self.db["notifications"].get(notification_id)
    
    def get_notifications(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """查询通知列表"""
        notifications = list(self.db["notifications"].values())
        
        # 过滤条件
        if query.get("status"):
            notifications = [n for n in notifications if n["status"] == query["status"]]
        if query.get("notification_type"):
            notifications = [n for n in notifications if n["notification_type"] == query["notification_type"]]
        if query.get("priority"):
            notifications = [n for n in notifications if n["priority"] == query["priority"]]
        if query.get("sender_id"):
            notifications = [n for n in notifications if n["sender_id"] == query["sender_id"]]
        if query.get("keyword"):
            keyword = query["keyword"].lower()
            notifications = [
                n for n in notifications 
                if keyword in n["title"].lower() or keyword in n["content"].lower()
            ]
        
        # 时间范围过滤
        if query.get("start_date"):
            notifications = [n for n in notifications if n["created_at"] >= query["start_date"]]
        if query.get("end_date"):
            notifications = [n for n in notifications if n["created_at"] <= query["end_date"]]
        
        # 排序（按创建时间倒序）
        notifications.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 分页
        page = query.get("page", 1)
        page_size = query.get("page_size", 20)
        start = (page - 1) * page_size
        end = start + page_size
        
        total = len(notifications)
        page_data = notifications[start:end]
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "notifications": page_data
        }
    
    def get_distribution_stats(self, notification_id: int) -> Dict[str, Any]:
        """获取分发统计信息"""
        distributions = [
            d for d in self.db["distributions"]
            if d["notification_id"] == notification_id
        ]
        
        total = len(distributions)
        distributed = len([d for d in distributions if d["status"] in ["sent", "read"]])
        read = len([d for d in distributions if d["status"] == "read"])
        failed = len([d for d in distributions if d["status"] == "failed"])
        
        read_rate = (read / total * 100) if total > 0 else 0
        distribution_rate = (distributed / total * 100) if total > 0 else 0
        
        return {
            "notification_id": notification_id,
            "total_targets": total,
            "distributed": distributed,
            "read": read,
            "failed": failed,
            "read_rate": round(read_rate, 2),
            "distribution_rate": round(distribution_rate, 2)
        }
    
    def get_user_notifications(self, user_id: int, user_role: str) -> List[Dict[str, Any]]:
        """获取用户的通知列表"""
        # 根据用户角色确定可以接收的通知
        user_notifications = []
        
        for notification in self.db["notifications"].values():
            if notification["status"] != "published":
                continue
            
            # 检查通知是否针对该用户
            if self._is_notification_for_user(notification, user_id, user_role):
                # 查找该用户是否已读
                distribution = self._get_user_distribution(notification["notification_id"], user_id)
                
                user_notification = {
                    "notification_id": notification["notification_id"],
                    "user_id": user_id,
                    "title": notification["title"],
                    "content": notification["content"],
                    "notification_type": notification["notification_type"],
                    "priority": notification["priority"],
                    "is_read": distribution["status"] == "read" if distribution else False,
                    "read_at": distribution.get("read_at") if distribution else None,
                    "created_at": notification["created_at"]
                }
                
                user_notifications.append(user_notification)
        
        # 按创建时间倒序排序
        user_notifications.sort(key=lambda x: x["created_at"], reverse=True)
        
        return user_notifications
    
    def _is_notification_for_user(self, notification: Dict[str, Any], user_id: int, user_role: str) -> bool:
        """判断通知是否针对该用户"""
        target_audience = notification["target_audience"]
        
        if target_audience == "all":
            return True
        elif target_audience == "province" and user_role == "省级管理员":
            return True
        elif target_audience == "city" and user_role == "市级审核员":
            return True
        elif target_audience == "enterprise" and user_role == "企业用户":
            return True
        
        return False
    
    def _get_user_distribution(self, notification_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户的分发记录"""
        for distribution in self.db["distributions"]:
            if distribution["notification_id"] == notification_id and distribution["target_id"] == user_id:
                return distribution
        return None
    
    def mark_notification_read(self, user_id: int, notification_id: int):
        """标记通知为已读"""
        for distribution in self.db["distributions"]:
            if distribution["notification_id"] == notification_id and distribution["target_id"] == user_id:
                if distribution["status"] != "read":
                    distribution["status"] = "read"
                    distribution["read_at"] = datetime.now()
                    distribution["read_count"] += 1
                return
        
        raise ValueError("未找到对应的通知分发记录")
    
    def cancel_notification(self, notification_id: int) -> Dict[str, Any]:
        """取消通知"""
        notification = self.db["notifications"].get(notification_id)
        if not notification:
            raise ValueError("通知不存在")
        
        if notification["status"] != "published":
            raise ValueError("只能取消已发布的通知")
        
        notification["status"] = "cancelled"
        notification["updated_at"] = datetime.now()
        
        return notification
    
    def _generate_notification_id(self) -> int:
        """生成通知ID"""
        if not self.db["notifications"]:
            return 1
        return max(self.db["notifications"].keys()) + 1
    
    def _generate_distribution_id(self) -> int:
        """生成分发ID"""
        if not self.db["distributions"]:
            return 1
        return max(d["distribution_id"] for d in self.db["distributions"]) + 1