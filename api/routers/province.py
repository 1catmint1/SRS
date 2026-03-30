from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.dependencies import PermissionChecker, get_current_user
from schemas.api_models import AuditFilingRequest
from db.mock_db import t_enterprise_info, t_operation_log

router = APIRouter(prefix="/province", tags=["2. 省级管理业务流"])


@router.post("/audit-filing",
             summary="执行省级企业备案审批",
             dependencies=[Depends(PermissionChecker("PRO_AUDIT"))])
async def audit_enterprise_filing(req: AuditFilingRequest, current_user: dict = Depends(get_current_user)):
    ent = t_enterprise_info.get(req.enterprise_id)
    if not ent:
        raise HTTPException(status_code=404, detail="未能在数据库中找到该企业记录")

    if ent["filing_status"] != 0:
        raise HTTPException(status_code=400, detail="该企业当前并非处于【待备案】状态，无法进行审批")

    old_status = ent["filing_status"]

    if req.action == "APPROVE":
        new_status = 1
        op_type = "FILING_APPROVE"
    elif req.action == "REJECT":
        if not req.reason or not req.reason.strip():
            raise HTTPException(status_code=400, detail="触发红线规则：执行备案退回操作必须填写具体原因！")
        new_status = 2
        op_type = "FILING_REJECT"
    else:
        raise HTTPException(status_code=400, detail="无法识别的审批动作，请输入 APPROVE 或 REJECT")

    ent["filing_status"] = new_status

    log_entry = {
        "user_id": current_user.get("user_id"),
        "operation_type": op_type,
        "table_name": "t_enterprise_info",
        "record_id": req.enterprise_id,
        "old_value": str(old_status),
        "new_value": str(new_status),
        "reason": req.reason if req.action == "REJECT" else "省级审核通过",
        "operation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    t_operation_log.append(log_entry)

    return {
        "status": "success",
        "msg": f"审批流程结束：企业【{ent['enterprise_name']}】已被" + ("通过" if req.action == "APPROVE" else "退回"),
        "current_status": new_status,
        "audit_log": log_entry
    }