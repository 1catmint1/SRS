# 云南省企业就业失业数据采集系统

## 项目简介

本项目是基于FastAPI + Streamlit构建的企业就业失业数据采集与管理平台，实现企业数据的在线填报、三级审批流转、数据统计分析和可视化展示。

## 技术栈

- **后端框架**: FastAPI 0.135.2
- **前端可视化**: Streamlit 1.55.0
- **认证授权**: JWT + RBAC
- **数据验证**: Pydantic 2.11.9
- **ASGI服务器**: Uvicorn 0.42.0
- **密码加密**: Passlib + PBKDF2_SHA256

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd SRS

# 创建虚拟环境 (可选)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install fastapi uvicorn pydantic "python-jose[cryptography]" "passlib[bcrypt]" python-multipart streamlit pandas requests
```

### 3. 启动服务

```bash
# 启动FastAPI后端
python main.py

# 启动Streamlit前端 (新终端)
streamlit run dashboard.py
```

### 4. 访问系统

- **API文档**: http://127.0.0.1:8000/docs
- **可视化大屏**: http://127.0.0.1:8501

## 项目结构

```
SRS/
├── main.py                    # FastAPI应用入口
├── dashboard.py              # Streamlit可视化大屏
├── api/                      # API路由模块
│   └── routers/
│       ├── auth.py          # 身份认证路由
│       └── province.py      # 省级业务路由
├── core/                     # 核心功能模块
│   ├── dependencies.py      # 依赖注入和权限检查
│   ├── security.py          # 安全认证(JWT、密码加密)
│   └── swagger_ui.py       # 自定义Swagger界面
├── db/                       # 数据库模块
│   └── mock_db.py          # 模拟数据库
├── schemas/                  # 数据模型
│   └── api_models.py       # API数据模型
├── API交互文档.md           # API接口文档
├── 大作业交付材料.md        # 项目交付文档
└── README.md               # 项目说明文档
```

## 核心功能

### 1. 身份认证
- JWT令牌认证
- 基于角色的权限控制(RBAC)
- 密码安全加密

### 2. 企业管理
- 企业基础信息备案
- 企业信息查询与筛选
- 企业状态管理

### 3. 审批流程
- 三级审批流转 (企业-市级-省级)
- 在线审批操作
- 审批原因记录

### 4. 审计留痕
- 完整的操作日志
- 数据变更追踪
- 防篡改机制

### 5. 数据可视化
- 企业数据统计卡片
- 多维度数据分析
- 趋势图表展示

## API文档

### 用户登录
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=password123
```

### 企业备案审批
```bash
POST /api/v1/province/audit-filing
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "enterprise_id": 1001,
  "action": "APPROVE",
  "reason": null
}
```

详细API文档请访问: http://127.0.0.1:8000/docs

## 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 省级管理员 | admin | password123 | PRO_AUDIT, PRO_ADMIN |
| 市级审核员 | city_admin | password123 | CTY_AUDIT |
| 企业用户 | enterprise | password123 | ENT_SUBMIT |

## 开发进度

### v0.5 Alpha (当前版本)
- ✅ FastAPI基础框架
- ✅ JWT认证授权
- ✅ RBAC权限控制
- ✅ 企业备案审批API
- ✅ 审计留痕功能
- ✅ Streamlit可视化大屏

### 计划中功能
- 🔲 企业基础信息备案API
- 🔲 月度调查期填报API
- 🔲 市级初审流转
- 🔲 数据统计分析
- 🔲 趋势预测算法

## 安全机制

- **身份认证**: JWT令牌，有效期120分钟
- **密码安全**: PBKDF2_SHA256加密算法
- **权限控制**: 基于角色的访问控制
- **审计追踪**: 完整的操作日志记录
- **越权拦截**: 自动检测并拦截越权操作

## 文档

- [API交互文档](./API交互文档.md) - 详细的API接口说明
- [大作业交付材料](./大作业交付材料.md) - 项目完整交付文档

## 技术支持

**项目负责人**: 杨海天 (PM)  
**技术架构**: FastAPI + Streamlit + JWT  
**项目版本**: v0.5 Alpha  
**更新时间**: 2026年3月30日

## 许可证

本项目仅用于学习和教学目的。

---

**🎉 感谢使用云南省企业就业失业数据采集系统！**