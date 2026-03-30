# 云南省企业就业失业数据采集系统 - API交互文档

## 项目概述

**项目名称**: 云南省企业就业失业数据采集系统  
**项目版本**: v0.5 Alpha (敏捷迭代版本)  
**技术栈**: Python + FastAPI + JWT认证  
**项目目标**: 建立企业就业失业数据三级流转体系(企业端-市级-省级)

---

## 系统架构

### 项目结构
```
SRS/
├── main.py                 # FastAPI应用入口
├── api/                    # API路由模块
│   └── routers/
│       ├── auth.py        # 身份认证路由
│       └── province.py    # 省级业务路由
├── core/                   # 核心功能模块
│   ├── dependencies.py    # 依赖注入和权限检查
│   ├── security.py        # 安全认证(JWT、密码加密)
│   └── swagger_ui.py     # 自定义Swagger界面
├── db/                     # 数据库模块
│   └── mock_db.py        # 模拟数据库
└── schemas/                # 数据模型
    └── api_models.py     # API数据模型
```

### 技术架构
- **Web框架**: FastAPI 0.135.2
- **ASGI服务器**: Uvicorn 0.42.0
- **数据验证**: Pydantic 2.11.9
- **身份认证**: JWT (python-jose)
- **密码加密**: Passlib + PBKDF2_SHA256
- **API文档**: 自定义SwaggerUI (全中文界面)

---

## API接口文档

### 1. 身份认证中心 (Identity Authentication)

#### 1.1 用户登录与签发令牌

**接口地址**: `POST /api/v1/auth/login`  
**功能描述**: 企业用户、市级审核员、省级管理员登录系统并获取访问令牌  
**权限要求**: 无需认证  

**请求参数** (OAuth2 Password模式):
```
username: string (必填) - 登录用户名
password: string (必填) - 登录密码
```

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

**响应示例** (成功):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**响应示例** (失败):
```json
{
  "detail": "对不起，您输入的账号或密码不正确"
}
```

**测试账号**:
- 省级管理员: `admin` / `password123` (权限: PRO_AUDIT, PRO_ADMIN)
- 市级审核员: `city_admin` / `password123` (权限: CTY_AUDIT)
- 企业用户: `enterprise` / `password123` (权限: ENT_SUBMIT)

---

### 2. 省级管理业务流 (Provincial Management)

#### 2.1 省级企业备案审批

**接口地址**: `POST /api/v1/province/audit-filing`  
**功能描述**: 省级管理员对企业备案申请进行审批(通过/退回)  
**权限要求**: PRO_AUDIT (省级审核权限)  
**认证方式**: Bearer Token  

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "enterprise_id": 1001,
  "action": "APPROVE",
  "reason": null
}
```

**参数说明**:
- `enterprise_id` (int, 必填): 企业编号
- `action` (string, 必填): 审批动作,可选值:
  - `APPROVE`: 通过备案
  - `REJECT`: 退回备案
- `reason` (string, 可选): 退回原因(当action为REJECT时必填)

**请求示例** (通过):
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/province/audit-filing" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_id": 1001,
    "action": "APPROVE"
  }'
```

**请求示例** (退回):
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/province/audit-filing" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_id": 1001,
    "action": "REJECT",
    "reason": "企业信息不完整，需要补充相关材料"
  }'
```

**响应示例** (成功):
```json
{
  "status": "success",
  "msg": "审批流程结束：企业【昆明市某制造企业】已被通过",
  "current_status": 1,
  "audit_log": {
    "user_id": 1,
    "operation_type": "FILING_APPROVE",
    "table_name": "t_enterprise_info",
    "record_id": 1001,
    "old_value": "0",
    "new_value": "1",
    "reason": "省级审核通过",
    "operation_time": "2026-03-30 20:15:30"
  }
}
```

**响应示例** (失败 - 企业不存在):
```json
{
  "detail": "未能在数据库中找到该企业记录"
}
```

**响应示例** (失败 - 状态不正确):
```json
{
  "detail": "该企业当前并非处于【待备案】状态，无法进行审批"
}
```

**响应示例** (失败 - 退回未填原因):
```json
{
  "detail": "触发红线规则：执行备案退回操作必须填写具体原因！"
}
```

**响应示例** (失败 - 权限不足):
```json
{
  "detail": "越权拦截：您的角色缺少【省级报表终审】权限，禁止操作！"
}
```

---

## 数据字典

### 企业备案状态 (filing_status)
- `0`: 待备案 (Pending)
- `1`: 已备案 (Approved)
- `2`: 已退回 (Rejected)

### 操作类型 (operation_type)
- `FILING_APPROVE`: 备案通过
- `FILING_REJECT`: 备案退回

### 权限标识符
- `PRO_AUDIT`: 省级报表终审
- `PRO_ADMIN`: 省级系统管理
- `CTY_AUDIT`: 市级数据初审
- `ENT_SUBMIT`: 企业数据填报

### 角色权限映射
- 角色ID `1` (省级管理员): PRO_AUDIT, PRO_ADMIN
- 角色ID `2` (市级审核员): CTY_AUDIT
- 角色ID `3` (企业用户): ENT_SUBMIT

---

## 安全机制

### JWT认证流程
1. 用户通过 `/api/v1/auth/login` 登录获取访问令牌
2. 在后续请求的Header中携带: `Authorization: Bearer {token}`
3. 令牌有效期: 120分钟
4. 令牌过期后需重新登录

### 密码安全
- 加密算法: PBKDF2_SHA256
- 密码强度要求: 建议包含大小写字母、数字、特殊字符

### 权限控制
- 基于角色的访问控制(RBAC)
- 接口级别的权限检查
- 越权操作自动拦截

### 审计留痕
- 所有数据修改操作自动记录审计日志
- 日志包含: 操作用户、操作类型、操作时间、修改前后值、操作原因

---

## 部署说明

### 环境要求
- Python 3.8+
- 依赖库: fastapi, uvicorn, pydantic, python-jose, passlib, python-multipart

### 启动方式

**方式1: 直接运行**
```bash
python main.py
```

**方式2: Uvicorn启动**
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 访问地址
- API文档: http://127.0.0.1:8000/docs
- OpenAPI规范: http://127.0.0.1:8000/openapi.json

---

## 测试指南

### 1. 获取访问令牌
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

### 2. 测试企业备案审批
```bash
# 复制上面获取的access_token
curl -X POST "http://127.0.0.1:8000/api/v1/province/audit-filing" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_id": 1001,
    "action": "APPROVE"
  }'
```

### 3. 测试权限拦截
使用市级审核员账号尝试访问省级接口,应该返回403权限不足错误。

---

## 开发进度

### 已完成功能 (v0.5 Alpha)
- ✅ FastAPI基础框架搭建
- ✅ JWT登录鉴权机制
- ✅ RBAC权限拦截器
- ✅ 企业备案审批API
- ✅ 审计留痕功能
- ✅ 自定义SwaggerUI文档界面

### 待开发功能
- 🔲 企业基础信息备案API
- 🔲 月度调查期填报API
- 🔲 市级初审流转
- 🔲 省市级报表终审
- 🔲 数据统计分析
- 🔲 Streamlit可视化大屏

---

## 联系方式

**项目负责人**: 杨海天 (PM)  
**技术架构**: FastAPI + JWT + RBAC  
**项目状态**: v0.5 Alpha 开发中  

**文档更新时间**: 2026年3月30日