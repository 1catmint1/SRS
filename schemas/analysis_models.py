"""
数据分析模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class AnalysisPeriod(str, Enum):
    """分析周期"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class DimensionType(str, Enum):
    """维度类型"""
    REGION = "region"  # 地区维度
    INDUSTRY = "industry"  # 行业维度
    ENTERPRISE_SCALE = "enterprise_scale"  # 企业规模维度
    TIME = "time"  # 时间维度


class DataQualityIssue(BaseModel):
    """数据质量问题"""
    issue_type: str = Field(..., description="问题类型")
    severity: str = Field(..., description="严重程度：high-高, medium-中, low-低")
    field_name: str = Field(..., description="字段名称")
    record_id: Optional[int] = Field(None, description="记录ID")
    description: str = Field(..., description="问题描述")
    suggested_value: Optional[Any] = Field(None, description="建议值")


class DataCleaningReport(BaseModel):
    """数据清洗报告"""
    total_records: int = Field(..., description="总记录数")
    valid_records: int = Field(..., description="有效记录数")
    invalid_records: int = Field(..., description="无效记录数")
    cleaned_records: int = Field(..., description="清洗记录数")
    quality_score: float = Field(..., description="数据质量评分 0-100")
    issues: List[DataQualityIssue] = Field(default_factory=list)
    cleaning_rules: List[str] = Field(default_factory=list)


class EmploymentStatistics(BaseModel):
    """就业统计数据"""
    total_enterprises: int = Field(..., description="企业总数")
    total_employees: int = Field(..., description="员工总数")
    employed_count: int = Field(..., description="就业人数")
    unemployed_count: int = Field(..., description="失业人数")
    unemployment_rate: float = Field(..., description="失业率(%)")
    new_employees: int = Field(..., description="新增就业人数")
    lost_employees: int = Field(..., description="减少就业人数")
    net_change: int = Field(..., description="净变化人数")
    
    class Config:
        from_attributes = True


class DimensionStatistics(BaseModel):
    """维度统计数据"""
    dimension_name: str = Field(..., description="维度名称")
    dimension_value: str = Field(..., description="维度值")
    total_enterprises: int = Field(..., description="企业数")
    total_employees: int = Field(..., description="员工总数")
    employed_count: int = Field(..., description="就业人数")
    unemployed_count: int = Field(..., description="失业人数")
    unemployment_rate: float = Field(..., description="失业率(%)")
    new_employees: int = Field(..., description="新增就业人数")
    lost_employees: int = Field(..., description="减少就业人数")
    net_change: int = Field(..., description="净变化人数")


class TimeSeriesData(BaseModel):
    """时间序列数据"""
    period: str = Field(..., description="周期")
    total_employees: int = Field(..., description="员工总数")
    employed_count: int = Field(..., description="就业人数")
    unemployed_count: int = Field(..., description="失业人数")
    unemployment_rate: float = Field(..., description="失业率(%)")
    new_employees: int = Field(..., description="新增就业人数")
    lost_employees: int = Field(..., description="减少就业人数")
    net_change: int = Field(..., description="净变化人数")


class AnalysisRequest(BaseModel):
    """分析请求"""
    survey_period_id: int = Field(..., description="调查期ID")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    dimensions: List[DimensionType] = Field(default_factory=list, description="分析维度")
    region_filter: Optional[List[int]] = Field(None, description="地区过滤")
    industry_filter: Optional[List[str]] = Field(None, description="行业过滤")
    enterprise_scale_filter: Optional[List[str]] = Field(None, description="企业规模过滤")


class AnalysisResponse(BaseModel):
    """分析响应"""
    overall_statistics: EmploymentStatistics = Field(..., description="总体统计")
    dimension_statistics: List[DimensionStatistics] = Field(default_factory=list, description="维度统计")
    time_series_data: List[TimeSeriesData] = Field(default_factory=list, description="时间序列数据")
    top_unemployment_regions: List[Dict[str, Any]] = Field(default_factory=list, description="失业率最高地区")
    top_growth_regions: List[Dict[str, Any]] = Field(default_factory=list, description="就业增长最快地区")
    data_quality_report: DataCleaningReport = Field(..., description="数据质量报告")


class TrendAnalysis(BaseModel):
    """趋势分析"""
    metric: str = Field(..., description="指标名称")
    current_value: float = Field(..., description="当前值")
    previous_value: float = Field(..., description="上期值")
    change_value: float = Field(..., description="变化值")
    change_rate: float = Field(..., description="变化率(%)")
    trend: str = Field(..., description="趋势：up-上升, down-下降, stable-稳定")
    
    class Config:
        from_attributes = True


class ComparisonAnalysis(BaseModel):
    """对比分析"""
    comparison_type: str = Field(..., description="对比类型")
    period1: str = Field(..., description="周期1")
    period2: str = Field(..., description="周期2")
    metrics: Dict[str, Dict[str, float]] = Field(..., description="指标对比数据")


class AlertRule(BaseModel):
    """预警规则"""
    rule_id: int = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    metric: str = Field(..., description="监控指标")
    threshold_type: str = Field(..., description="阈值类型：greater_than, less_than, equal, between")
    threshold_value: float = Field(..., description="阈值")
    severity: str = Field(..., description="严重程度：high, medium, low")
    is_active: bool = Field(True, description="是否启用")


class DataAlert(BaseModel):
    """数据预警"""
    alert_id: int = Field(..., description="预警ID")
    rule_id: int = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    metric: str = Field(..., description="指标名称")
    current_value: float = Field(..., description="当前值")
    threshold_value: float = Field(..., description="阈值")
    severity: str = Field(..., description="严重程度")
    region: Optional[str] = Field(None, description="地区")
    industry: Optional[str] = Field(None, description="行业")
    alert_time: datetime = Field(..., description="预警时间")
    status: str = Field(..., description="状态：pending, acknowledged, resolved")