"""
数据分析API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import date

from schemas.analysis_models import (
    AnalysisRequest,
    AnalysisResponse,
    TrendAnalysis,
    ComparisonAnalysis,
    AlertRule,
    DataAlert,
    DimensionType
)
from services.analysis_service import AnalysisService
from core.dependencies import get_current_user
from core.audit import AuditLogger
from db.mock_db import USER_DATABASE

router = APIRouter(prefix="/analysis", tags=["数据分析与统计"])

# 初始化服务
analysis_db = {
    "survey_data": {},
    "users": USER_DATABASE
}

analysis_service = AnalysisService(analysis_db)
audit_logger = AuditLogger()


@router.post("/analyze", summary="执行多维数据分析")
async def analyze_data(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    执行多维数据分析，包括总体统计、维度统计、时间序列分析等
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能执行数据分析"
        )
    
    try:
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        # 审计日志
        audit_logger.log_operation(
            user_id=current_user["user_id"],
            operation="ANALYSIS_EXECUTE",
            resource_type="analysis",
            resource_id=request.survey_period_id,
            details={
                "survey_period_id": request.survey_period_id,
                "dimensions": [d.value for d in request.dimensions]
            },
            ip_address="127.0.0.1"
        )
        
        return {
            "status": "success",
            "message": "分析完成",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/overall-statistics", summary="获取总体统计数据")
async def get_overall_statistics(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取总体就业统计数据
    
    权限要求：登录用户
    """
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        return {
            "status": "success",
            "statistics": result.overall_statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/dimension-statistics", summary="获取维度统计数据")
async def get_dimension_statistics(
    survey_period_id: int = Query(..., description="调查期ID"),
    dimension: DimensionType = Query(..., description="维度类型"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定维度的统计数据
    
    权限要求：登录用户
    """
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[dimension]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        # 过滤指定维度的统计
        dimension_stats = [
            d for d in result.dimension_statistics
            if d.dimension_name == dimension.value
        ]
        
        return {
            "status": "success",
            "dimension": dimension.value,
            "statistics": dimension_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取维度统计失败: {str(e)}")


@router.get("/time-series", summary="获取时间序列数据")
async def get_time_series(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取时间序列数据
    
    权限要求：登录用户
    """
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        return {
            "status": "success",
            "time_series": result.time_series_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间序列数据失败: {str(e)}")


@router.get("/top-unemployment", summary="获取失业率最高地区")
async def get_top_unemployment(
    survey_period_id: int = Query(..., description="调查期ID"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取失业率最高的地区列表
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看此数据"
        )
    
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        # 限制返回数量
        top_regions = result.top_unemployment_regions[:limit]
        
        return {
            "status": "success",
            "top_unemployment_regions": top_regions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/top-growth", summary="获取就业增长最快地区")
async def get_top_growth(
    survey_period_id: int = Query(..., description="调查期ID"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取就业增长最快的地区列表
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看此数据"
        )
    
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        # 限制返回数量
        top_regions = result.top_growth_regions[:limit]
        
        return {
            "status": "success",
            "top_growth_regions": top_regions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/data-quality", summary="获取数据质量报告")
async def get_data_quality(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取数据质量报告
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看数据质量报告"
        )
    
    try:
        # 构建分析请求
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        # 执行分析
        result = analysis_service.analyze_data(request)
        
        return {
            "status": "success",
            "data_quality_report": result.data_quality_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据质量报告失败: {str(e)}")


@router.get("/trend-analysis", summary="获取趋势分析")
async def get_trend_analysis(
    survey_period_id: int = Query(..., description="调查期ID"),
    metric: str = Query(..., description="指标名称"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定指标的趋势分析
    
    权限要求：登录用户
    """
    try:
        # 获取调查数据
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        survey_data = analysis_service._get_survey_data(request)
        
        if len(survey_data) < 2:
            raise HTTPException(
                status_code=400,
                detail="需要至少两个周期的数据才能进行趋势分析"
            )
        
        # 计算趋势分析
        trend = analysis_service.calculate_trend_analysis(survey_data, metric)
        
        return {
            "status": "success",
            "trend_analysis": trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"趋势分析失败: {str(e)}")


@router.post("/alerts/check", summary="检查预警")
async def check_alerts(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    检查数据预警
    
    权限要求：省级管理员
    """
    # 权限检查
    if current_user.get("role_name") != "省级管理员":
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员才能检查预警"
        )
    
    try:
        # 获取调查数据
        request = AnalysisRequest(
            survey_period_id=survey_period_id,
            dimensions=[]
        )
        
        survey_data = analysis_service._get_survey_data(request)
        
        # 定义预警规则
        rules = [
            AlertRule(
                rule_id=1,
                rule_name="失业率过高预警",
                metric="unemployment_rate",
                threshold_type="greater_than",
                threshold_value=10.0,
                severity="high"
            ),
            AlertRule(
                rule_id=2,
                rule_name="就业减少预警",
                metric="net_change",
                threshold_type="less_than",
                threshold_value=-100,
                severity="medium"
            ),
            AlertRule(
                rule_id=3,
                rule_name="大规模裁员预警",
                metric="lost_employees",
                threshold_type="greater_than",
                threshold_value=500,
                severity="high"
            )
        ]
        
        # 检查预警
        alerts = analysis_service.check_alerts(survey_data, rules)
        
        return {
            "status": "success",
            "total_alerts": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查预警失败: {str(e)}")


@router.get("/comparison", summary="获取对比分析")
async def get_comparison(
    period1_id: int = Query(..., description="周期1 ID"),
    period2_id: int = Query(..., description="周期2 ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取两个周期的对比分析
    
    权限要求：省级管理员、市级审核员
    """
    # 权限检查
    if current_user.get("role_name") not in ["省级管理员", "市级审核员"]:
        raise HTTPException(
            status_code=403,
            detail="只有省级管理员和市级审核员才能查看对比分析"
        )
    
    try:
        # 获取两个周期的数据
        request1 = AnalysisRequest(survey_period_id=period1_id, dimensions=[])
        request2 = AnalysisRequest(survey_period_id=period2_id, dimensions=[])
        
        result1 = analysis_service.analyze_data(request1)
        result2 = analysis_service.analyze_data(request2)
        
        # 构建对比数据
        metrics = {
            "total_employees": {
                "period1": result1.overall_statistics.total_employees,
                "period2": result2.overall_statistics.total_employees,
                "change": result2.overall_statistics.total_employees - result1.overall_statistics.total_employees
            },
            "employed_count": {
                "period1": result1.overall_statistics.employed_count,
                "period2": result2.overall_statistics.employed_count,
                "change": result2.overall_statistics.employed_count - result1.overall_statistics.employed_count
            },
            "unemployed_count": {
                "period1": result1.overall_statistics.unemployed_count,
                "period2": result2.overall_statistics.unemployed_count,
                "change": result2.overall_statistics.unemployed_count - result1.overall_statistics.unemployed_count
            },
            "unemployment_rate": {
                "period1": result1.overall_statistics.unemployment_rate,
                "period2": result2.overall_statistics.unemployment_rate,
                "change": result2.overall_statistics.unemployment_rate - result1.overall_statistics.unemployment_rate
            },
            "new_employees": {
                "period1": result1.overall_statistics.new_employees,
                "period2": result2.overall_statistics.new_employees,
                "change": result2.overall_statistics.new_employees - result1.overall_statistics.new_employees
            }
        }
        
        return {
            "status": "success",
            "comparison_type": "period_comparison",
            "period1": str(period1_id),
            "period2": str(period2_id),
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对比分析失败: {str(e)}")