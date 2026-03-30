from pydantic import BaseModel, Field
from typing import Optional

class AuditFilingRequest(BaseModel):
    enterprise_id: int = Field(..., description="需要审批的企业编号数字")
    action: str = Field(..., description="输入文本：APPROVE(通过) 或 REJECT(退回)")
    reason: Optional[str] = Field(None, description="若审批动作为 REJECT(退回)，则必须填写此项")