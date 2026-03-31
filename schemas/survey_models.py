from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmploymentStatus(str, Enum):
    """就业状态枚举"""
    EMPLOYED = "employed"      # 就业
    UNEMPLOYED = "unemployed"  # 失业
    PARTIAL = "partial"        # 部分就业


class SurveyDataRequest(BaseModel):
    """月度调查期填报数据请求模型"""
    
    # 基本信息
    survey_period_id: int = Field(..., description="调查期ID")
    enterprise_id: int = Field(..., description="企业ID")
    report_month: str = Field(..., description="填报月份 (YYYY-MM)")
    
    # 就业数据
    total_employees: int = Field(..., ge=0, description="员工总数")
    employed_count: int = Field(..., ge=0, description="就业人数")
    unemployed_count: int = Field(..., ge=0, description="失业人数")
    new_employees: int = Field(0, ge=0, description="本月新增就业人数")
    lost_employees: int = Field(0, ge=0, description="本月失业人数")
    
    # 详细分类
    full_time_employees: int = Field(0, ge=0, description="全职员工数")
    part_time_employees: int = Field(0, ge=0, description="兼职员工数")
    contract_employees: int = Field(0, ge=0, description="合同工数")
    
    # 薪资数据
    total_payroll: float = Field(..., ge=0, description="薪资总额")
    average_salary: float = Field(..., ge=0, description="平均薪资")
    
    # 行业信息
    industry_type: str = Field(..., description="行业类型")
    business_scale: str = Field(..., description="企业规模")
    
    # 联系信息
    contact_person: str = Field(..., description="联系人")
    contact_phone: str = Field(..., description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    
    # 备注
    remarks: Optional[str] = Field(None, description="备注信息")
    
    @validator('report_month')
    def validate_report_month(cls, v):
        """验证填报月份格式"""
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("填报月份格式不正确，请使用 YYYY-MM 格式")
    
    @validator('total_employees')
    def validate_total_employees(cls, v, values):
        """验证员工总数逻辑"""
        if 'employed_count' in values and 'unemployed_count' in values:
            if v != values['employed_count'] + values['unemployed_count']:
                raise ValueError("员工总数必须等于就业人数与失业人数之和")
        return v
    
    @validator('contact_phone')
    def validate_contact_phone(cls, v):
        """验证联系电话格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("联系电话格式不正确")
        return v
    
    @validator('contact_email')
    def validate_contact_email(cls, v):
        """验证邮箱格式"""
        if v:
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError("邮箱格式不正确")
        return v


class SurveyDataResponse(BaseModel):
    """调查数据响应模型"""
    survey_id: int
    survey_period_id: int
    enterprise_id: int
    enterprise_name: str
    report_month: str
    total_employees: int
    employed_count: int
    unemployed_count: int
    unemployment_rate: float
    new_employees: int
    lost_employees: int
    total_payroll: float
    average_salary: float
    industry_type: str
    business_scale: str
    contact_person: str
    contact_phone: str
    submit_time: str
    status: str
    audit_status: str


class SurveyDataUpdate(BaseModel):
    """调查数据更新模型"""
    total_employees: Optional[int] = Field(None, ge=0)
    employed_count: Optional[int] = Field(None, ge=0)
    unemployed_count: Optional[int] = Field(None, ge=0)
    new_employees: Optional[int] = Field(None, ge=0)
    lost_employees: Optional[int] = Field(None, ge=0)
    total_payroll: Optional[float] = Field(None, ge=0)
    average_salary: Optional[float] = Field(None, ge=0)
    remarks: Optional[str] = None


class ValidationResult(BaseModel):
    """动态校验结果模型"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []


class SurveyStatistics(BaseModel):
    """调查统计数据模型"""
    total_enterprises: int
    total_employees: int
    total_employed: int
    total_unemployed: int
    average_unemployment_rate: float
    industry_statistics: dict
    region_statistics: dict