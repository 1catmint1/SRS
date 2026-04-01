"""
API测试配置文件
"""
import os

# API基础URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_PREFIX = "/api/v1"

# 测试用户账号
TEST_USERS = {
    "admin": {
        "username": "admin",
        "password": "password123",
        "role": "省级管理员"
    },
    "city_admin": {
        "username": "city_admin",
        "password": "password123",
        "role": "市级审核员"
    },
    "enterprise": {
        "username": "enterprise",
        "password": "password123",
        "role": "企业用户"
    }
}

# 测试数据
TEST_ENTERPRISE_ID = 1001
TEST_SURVEY_PERIOD_ID = 1

# 测试调查数据
TEST_SURVEY_DATA = {
    "survey_period_id": 1,
    "enterprise_id": 1001,
    "report_month": "2026-03",
    "total_employees": 1200,
    "employed_count": 1150,
    "unemployed_count": 50,
    "new_employees": 10,
    "lost_employees": 5,
    "full_time_employees": 1000,
    "part_time_employees": 150,
    "contract_employees": 50,
    "total_payroll": 3600000.0,
    "average_salary": 3000.0,
    "industry_type": "制造业",
    "business_scale": "中型",
    "contact_person": "张三",
    "contact_phone": "13800138000",
    "contact_email": "zhangsan@example.com",
    "remarks": "测试数据"
}
