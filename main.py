from fastapi import FastAPI
from core.swagger_ui import get_custom_swagger_ui_html
from api.routers import auth, province, admin, audit, enterprise, notification, analysis, national_system

app = FastAPI(
    title="云南省企业就业失业数据采集系统",
    description="后端敏捷迭代 v0.5：纯英文底层逻辑 + 纯中文展现界面",
    docs_url=None,
    redoc_url=None
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_custom_swagger_ui_html()

# 注册各个模块的路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(province.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(enterprise.router, prefix="/api/v1")
app.include_router(notification.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(national_system.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)