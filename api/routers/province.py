from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.dependencies import PermissionChecker, get_current_user
from core.audit import audit_logger, data_protection
from schemas.api_models import AuditFilingRequest
from db.mock_db import t_enterprise_info, t_operation_log

router = APIRouter(prefix="/province", tags=["2. 省级管理业务流"])


@router.post("/audit-filing",
             summary="执行省级企业备案审批",
             dependencies=[Depends(PermissionChecker("PRO_AUDIT"))])
async def audit_enterprise_filing(req: AuditFilingRequest, current_user: dict = Depends(get_current_user)):
    """企业备案审批接口，集成强制审计留痕和数据保护"""
    # 1. 检查企业是否存在
    ent = t_enterprise_info.get(req.enterprise_id)
    if not ent:
        raise HTTPException(status_code=404, detail="未能在数据库中找到该企业记录")

    # 2. 检查企业当前状态
    if ent["filing_status"] != 0:
        raise HTTPException(status_code=400, detail="该企业当前并非处于【待备案】状态，无法进行审批")

    # 3. 数据完整性检查
    is_complete, error_msg = data_protection.check_data_integrity("t_enterprise_info", ent)
    if not is_complete:
        raise HTTPException(status_code=400, detail=f"数据完整性检查失败: {error_msg}")

    # 4. 记录修改前的状态
    old_status = ent["filing_status"]
    old_data = ent.copy()

    # 5. 准备新的状态
    if req.action == "APPROVE":
        new_status = 1
        op_type = "FILING_APPROVE"
        reason = "省级审核通过"
    elif req.action == "REJECT":
        if not req.reason or not req.reason.strip():
            raise HTTPException(status_code=400, detail="触发红线规则：执行备案退回操作必须填写具体原因！")
        new_status = 2
        op_type = "FILING_REJECT"
        reason = req.reason
    else:
        raise HTTPException(status_code=400, detail="无法识别的审批动作，请输入 APPROVE 或 REJECT")

    # 6. 验证数据变更合法性
    new_data = ent.copy()
    new_data["filing_status"] = new_status
    
    user_role = current_user.get("role_name", "")
    is_valid, error_message = data_protection.validate_data_change(
        table_name="t_enterprise_info",
        old_data=old_data,
        new_data=new_data,
        user_role=user_role
    )
    
    if not is_valid:
        raise HTTPException(status_code=403, detail=f"数据修改保护拦截: {error_message}")

    # 7. 执行状态更新
    ent["filing_status"] = new_status

    # 8. 强制审计留痕 - 使用增强的审计记录器
    log_entry = audit_logger.log_operation(
        user_id=current_user.get("user_id"),
        operation_type=op_type,
        table_name="t_enterprise_info",
        record_id=req.enterprise_id,
        old_value=f"status={old_status}",
        new_value=f"status={new_status}",
        reason=reason,
        ip_address=current_user.get("ip_address"),  # 如果有IP信息
        user_agent=current_user.get("user_agent")   # 如果有用户代理信息
    )

    return {
        "status": "success",
        "msg": f"审批流程结束：企业【{ent['enterprise_name']}】已被" + ("通过" if req.action == "APPROVE" else "退回"),
        "current_status": new_status,
        "audit_log": log_entry,
        "data_protection": {
            "integrity_check": "passed",
            "modification_validation": "passed",
            "audit_logging": "enabled"
        }
    }