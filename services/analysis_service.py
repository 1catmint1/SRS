"""
数据清洗与多维分析统计服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import re
from collections import defaultdict

from schemas.analysis_models import (
    DataQualityIssue,
    DataCleaningReport,
    EmploymentStatistics,
    DimensionStatistics,
    TimeSeriesData,
    AnalysisRequest,
    AnalysisResponse,
    TrendAnalysis,
    ComparisonAnalysis,
    AlertRule,
    DataAlert,
    DimensionType
)


class DataCleaningService:
    """数据清洗服务"""
    
    def __init__(self):
        self.cleaning_rules = []
        self.issues = []
    
    def clean_survey_data(self, data: List[Dict[str, Any]]) -> DataCleaningReport:
        """清洗调查数据"""
        total_records = len(data)
        valid_records = 0
        invalid_records = 0
        cleaned_records = 0
        
        self.issues = []
        
        for record in data:
            record_issues = self._validate_record(record)
            
            if record_issues:
                invalid_records += 1
                self.issues.extend(record_issues)
                
                # 尝试清洗数据
                cleaned = self._clean_record(record, record_issues)
                if cleaned:
                    cleaned_records += 1
                    valid_records += 1
            else:
                valid_records += 1
        
        # 计算数据质量评分
        quality_score = self._calculate_quality_score(total_records, invalid_records)
        
        return DataCleaningReport(
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            cleaned_records=cleaned_records,
            quality_score=quality_score,
            issues=self.issues,
            cleaning_rules=self.cleaning_rules
        )
    
    def _validate_record(self, record: Dict[str, Any]) -> List[DataQualityIssue]:
        """验证单条记录"""
        issues = []
        
        # 必填字段检查
        required_fields = [
            "enterprise_id", "survey_period_id", "report_month",
            "total_employees", "employed_count", "unemployed_count"
        ]
        
        for field in required_fields:
            if field not in record or record[field] is None:
                issues.append(DataQualityIssue(
                    issue_type="missing_value",
                    severity="high",
                    field_name=field,
                    record_id=record.get("survey_id"),
                    description=f"必填字段 {field} 缺失",
                    suggested_value=None
                ))
        
        # 数值范围检查
        if "total_employees" in record and record["total_employees"] is not None:
            if record["total_employees"] < 0:
                issues.append(DataQualityIssue(
                    issue_type="invalid_range",
                    severity="high",
                    field_name="total_employees",
                    record_id=record.get("survey_id"),
                    description="员工总数不能为负数",
                    suggested_value=abs(record["total_employees"])
                ))
        
        if "employed_count" in record and record["employed_count"] is not None:
            if record["employed_count"] < 0:
                issues.append(DataQualityIssue(
                    issue_type="invalid_range",
                    severity="high",
                    field_name="employed_count",
                    record_id=record.get("survey_id"),
                    description="就业人数不能为负数",
                    suggested_value=abs(record["employed_count"])
                ))
        
        # 逻辑一致性检查
        if all(key in record for key in ["total_employees", "employed_count", "unemployed_count"]):
            total = record["total_employees"] or 0
            employed = record["employed_count"] or 0
            unemployed = record["unemployed_count"] or 0
            
            if total != employed + unemployed:
                issues.append(DataQualityIssue(
                    issue_type="logic_inconsistency",
                    severity="high",
                    field_name="employment_balance",
                    record_id=record.get("survey_id"),
                    description=f"员工总数({total})不等于就业人数({employed})+失业人数({unemployed})",
                    suggested_value=employed + unemployed
                ))
        
        # 手机号格式检查
        if "contact_phone" in record and record["contact_phone"]:
            phone = record["contact_phone"]
            if not self._validate_phone(phone):
                issues.append(DataQualityIssue(
                    issue_type="invalid_format",
                    severity="medium",
                    field_name="contact_phone",
                    record_id=record.get("survey_id"),
                    description="手机号格式不正确",
                    suggested_value=self._normalize_phone(phone)
                ))
        
        # 邮箱格式检查
        if "contact_email" in record and record["contact_email"]:
            email = record["contact_email"]
            if not self._validate_email(email):
                issues.append(DataQualityIssue(
                    issue_type="invalid_format",
                    severity="medium",
                    field_name="contact_email",
                    record_id=record.get("survey_id"),
                    description="邮箱格式不正确",
                    suggested_value=self._normalize_email(email)
                ))
        
        # 失业率合理性检查
        if "total_employees" in record and record["total_employees"] > 0:
            unemployment_rate = record.get("unemployed_count", 0) / record["total_employees"] * 100
            if unemployment_rate > 50:
                issues.append(DataQualityIssue(
                    issue_type="abnormal_value",
                    severity="medium",
                    field_name="unemployment_rate",
                    record_id=record.get("survey_id"),
                    description=f"失业率{unemployment_rate:.2f}%过高，可能存在数据异常",
                    suggested_value=None
                ))
        
        return issues
    
    def _clean_record(self, record: Dict[str, Any], issues: List[DataQualityIssue]) -> bool:
        """清洗单条记录"""
        cleaned = False
        
        for issue in issues:
            if issue.suggested_value is not None:
                record[issue.field_name] = issue.suggested_value
                cleaned = True
        
        return cleaned
    
    def _calculate_quality_score(self, total: int, invalid: int) -> float:
        """计算数据质量评分"""
        if total == 0:
            return 100.0
        
        invalid_rate = invalid / total
        quality_score = (1 - invalid_rate) * 100
        
        return round(quality_score, 2)
    
    def _validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    def _normalize_phone(self, phone: str) -> Optional[str]:
        """规范化手机号"""
        # 移除非数字字符
        phone = re.sub(r'[^\d]', '', phone)
        
        # 检查长度
        if len(phone) == 11 and phone.startswith('1'):
            return phone
        
        return None
    
    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _normalize_email(self, email: str) -> Optional[str]:
        """规范化邮箱"""
        email = email.strip().lower()
        
        if self._validate_email(email):
            return email
        
        return None


class AnalysisService:
    """多维分析统计服务"""
    
    def __init__(self, db):
        self.db = db
        self.cleaning_service = DataCleaningService()
    
    def analyze_data(self, request: AnalysisRequest) -> AnalysisResponse:
        """执行多维数据分析"""
        # 获取数据
        survey_data = self._get_survey_data(request)
        
        # 数据清洗
        quality_report = self.cleaning_service.clean_survey_data(survey_data)
        
        # 总体统计
        overall_stats = self._calculate_overall_statistics(survey_data)
        
        # 维度统计
        dimension_stats = self._calculate_dimension_statistics(survey_data, request.dimensions)
        
        # 时间序列数据
        time_series = self._calculate_time_series(survey_data, request)
        
        # 失业率最高地区
        top_unemployment = self._get_top_unemployment_regions(survey_data)
        
        # 就业增长最快地区
        top_growth = self._get_top_growth_regions(survey_data)
        
        return AnalysisResponse(
            overall_statistics=overall_stats,
            dimension_statistics=dimension_stats,
            time_series_data=time_series,
            top_unemployment_regions=top_unemployment,
            top_growth_regions=top_growth,
            data_quality_report=quality_report
        )
    
    def _get_survey_data(self, request: AnalysisRequest) -> List[Dict[str, Any]]:
        """获取调查数据"""
        survey_data = []
        
        for survey_id, data in self.db.get("survey_data", {}).items():
            # 过滤调查期
            if data.get("survey_period_id") != request.survey_period_id:
                continue
            
            # 时间过滤
            if request.start_date or request.end_date:
                report_date = datetime.strptime(data.get("report_month", "2026-01"), "%Y-%m").date()
                if request.start_date and report_date < request.start_date:
                    continue
                if request.end_date and report_date > request.end_date:
                    continue
            
            # 地区过滤
            if request.region_filter:
                region_id = data.get("region_id")
                if region_id not in request.region_filter:
                    continue
            
            # 行业过滤
            if request.industry_filter:
                industry = data.get("industry")
                if industry not in request.industry_filter:
                    continue
            
            # 企业规模过滤
            if request.enterprise_scale_filter:
                scale = data.get("business_scale")
                if scale not in request.enterprise_scale_filter:
                    continue
            
            survey_data.append(data)
        
        return survey_data
    
    def _calculate_overall_statistics(self, data: List[Dict[str, Any]]) -> EmploymentStatistics:
        """计算总体统计"""
        total_enterprises = len(set(d.get("enterprise_id") for d in data))
        
        total_employees = sum(d.get("total_employees", 0) for d in data)
        employed_count = sum(d.get("employed_count", 0) for d in data)
        unemployed_count = sum(d.get("unemployed_count", 0) for d in data)
        
        unemployment_rate = (unemployed_count / total_employees * 100) if total_employees > 0 else 0
        
        new_employees = sum(d.get("new_employees", 0) for d in data)
        lost_employees = sum(d.get("lost_employees", 0) for d in data)
        net_change = new_employees - lost_employees
        
        return EmploymentStatistics(
            total_enterprises=total_enterprises,
            total_employees=total_employees,
            employed_count=employed_count,
            unemployed_count=unemployed_count,
            unemployment_rate=round(unemployment_rate, 2),
            new_employees=new_employees,
            lost_employees=lost_employees,
            net_change=net_change
        )
    
    def _calculate_dimension_statistics(
        self,
        data: List[Dict[str, Any]],
        dimensions: List[DimensionType]
    ) -> List[DimensionStatistics]:
        """计算维度统计"""
        dimension_stats = []
        
        for dimension in dimensions:
            if dimension == DimensionType.REGION:
                stats = self._calculate_region_statistics(data)
            elif dimension == DimensionType.INDUSTRY:
                stats = self._calculate_industry_statistics(data)
            elif dimension == DimensionType.ENTERPRISE_SCALE:
                stats = self._calculate_scale_statistics(data)
            else:
                continue
            
            dimension_stats.extend(stats)
        
        return dimension_stats
    
    def _calculate_region_statistics(self, data: List[Dict[str, Any]]) -> List[DimensionStatistics]:
        """计算地区统计"""
        region_data = defaultdict(list)
        
        for record in data:
            region_id = record.get("region_id", "unknown")
            region_name = record.get("region_name", f"地区{region_id}")
            region_data[region_name].append(record)
        
        stats = []
        for region_name, records in region_data.items():
            total_employees = sum(r.get("total_employees", 0) for r in records)
            employed_count = sum(r.get("employed_count", 0) for r in records)
            unemployed_count = sum(r.get("unemployed_count", 0) for r in records)
            unemployment_rate = (unemployed_count / total_employees * 100) if total_employees > 0 else 0
            new_employees = sum(r.get("new_employees", 0) for r in records)
            lost_employees = sum(r.get("lost_employees", 0) for r in records)
            
            stats.append(DimensionStatistics(
                dimension_name="region",
                dimension_value=region_name,
                total_enterprises=len(set(r.get("enterprise_id") for r in records)),
                total_employees=total_employees,
                employed_count=employed_count,
                unemployed_count=unemployed_count,
                unemployment_rate=round(unemployment_rate, 2),
                new_employees=new_employees,
                lost_employees=lost_employees,
                net_change=new_employees - lost_employees
            ))
        
        return stats
    
    def _calculate_industry_statistics(self, data: List[Dict[str, Any]]) -> List[DimensionStatistics]:
        """计算行业统计"""
        industry_data = defaultdict(list)
        
        for record in data:
            industry = record.get("industry", "unknown")
            industry_data[industry].append(record)
        
        stats = []
        for industry, records in industry_data.items():
            total_employees = sum(r.get("total_employees", 0) for r in records)
            employed_count = sum(r.get("employed_count", 0) for r in records)
            unemployed_count = sum(r.get("unemployed_count", 0) for r in records)
            unemployment_rate = (unemployed_count / total_employees * 100) if total_employees > 0 else 0
            new_employees = sum(r.get("new_employees", 0) for r in records)
            lost_employees = sum(r.get("lost_employees", 0) for r in records)
            
            stats.append(DimensionStatistics(
                dimension_name="industry",
                dimension_value=industry,
                total_enterprises=len(set(r.get("enterprise_id") for r in records)),
                total_employees=total_employees,
                employed_count=employed_count,
                unemployed_count=unemployed_count,
                unemployment_rate=round(unemployment_rate, 2),
                new_employees=new_employees,
                lost_employees=lost_employees,
                net_change=new_employees - lost_employees
            ))
        
        return stats
    
    def _calculate_scale_statistics(self, data: List[Dict[str, Any]]) -> List[DimensionStatistics]:
        """计算企业规模统计"""
        scale_data = defaultdict(list)
        
        for record in data:
            scale = record.get("business_scale", "unknown")
            scale_data[scale].append(record)
        
        stats = []
        for scale, records in scale_data.items():
            total_employees = sum(r.get("total_employees", 0) for r in records)
            employed_count = sum(r.get("employed_count", 0) for r in records)
            unemployed_count = sum(r.get("unemployed_count", 0) for r in records)
            unemployment_rate = (unemployed_count / total_employees * 100) if total_employees > 0 else 0
            new_employees = sum(r.get("new_employees", 0) for r in records)
            lost_employees = sum(r.get("lost_employees", 0) for r in records)
            
            stats.append(DimensionStatistics(
                dimension_name="enterprise_scale",
                dimension_value=scale,
                total_enterprises=len(set(r.get("enterprise_id") for r in records)),
                total_employees=total_employees,
                employed_count=employed_count,
                unemployed_count=unemployed_count,
                unemployment_rate=round(unemployment_rate, 2),
                new_employees=new_employees,
                lost_employees=lost_employees,
                net_change=new_employees - lost_employees
            ))
        
        return stats
    
    def _calculate_time_series(self, data: List[Dict[str, Any]], request: AnalysisRequest) -> List[TimeSeriesData]:
        """计算时间序列数据"""
        monthly_data = defaultdict(list)
        
        for record in data:
            month = record.get("report_month", "2026-01")
            monthly_data[month].append(record)
        
        time_series = []
        for month in sorted(monthly_data.keys()):
            records = monthly_data[month]
            total_employees = sum(r.get("total_employees", 0) for r in records)
            employed_count = sum(r.get("employed_count", 0) for r in records)
            unemployed_count = sum(r.get("unemployed_count", 0) for r in records)
            unemployment_rate = (unemployed_count / total_employees * 100) if total_employees > 0 else 0
            new_employees = sum(r.get("new_employees", 0) for r in records)
            lost_employees = sum(r.get("lost_employees", 0) for r in records)
            
            time_series.append(TimeSeriesData(
                period=month,
                total_employees=total_employees,
                employed_count=employed_count,
                unemployed_count=unemployed_count,
                unemployment_rate=round(unemployment_rate, 2),
                new_employees=new_employees,
                lost_employees=lost_employees,
                net_change=new_employees - lost_employees
            ))
        
        return time_series
    
    def _get_top_unemployment_regions(self, data: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """获取失业率最高的地区"""
        region_stats = {}
        
        for record in data:
            region_id = record.get("region_id", "unknown")
            region_name = record.get("region_name", f"地区{region_id}")
            
            if region_name not in region_stats:
                region_stats[region_name] = {
                    "total_employees": 0,
                    "unemployed_count": 0
                }
            
            region_stats[region_name]["total_employees"] += record.get("total_employees", 0)
            region_stats[region_name]["unemployed_count"] += record.get("unemployed_count", 0)
        
        # 计算失业率并排序
        regions_with_rate = []
        for region_name, stats in region_stats.items():
            total = stats["total_employees"]
            unemployed = stats["unemployed_count"]
            rate = (unemployed / total * 100) if total > 0 else 0
            
            regions_with_rate.append({
                "region": region_name,
                "unemployment_rate": round(rate, 2),
                "total_employees": total,
                "unemployed_count": unemployed
            })
        
        regions_with_rate.sort(key=lambda x: x["unemployment_rate"], reverse=True)
        
        return regions_with_rate[:limit]
    
    def _get_top_growth_regions(self, data: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """获取就业增长最快的地区"""
        region_stats = {}
        
        for record in data:
            region_id = record.get("region_id", "unknown")
            region_name = record.get("region_name", f"地区{region_id}")
            
            if region_name not in region_stats:
                region_stats[region_name] = {
                    "new_employees": 0,
                    "lost_employees": 0
                }
            
            region_stats[region_name]["new_employees"] += record.get("new_employees", 0)
            region_stats[region_name]["lost_employees"] += record.get("lost_employees", 0)
        
        # 计算净增长并排序
        regions_with_growth = []
        for region_name, stats in region_stats.items():
            net_change = stats["new_employees"] - stats["lost_employees"]
            
            regions_with_growth.append({
                "region": region_name,
                "net_change": net_change,
                "new_employees": stats["new_employees"],
                "lost_employees": stats["lost_employees"]
            })
        
        regions_with_growth.sort(key=lambda x: x["net_change"], reverse=True)
        
        return regions_with_growth[:limit]
    
    def calculate_trend_analysis(self, data: List[Dict[str, Any]], metric: str) -> TrendAnalysis:
        """计算趋势分析"""
        if len(data) < 2:
            raise ValueError("需要至少两个周期的数据")
        
        # 按时间排序
        sorted_data = sorted(data, key=lambda x: x.get("report_month", ""))
        
        # 获取最近两个周期的数据
        current = sorted_data[-1]
        previous = sorted_data[-2]
        
        current_value = current.get(metric, 0)
        previous_value = previous.get(metric, 0)
        
        change_value = current_value - previous_value
        change_rate = (change_value / previous_value * 100) if previous_value != 0 else 0
        
        # 判断趋势
        if change_value > 0:
            trend = "up"
        elif change_value < 0:
            trend = "down"
        else:
            trend = "stable"
        
        return TrendAnalysis(
            metric=metric,
            current_value=current_value,
            previous_value=previous_value,
            change_value=change_value,
            change_rate=round(change_rate, 2),
            trend=trend
        )
    
    def check_alerts(self, data: List[Dict[str, Any]], rules: List[AlertRule]) -> List[DataAlert]:
        """检查预警规则"""
        alerts = []
        
        for rule in rules:
            if not rule.is_active:
                continue
            
            for record in data:
                metric_value = record.get(rule.metric, 0)
                
                triggered = False
                if rule.threshold_type == "greater_than":
                    triggered = metric_value > rule.threshold_value
                elif rule.threshold_type == "less_than":
                    triggered = metric_value < rule.threshold_value
                elif rule.threshold_type == "equal":
                    triggered = metric_value == rule.threshold_value
                
                if triggered:
                    alert = DataAlert(
                        alert_id=len(alerts) + 1,
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        metric=rule.metric,
                        current_value=metric_value,
                        threshold_value=rule.threshold_value,
                        severity=rule.severity,
                        region=record.get("region_name"),
                        industry=record.get("industry"),
                        alert_time=datetime.now(),
                        status="pending"
                    )
                    alerts.append(alert)
        
        return alerts