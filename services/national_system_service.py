"""
国家失业监测系统对接服务
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import httpx
import json
from enum import Enum


class NationalSystemStatus(Enum):
    """国家系统状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class SyncStatus(Enum):
    """同步状态"""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"


class NationalSystemConfig:
    """国家系统配置"""
    
    def __init__(self):
        self.base_url = "https://api.national-employment-monitoring.gov.cn/v1"  # 模拟的国家系统API
        self.api_key = "YOUR_API_KEY"  # 实际使用时从配置文件读取
        self.secret_key = "YOUR_SECRET_KEY"  # 实际使用时从配置文件读取
        self.timeout = 30  # 超时时间（秒）
        self.retry_times = 3  # 重试次数
        self.retry_delay = 1  # 重试延迟（秒）


class NationalSystemService:
    """国家失业监测系统对接服务"""
    
    def __init__(self, config: NationalSystemConfig = None):
        self.config = config or NationalSystemConfig()
        self.client = httpx.Client(timeout=self.config.timeout)
    
    def check_system_status(self) -> Dict[str, Any]:
        """检查国家系统状态"""
        try:
            # 模拟检查系统状态
            response = {
                "status": NationalSystemStatus.ONLINE.value,
                "message": "系统正常运行",
                "last_updated": datetime.now().isoformat(),
                "version": "v1.2.0"
            }
            return response
        except Exception as e:
            return {
                "status": NationalSystemStatus.ERROR.value,
                "message": f"系统状态检查失败: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }
    
    def authenticate(self) -> Dict[str, Any]:
        """认证获取访问令牌"""
        try:
            # 模拟认证过程
            # 实际应用中应该调用国家系统的认证接口
            token_data = {
                "access_token": "mock_access_token_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "token_type": "Bearer",
                "expires_in": 7200,  # 2小时
                "refresh_token": "mock_refresh_token"
            }
            return {
                "success": True,
                "data": token_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"认证失败: {str(e)}"
            }
    
    def sync_employment_data(
        self,
        survey_period_id: int,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """同步就业数据到国家系统"""
        sync_record = {
            "sync_id": self._generate_sync_id(),
            "survey_period_id": survey_period_id,
            "status": SyncStatus.SYNCING.value,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_records": len(data),
            "success_records": 0,
            "failed_records": 0,
            "error_message": None,
            "response_data": None
        }
        
        try:
            # 获取访问令牌
            auth_result = self.authenticate()
            if not auth_result["success"]:
                sync_record["status"] = SyncStatus.FAILED.value
                sync_record["error_message"] = "认证失败"
                return sync_record
            
            # 准备数据
            formatted_data = self._format_data_for_national_system(data)
            
            # 模拟同步数据
            # 实际应用中应该调用国家系统的数据同步接口
            success_count = len(formatted_data)
            failed_count = 0
            
            sync_record["status"] = SyncStatus.SUCCESS.value
            sync_record["end_time"] = datetime.now().isoformat()
            sync_record["success_records"] = success_count
            sync_record["failed_records"] = failed_count
            sync_record["response_data"] = {
                "batch_id": self._generate_batch_id(),
                "total_processed": success_count,
                "processing_time": "0.5s"
            }
            
            return sync_record
            
        except Exception as e:
            sync_record["status"] = SyncStatus.FAILED.value
            sync_record["end_time"] = datetime.now().isoformat()
            sync_record["error_message"] = str(e)
            return sync_record
    
    def _format_data_for_national_system(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化数据以符合国家系统要求"""
        formatted_data = []
        
        for record in data:
            formatted_record = {
                "province_code": "53",  # 云南省代码
                "province_name": "云南省",
                "city_code": record.get("city_code", ""),
                "city_name": record.get("city_name", ""),
                "enterprise_id": record.get("enterprise_id"),
                "enterprise_name": record.get("enterprise_name", ""),
                "industry_code": record.get("industry_code", ""),
                "industry_name": record.get("industry", ""),
                "report_month": record.get("report_month", ""),
                "total_employees": record.get("total_employees", 0),
                "employed_count": record.get("employed_count", 0),
                "unemployed_count": record.get("unemployed_count", 0),
                "unemployment_rate": record.get("unemployment_rate", 0.0),
                "new_employees": record.get("new_employees", 0),
                "lost_employees": record.get("lost_employees", 0),
                "submit_time": record.get("created_at", datetime.now().isoformat())
            }
            
            formatted_data.append(formatted_record)
        
        return formatted_data
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """查询同步状态"""
        # 模拟查询同步状态
        # 实际应用中应该调用国家系统的状态查询接口
        return {
            "sync_id": sync_id,
            "status": SyncStatus.SUCCESS.value,
            "progress": 100,
            "message": "同步完成"
        }
    
    def query_national_data(
        self,
        start_date: date,
        end_date: date,
        region_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """查询国家系统数据"""
        try:
            # 模拟查询国家系统数据
            # 实际应用中应该调用国家系统的数据查询接口
            mock_data = {
                "total_records": 100,
                "data": [
                    {
                        "date": "2026-01",
                        "province_code": "53",
                        "province_name": "云南省",
                        "total_employees": 1250000,
                        "employed_count": 1187500,
                        "unemployed_count": 62500,
                        "unemployment_rate": 5.0
                    }
                ]
            }
            
            return {
                "success": True,
                "data": mock_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败: {str(e)}"
            }
    
    def validate_data_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据格式是否符合国家系统要求"""
        errors = []
        warnings = []
        
        # 必填字段检查
        required_fields = [
            "province_code", "province_name", "enterprise_id",
            "report_month", "total_employees", "employed_count",
            "unemployed_count"
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"必填字段 {field} 缺失")
        
        # 数据格式检查
        if "unemployment_rate" in data:
            rate = data["unemployment_rate"]
            if not (0 <= rate <= 100):
                errors.append("失业率必须在0-100之间")
        
        if "total_employees" in data:
            total = data["total_employees"]
            if total < 0:
                errors.append("员工总数不能为负数")
        
        # 数据一致性检查
        if all(key in data for key in ["total_employees", "employed_count", "unemployed_count"]):
            total = data["total_employees"]
            employed = data["employed_count"]
            unemployed = data["unemployed_count"]
            
            if total != employed + unemployed:
                warnings.append("员工总数与就业、失业人数不匹配")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_sync_history(
        self,
        survey_period_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取同步历史记录"""
        # 模拟获取同步历史
        mock_history = [
            {
                "sync_id": "sync_20260330_001",
                "survey_period_id": 1,
                "status": SyncStatus.SUCCESS.value,
                "start_time": "2026-03-30T10:00:00",
                "end_time": "2026-03-30T10:00:05",
                "total_records": 1250,
                "success_records": 1250,
                "failed_records": 0
            },
            {
                "sync_id": "sync_20260329_001",
                "survey_period_id": 1,
                "status": SyncStatus.SUCCESS.value,
                "start_time": "2026-03-29T10:00:00",
                "end_time": "2026-03-29T10:00:04",
                "total_records": 1248,
                "success_records": 1248,
                "failed_records": 0
            }
        ]
        
        if survey_period_id:
            mock_history = [h for h in mock_history if h["survey_period_id"] == survey_period_id]
        
        return mock_history[:limit]
    
    def retry_sync(self, sync_id: str) -> Dict[str, Any]:
        """重试失败的同步"""
        try:
            # 模拟重试同步
            return {
                "success": True,
                "message": "重试同步已启动",
                "new_sync_id": self._generate_sync_id()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"重试失败: {str(e)}"
            }
    
    def cancel_sync(self, sync_id: str) -> Dict[str, Any]:
        """取消同步"""
        try:
            # 模拟取消同步
            return {
                "success": True,
                "message": "同步已取消"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"取消失败: {str(e)}"
            }
    
    def _generate_sync_id(self) -> str:
        """生成同步ID"""
        return f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _generate_batch_id(self) -> str:
        """生成批次ID"""
        return f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def close(self):
        """关闭客户端连接"""
        self.client.close()


class DataSyncManager:
    """数据同步管理器"""
    
    def __init__(self, national_service: NationalSystemService):
        self.national_service = national_service
        self.sync_records = {}
    
    def create_sync_task(
        self,
        survey_period_id: int,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建同步任务"""
        sync_record = self.national_service.sync_employment_data(survey_period_id, data)
        sync_id = sync_record["sync_id"]
        self.sync_records[sync_id] = sync_record
        
        return sync_record
    
    def get_sync_record(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """获取同步记录"""
        return self.sync_records.get(sync_id)
    
    def list_sync_records(
        self,
        survey_period_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """列出同步记录"""
        records = list(self.sync_records.values())
        
        if survey_period_id:
            records = [r for r in records if r["survey_period_id"] == survey_period_id]
        
        if status:
            records = [r for r in records if r["status"] == status]
        
        # 按开始时间倒序排序
        records.sort(key=lambda x: x["start_time"], reverse=True)
        
        return records
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """获取同步统计信息"""
        total_syncs = len(self.sync_records)
        success_syncs = len([r for r in self.sync_records.values() if r["status"] == SyncStatus.SUCCESS.value])
        failed_syncs = len([r for r in self.sync_records.values() if r["status"] == SyncStatus.FAILED.value])
        
        total_records = sum(r["total_records"] for r in self.sync_records.values())
        success_records = sum(r["success_records"] for r in self.sync_records.values())
        failed_records = sum(r["failed_records"] for r in self.sync_records.values())
        
        return {
            "total_syncs": total_syncs,
            "success_syncs": success_syncs,
            "failed_syncs": failed_syncs,
            "success_rate": round(success_syncs / total_syncs * 100, 2) if total_syncs > 0 else 0,
            "total_records": total_records,
            "success_records": success_records,
            "failed_records": failed_records,
            "record_success_rate": round(success_records / total_records * 100, 2) if total_records > 0 else 0
        }