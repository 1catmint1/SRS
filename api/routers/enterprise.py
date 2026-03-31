from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from core.dependencies import PermissionChecker, get_current_user
from core.audit import audit_logger
from core.validation import dynamic_validator
from schemas.survey_models import (
    SurveyDataRequest, SurveyDataResponse, SurveyDataUpdate,
    ValidationResult, SurveyStatistics
)
from db.mock_db import t_survey_data, t_enterprise_info, t_survey_period

router = APIRouter(prefix="/enterprise", tags=["5. 企业填报业务流"])


@router.post("/survey/submit",
             summary="提交月度调查数据",
             dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def submit_survey_data(
    req: SurveyDataRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    企业提交月度调查数据
    
    权限要求: ENT_SUBMIT (企业数据填报)
    
    功能:
    - 动态校验(BR-01): 基础规则校验 + 业务逻辑校验
    - 审计留痕: 记录填报操作
    - 数据完整性检查
    """
    # 1. 验证企业是否存在
    enterprise = t_enterprise_info.get(req.enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="未找到指定的企业")
    
    # 2. 动态校验 (BR-01)
    validation_result = dynamic_validator.validate_all(req.dict())
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "数据校验失败",
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "suggestions": validation_result.suggestions
            }
        )
    
    # 3. 检查是否已经提交过该月份的数据
    survey_key = f"{req.enterprise_id}_{req.report_month}"
    if survey_key in t_survey_data:
        existing_data = t_survey_data[survey_key]
        if existing_data.get('status') == 'submitted':
            raise HTTPException(
                status_code=400,
                detail=f"企业已在{req.report_month}提交过调查数据，如需修改请联系管理员"
            )
    
    # 4. 计算失业率
    unemployment_rate = (req.unemployed_count / req.total_employees) * 100 if req.total_employees > 0 else 0
    
    # 5. 生成调查数据记录
    survey_id = len(t_survey_data) + 1
    survey_data = {
        "survey_id": survey_id,
        "survey_period_id": req.survey_period_id,
        "enterprise_id": req.enterprise_id,
        "enterprise_name": enterprise.get("enterprise_name", ""),
        "report_month": req.report_month,
        "total_employees": req.total_employees,
        "employed_count": req.employed_count,
        "unemployed_count": req.unemployed_count,
        "unemployment_rate": round(unemployment_rate, 2),
        "new_employees": req.new_employees,
        "lost_employees": req.lost_employees,
        "full_time_employees": req.full_time_employees,
        "part_time_employees": req.part_time_employees,
        "contract_employees": req.contract_employees,
        "total_payroll": req.total_payroll,
        "average_salary": req.average_salary,
        "industry_type": req.industry_type,
        "business_scale": req.business_scale,
        "contact_person": req.contact_person,
        "contact_phone": req.contact_phone,
        "contact_email": req.contact_email,
        "remarks": req.remarks,
        "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "submit_user_id": current_user.get("user_id"),
        "status": "submitted",
        "audit_status": "pending"
    }
    
    # 6. 保存调查数据
    t_survey_data[survey_key] = survey_data
    
    # 7. 审计留痕
    audit_logger.log_operation(
        user_id=current_user.get("user_id"),
        operation_type="SURVEY_SUBMIT",
        table_name="t_survey_data",
        record_id=survey_id,
        old_value="",
        new_value=f"企业ID:{req.enterprise_id}, 月份:{req.report_month}, 员工总数:{req.total_employees}",
        reason=f"企业{enterprise.get('enterprise_name')}提交{req.report_month}月度调查数据",
        ip_address=current_user.get("ip_address"),
        user_agent=current_user.get("user_agent")
    )
    
    return {
        "status": "success",
        "message": "调查数据提交成功",
        "survey_id": survey_id,
        "data": survey_data,
        "validation": {
            "is_valid": True,
            "warnings": validation_result.warnings,
            "suggestions": validation_result.suggestions
        },
        "audit_log": {
            "operation": "SURVEY_SUBMIT",
            "user": current_user.get("username"),
            "time": survey_data["submit_time"]
        }
    }


@router.get("/survey/validate",
            summary="预校验调查数据",
            dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def validate_survey_data(
    req: SurveyDataRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    预校验调查数据，不实际提交
    
    权限要求: ENT_SUBMIT (企业数据填报)
    
    功能:
    - 动态校验(BR-01): 完整的数据校验
    - 返回校验结果和建议
    """
    validation_result = dynamic_validator.validate_all(req.dict())
    
    return {
        "status": "success",
        "validation": {
            "is_valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "suggestions": validation_result.suggestions
        },
        "message": "预校验完成" if validation_result.is_valid else "数据存在错误，请修正后重新提交"
    }


@router.get("/survey/list",
            summary="查询企业调查数据列表",
            dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def get_enterprise_surveys(
    enterprise_id: int = Query(..., description="企业ID"),
    year: Optional[int] = Query(None, description="查询年份"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: dict = Depends(get_current_user)
):
    """
    查询企业的调查数据列表
    
    权限要求: ENT_SUBMIT (企业数据填报)
    """
    surveys = []
    
    for key, data in t_survey_data.items():
        if data.get("enterprise_id") == enterprise_id:
            # 年份筛选
            if year and not data.get("report_month", "").startswith(str(year)):
                continue
            
            # 状态筛选
            if status and data.get("status") != status:
                continue
            
            surveys.append(data)
    
    # 按提交时间倒序排列
    surveys = sorted(surveys, key=lambda x: x.get("submit_time", ""), reverse=True)
    
    return {
        "enterprise_id": enterprise_id,
        "total": len(surveys),
        "surveys": surveys
    }


@router.get("/survey/{survey_id}",
            summary="获取单条调查数据详情",
            dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def get_survey_detail(
    survey_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定调查数据的详细信息
    
    权限要求: ENT_SUBMIT (企业数据填报)
    """
    for key, data in t_survey_data.items():
        if data.get("survey_id") == survey_id:
            # 检查权限：只能查看自己企业的数据
            if data.get("enterprise_id") != current_user.get("user_id"):
                # 这里简化处理，实际应该根据企业ID判断
                pass
            
            return {
                "survey": data
            }
    
    raise HTTPException(status_code=404, detail="未找到指定的调查数据")


@router.put("/survey/{survey_id}",
            summary="更新调查数据",
            dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def update_survey_data(
    survey_id: int,
    req: SurveyDataUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新调查数据（仅限未审核的数据）
    
    权限要求: ENT_SUBMIT (企业数据填报)
    """
    for key, data in t_survey_data.items():
        if data.get("survey_id") == survey_id:
            # 检查是否可以修改
            if data.get("audit_status") == "approved":
                raise HTTPException(
                    status_code=400,
                    detail="该调查数据已审核通过，无法修改"
                )
            
            if data.get("audit_status") == "rejected":
                raise HTTPException(
                    status_code=400,
                    detail="该调查数据已被退回，请联系管理员"
                )
            
            # 记录修改前的数据
            old_data = data.copy()
            
            # 更新字段
            update_dict = req.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if value is not None:
                    data[field] = value
            
            # 重新计算失业率
            if 'employed_count' in update_dict or 'unemployed_count' in update_dict or 'total_employees' in update_dict:
                total = data.get("total_employees", 0)
                unemployed = data.get("unemployed_count", 0)
                data["unemployment_rate"] = round((unemployed / total) * 100, 2) if total > 0 else 0
            
            # 更新修改时间
            data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["update_user_id"] = current_user.get("user_id")
            
            # 审计留痕
            audit_logger.log_operation(
                user_id=current_user.get("user_id"),
                operation_type="SURVEY_UPDATE",
                table_name="t_survey_data",
                record_id=survey_id,
                old_value=str(old_data),
                new_value=str(data),
                reason=f"更新调查数据",
                ip_address=current_user.get("ip_address"),
                user_agent=current_user.get("user_agent")
            )
            
            return {
                "status": "success",
                "message": "调查数据更新成功",
                "survey": data
            }
    
    raise HTTPException(status_code=404, detail="未找到指定的调查数据")


@router.delete("/survey/{survey_id}",
               summary="删除调查数据",
               dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def delete_survey_data(
    survey_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    删除调查数据（仅限未审核的数据）
    
    权限要求: ENT_SUBMIT (企业数据填报)
    """
    for key, data in t_survey_data.items():
        if data.get("survey_id") == survey_id:
            # 检查是否可以删除
            if data.get("audit_status") == "approved":
                raise HTTPException(
                    status_code=400,
                    detail="该调查数据已审核通过，无法删除"
                )
            
            # 记录删除前的数据
            old_value = str(data)
            
            # 删除数据
            del t_survey_data[key]
            
            # 审计留痕
            audit_logger.log_operation(
                user_id=current_user.get("user_id"),
                operation_type="SURVEY_DELETE",
                table_name="t_survey_data",
                record_id=survey_id,
                old_value=old_value,
                new_value="",
                reason=f"删除调查数据",
                ip_address=current_user.get("ip_address"),
                user_agent=current_user.get("user_agent")
            )
            
            return {
                "status": "success",
                "message": "调查数据删除成功"
            }
    
    raise HTTPException(status_code=404, detail="未找到指定的调查数据")


@router.get("/survey/statistics",
            summary="获取调查统计数据",
            dependencies=[Depends(PermissionChecker("ENT_SUBMIT"))])
async def get_survey_statistics(
    survey_period_id: int = Query(..., description="调查期ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取调查数据的统计信息
    
    权限要求: ENT_SUBMIT (企业数据填报)
    """
    period = t_survey_period.get(survey_period_id)
    if not period:
        raise HTTPException(status_code=404, detail="未找到指定的调查期")
    
    # 筛选该调查期的数据
    period_surveys = [
        data for data in t_survey_data.values()
        if data.get("survey_period_id") == survey_period_id
    ]
    
    # 计算统计数据
    total_enterprises = len(period_surveys)
    total_employees = sum(data.get("total_employees", 0) for data in period_surveys)
    total_employed = sum(data.get("employed_count", 0) for data in period_surveys)
    total_unemployed = sum(data.get("unemployed_count", 0) for data in period_surveys)
    
    average_unemployment_rate = (
        sum(data.get("unemployment_rate", 0) for data in period_surveys) / total_enterprises
        if total_enterprises > 0 else 0
    )
    
    # 行业统计
    industry_stats = {}
    for data in period_surveys:
        industry = data.get("industry_type", "未知")
        if industry not in industry_stats:
            industry_stats[industry] = {
                "count": 0,
                "total_employees": 0,
                "total_unemployed": 0
            }
        industry_stats[industry]["count"] += 1
        industry_stats[industry]["total_employees"] += data.get("total_employees", 0)
        industry_stats[industry]["total_unemployed"] += data.get("unemployed_count", 0)
    
    return {
        "survey_period": period.get("period_name"),
        "statistics": {
            "total_enterprises": total_enterprises,
            "total_employees": total_employees,
            "total_employed": total_employed,
            "total_unemployed": total_unemployed,
            "average_unemployment_rate": round(average_unemployment_rate, 2)
        },
        "industry_statistics": industry_stats,
        "survey_count": len(period_surveys)
    }