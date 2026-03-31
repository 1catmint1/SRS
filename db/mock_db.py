# 权限标识符定义
PERMISSIONS = {
    "ENT_SUBMIT": "企业数据填报",
    "CTY_AUDIT": "市级数据初审",
    "PRO_AUDIT": "省级报表终审",
    "PRO_ADMIN": "省级系统管理"
}

# 模拟角色权限表
ROLE_PERMISSIONS = {
    1: ["PRO_AUDIT", "PRO_ADMIN"], # 省级管理员
    2: ["CTY_AUDIT"],              # 市级审核员
    3: ["ENT_SUBMIT"]              # 企业用户
}

# 模拟用户数据库（使用预计算的密码哈希）
USER_DATABASE = {
    "admin": {
        "user_id": 1,
        "username": "admin",
        "password_hash": "pbkdf2_sha256$260000$random_salt$password_hash_value",
        "role_id": 1,
        "role_name": "省级管理员",
        "full_name": "系统管理员",
        "is_active": True
    },
    "city_admin": {
        "user_id": 2,
        "username": "city_admin",
        "password_hash": "pbkdf2_sha256$260000$random_salt$password_hash_value",
        "role_id": 2,
        "role_name": "市级审核员",
        "full_name": "昆明市审核员",
        "is_active": True
    },
    "enterprise": {
        "user_id": 3,
        "username": "enterprise",
        "password_hash": "pbkdf2_sha256$260000$random_salt$password_hash_value",
        "role_id": 3,
        "role_name": "企业用户",
        "full_name": "某制造企业",
        "is_active": True
    }
}

# 初始化用户密码哈希的函数
def initialize_user_passwords():
    """初始化用户密码哈希"""
    from core.security import get_password_hash
    
    password_hash = get_password_hash("password123")
    
    for username in USER_DATABASE:
        USER_DATABASE[username]["password_hash"] = password_hash

# 在模块加载时初始化密码
initialize_user_passwords()

# 模拟登录失败记录缓存
login_attempts = {}

# 模拟企业信息表 t_enterprise_info
t_enterprise_info = {
    1001: {"enterprise_name": "昆明市某制造企业", "filing_status": 0},
    1002: {"enterprise_name": "大理州某服务企业", "filing_status": 1},
    1003: {"enterprise_name": "曲靖市某科技企业", "filing_status": 0},
    1004: {"enterprise_name": "玉溪市某农业企业", "filing_status": 2},
    1005: {"enterprise_name": "保山市某建材企业", "filing_status": 0}
}

# 模拟底层操作审计日志表 t_operation_log
t_operation_log = []

# 模拟调查期配置表 t_survey_period
t_survey_period = {
    1: {
        "period_id": 1,
        "period_name": "2026年第一季度",
        "start_date": "2026-01-01",
        "end_date": "2026-03-31",
        "status": "active"  # active, closed
    },
    2: {
        "period_id": 2,
        "period_name": "2026年第二季度",
        "start_date": "2026-04-01",
        "end_date": "2026-06-30",
        "status": "pending"
    }
}

# 模拟调查数据表 t_survey_data
t_survey_data = {}