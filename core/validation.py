from typing import List, Dict, Any
from schemas.survey_models import ValidationResult
import re


class DynamicValidator:
    """动态校验器 - 实现BR-01动态校验功能"""
    
    # 基础校验规则
    BASIC_RULES = {
        'total_employees': {
            'min': 1,
            'max': 100000,
            'message': '员工总数必须在1-100000之间'
        },
        'employed_count': {
            'min': 0,
            'max': 100000,
            'message': '就业人数必须在0-100000之间'
        },
        'unemployed_count': {
            'min': 0,
            'max': 100000,
            'message': '失业人数必须在0-100000之间'
        },
        'total_payroll': {
            'min': 0,
            'max': 1000000000,
            'message': '薪资总额必须在0-10亿之间'
        },
        'average_salary': {
            'min': 1000,
            'max': 1000000,
            'message': '平均薪资必须在1000-100万之间'
        }
    }
    
    # 业务逻辑校验规则
    BUSINESS_RULES = {
        'employment_balance': '就业人数 + 失业人数 = 员工总数',
        'unemployment_rate': '失业率 = 失业人数 / 员工总数',
        'salary_consistency': '平均薪资应该合理反映企业规模',
        'data_consistency': '新增就业人数和失业人数应该合理'
    }
    
    @staticmethod
    def validate_basic_rules(data: Dict[str, Any]) -> ValidationResult:
        """基础规则校验"""
        errors = []
        warnings = []
        
        # 校验数值范围
        for field, rules in DynamicValidator.BASIC_RULES.items():
            if field in data:
                value = data[field]
                if value < rules['min'] or value > rules['max']:
                    errors.append(f"{field}: {rules['message']} (当前值: {value})")
        
        # 校验必填字段
        required_fields = [
            'survey_period_id', 'enterprise_id', 'report_month',
            'total_employees', 'employed_count', 'unemployed_count',
            'total_payroll', 'average_salary', 'industry_type',
            'business_scale', 'contact_person', 'contact_phone'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"缺少必填字段: {field}")
        
        # 校验联系方式格式
        if 'contact_phone' in data:
            phone = data['contact_phone']
            if not re.match(r'^1[3-9]\d{9}$', str(phone)):
                errors.append("联系电话格式不正确")
        
        if 'contact_email' in data and data['contact_email']:
            email = data['contact_email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("邮箱格式不正确")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_business_rules(data: Dict[str, Any]) -> ValidationResult:
        """业务逻辑校验"""
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 就业平衡校验: 就业人数 + 失业人数 = 员工总数
        total = data.get('total_employees', 0)
        employed = data.get('employed_count', 0)
        unemployed = data.get('unemployed_count', 0)
        
        if employed + unemployed != total:
            errors.append(
                f"就业平衡校验失败: 就业人数({employed}) + 失业人数({unemployed}) "
                f"不等于员工总数({total})"
            )
            suggestions.append("请检查就业人数和失业人数的统计是否正确")
        
        # 2. 失业率校验
        if total > 0:
            unemployment_rate = (unemployed / total) * 100
            
            if unemployment_rate > 50:
                warnings.append(f"失业率过高: {unemployment_rate:.2f}%")
                suggestions.append("建议核实失业人员情况，或检查数据填报是否正确")
            
            if unemployment_rate < 0:
                errors.append("失业率不能为负数")
            
            if unemployment_rate == 0 and unemployed > 0:
                errors.append("失业率计算异常")
        
        # 3. 薪资一致性校验
        total_payroll = data.get('total_payroll', 0)
        average_salary = data.get('average_salary', 0)
        total_employees = data.get('total_employees', 0)
        
        if total_employees > 0:
            calculated_avg = total_payroll / total_employees
            salary_diff = abs(calculated_avg - average_salary)
            salary_diff_percent = (salary_diff / average_salary) * 100 if average_salary > 0 else 0
            
            if salary_diff_percent > 20:
                warnings.append(
                    f"薪资数据可能不一致: 计算平均薪资({calculated_avg:.2f}) "
                    f"与填报平均薪资({average_salary:.2f})差异较大"
                )
                suggestions.append("请核实薪资总额和平均薪资的填报是否正确")
        
        # 4. 数据一致性校验
        new_employees = data.get('new_employees', 0)
        lost_employees = data.get('lost_employees', 0)
        
        if new_employees < 0 or lost_employees < 0:
            errors.append("新增就业人数和失业人数不能为负数")
        
        if new_employees > total:
            warnings.append(
                f"新增就业人数({new_employees})超过员工总数({total})，请确认数据正确性"
            )
        
        if lost_employees > employed:
            warnings.append(
                f"失业人数({lost_employees})超过就业人数({employed})，请确认数据正确性"
            )
        
        # 5. 企业规模合理性校验
        business_scale = data.get('business_scale', '')
        industry_type = data.get('industry_type', '')
        
        scale_employee_ranges = {
            '微型': (1, 10),
            '小型': (11, 100),
            '中型': (101, 500),
            '大型': (501, 1000),
            '超大型': (1001, float('inf'))
        }
        
        if business_scale in scale_employee_ranges:
            min_emp, max_emp = scale_employee_ranges[business_scale]
            if total < min_emp or total > max_emp:
                warnings.append(
                    f"企业规模({business_scale})与员工总数({total})不匹配"
                )
                suggestions.append(
                    f"根据员工总数，建议的企业规模应为: "
                    f"{DynamicValidator._get_suggested_scale(total)}"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    @staticmethod
    def _get_suggested_scale(total_employees: int) -> str:
        """根据员工总数建议企业规模"""
        if total <= 10:
            return "微型"
        elif total <= 100:
            return "小型"
        elif total <= 500:
            return "中型"
        elif total <= 1000:
            return "大型"
        else:
            return "超大型"
    
    @staticmethod
    def validate_survey_period(survey_period_id: int, report_month: str) -> ValidationResult:
        """校验调查期和填报月份是否匹配"""
        from db.mock_db import t_survey_period
        
        errors = []
        warnings = []
        
        period = t_survey_period.get(survey_period_id)
        if not period:
            errors.append(f"未找到调查期ID: {survey_period_id}")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 检查调查期状态
        if period.get('status') != 'active':
            errors.append(f"调查期【{period.get('period_name')}】未激活，无法填报")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 检查填报月份是否在调查期范围内
        try:
            from datetime import datetime
            report_date = datetime.strptime(report_month, "%Y-%m")
            start_date = datetime.strptime(period['start_date'], "%Y-%m-%d")
            end_date = datetime.strptime(period['end_date'], "%Y-%m-%d")
            
            if report_date < start_date or report_date > end_date:
                warnings.append(
                    f"填报月份({report_month})不在调查期时间范围内 "
                    f"({period['start_date']} 至 {period['end_date']})"
                )
        except ValueError as e:
            errors.append(f"日期格式错误: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_all(data: Dict[str, Any]) -> ValidationResult:
        """执行所有校验"""
        all_errors = []
        all_warnings = []
        all_suggestions = []
        
        # 基础规则校验
        basic_result = DynamicValidator.validate_basic_rules(data)
        all_errors.extend(basic_result.errors)
        all_warnings.extend(basic_result.warnings)
        all_suggestions.extend(basic_result.suggestions)
        
        # 业务逻辑校验
        business_result = DynamicValidator.validate_business_rules(data)
        all_errors.extend(business_result.errors)
        all_warnings.extend(business_result.warnings)
        all_suggestions.extend(business_result.suggestions)
        
        # 调查期校验
        if 'survey_period_id' in data and 'report_month' in data:
            period_result = DynamicValidator.validate_survey_period(
                data['survey_period_id'],
                data['report_month']
            )
            all_errors.extend(period_result.errors)
            all_warnings.extend(period_result.warnings)
            all_suggestions.extend(period_result.suggestions)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            suggestions=all_suggestions
        )


# 创建全局校验器实例
dynamic_validator = DynamicValidator()