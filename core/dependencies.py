from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from core.security import SECRET_KEY, ALGORITHM
from db.mock_db import ROLE_PERMISSIONS, PERMISSIONS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="您的认证凭证已失效，请重新登录")

class PermissionChecker:
    def __init__(self, required_perm: str):
        self.required_perm = required_perm

    def __call__(self, user: dict = Depends(get_current_user)):
        role_id = user.get("role_id")
        if self.required_perm not in ROLE_PERMISSIONS.get(role_id, []):
            raise HTTPException(
                status_code=403,
                detail=f"越权拦截：您的角色缺少【{PERMISSIONS.get(self.required_perm, '未知')}】权限，禁止操作！"
            )
        return user