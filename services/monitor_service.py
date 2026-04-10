"""
系统监控服务
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import platform
import os


class SystemMonitorService:
    """系统监控服务类"""
    
    def __init__(self):
        self.start_time = datetime.now()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        return {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            }
        }
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            # 尝试使用psutil获取详细信息
            import psutil
            
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            
            # 网络信息
            network = psutil.net_io_counters()
            
            # 进程信息
            process = psutil.Process()
            process_info = {
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms
                },
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current if cpu_freq else None,
                        "min": cpu_freq.min if cpu_freq else None,
                        "max": cpu_freq.max if cpu_freq else None
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "process": process_info
            }
        
        except ImportError:
            # 如果没有psutil，返回基本信息
            return self._get_basic_resource_usage()
    
    def _get_basic_resource_usage(self) -> Dict[str, Any]:
        """获取基本资源使用信息（不依赖psutil）"""
        import shutil
        
        # 磁盘信息
        disk = shutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": 0,
                "count": os.cpu_count(),
                "frequency": None
            },
            "memory": {
                "total": 0,
                "available": 0,
                "percent": 0,
                "used": 0,
                "free": 0
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total * 100) if disk.total > 0 else 0
            },
            "network": {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0
            },
            "process": {
                "pid": os.getpid(),
                "name": "python",
                "cpu_percent": 0,
                "memory_info": None,
                "create_time": self.start_time.isoformat()
            }
        }
    
    def get_application_status(self) -> Dict[str, Any]:
        """获取应用系统状态"""
        uptime = datetime.now() - self.start_time
        
        return {
            "status": "running",
            "uptime": str(uptime),
            "uptime_seconds": uptime.total_seconds(),
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "version": "v0.5 Alpha"
        }
    
    def get_database_status(self, db: Dict[str, Any]) -> Dict[str, Any]:
        """获取数据库状态"""
        try:
            # 统计各类数据量
            user_count = len(db.get("users", {}))
            enterprise_count = len(db.get("enterprises", {}))
            survey_period_count = len(db.get("survey_periods", {}))
            survey_data_count = len(db.get("survey_data", {}))
            notification_count = len(db.get("notifications", {}))
            audit_log_count = len(db.get("audit_logs", []))
            
            return {
                "status": "connected",
                "type": "mock_db",
                "statistics": {
                    "users": user_count,
                    "enterprises": enterprise_count,
                    "survey_periods": survey_period_count,
                    "survey_data": survey_data_count,
                    "notifications": notification_count,
                    "audit_logs": audit_log_count
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查系统资源
            resource_usage = self.get_resource_usage()
            
            # 检查各组件状态
            components = {
                "system": "healthy",
                "database": "healthy",
                "application": "healthy"
            }
            
            # 检查CPU使用率
            if resource_usage["cpu"]["percent"] > 90:
                components["system"] = "warning"
            
            # 检查内存使用率
            if resource_usage["memory"]["percent"] > 90:
                components["system"] = "warning"
            
            # 检查磁盘使用率
            if resource_usage["disk"]["percent"] > 90:
                components["system"] = "warning"
            
            # 总体健康状态
            overall_status = "healthy"
            if any(status == "warning" for status in components.values()):
                overall_status = "warning"
            elif any(status == "error" for status in components.values()):
                overall_status = "error"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "components": components,
                "resource_usage": {
                    "cpu_percent": resource_usage["cpu"]["percent"],
                    "memory_percent": resource_usage["memory"]["percent"],
                    "disk_percent": resource_usage["disk"]["percent"]
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能指标（模拟历史数据）"""
        # 生成模拟的历史数据
        metrics = []
        now = datetime.now()
        
        for i in range(hours):
            timestamp = now - timedelta(hours=i)
            
            # 模拟CPU使用率（0-30%之间波动）
            cpu_percent = 10 + (i % 3) * 5
            
            # 模拟内存使用率（40-60%之间波动）
            memory_percent = 50 + (i % 4) * 2.5
            
            # 模拟磁盘使用率（基本稳定）
            disk_percent = 45
            
            metrics.append({
                "timestamp": timestamp.isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            })
        
        return {
            "period": f"{hours} hours",
            "metrics": metrics
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """获取系统告警"""
        alerts = []
        
        try:
            resource_usage = self.get_resource_usage()
            
            # CPU告警
            if resource_usage["cpu"]["percent"] > 80:
                alerts.append({
                    "level": "warning" if resource_usage["cpu"]["percent"] < 90 else "critical",
                    "type": "cpu",
                    "message": f"CPU使用率过高: {resource_usage['cpu']['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 内存告警
            if resource_usage["memory"]["percent"] > 80:
                alerts.append({
                    "level": "warning" if resource_usage["memory"]["percent"] < 90 else "critical",
                    "type": "memory",
                    "message": f"内存使用率过高: {resource_usage['memory']['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 磁盘告警
            if resource_usage["disk"]["percent"] > 80:
                alerts.append({
                    "level": "warning" if resource_usage["disk"]["percent"] < 90 else "critical",
                    "type": "disk",
                    "message": f"磁盘使用率过高: {resource_usage['disk']['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            alerts.append({
                "level": "error",
                "type": "system",
                "message": f"系统监控错误: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def format_bytes(self, bytes_value: int) -> str:
        """格式化字节数为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"