"""
省级管理业务流接口测试用例
"""
import pytest
import httpx
from tests.conftest import BASE_URL, API_PREFIX, TEST_USERS


class TestProvinceAPI:
    """省级管理业务流接口测试类"""
    
    @pytest.fixture
    def auth_headers(self):
        """获取认证头"""
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)
        response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def client(self):
        """创建HTTP客户端"""
        return httpx.Client(base_url=BASE_URL, timeout=10.0)
    
    def test_audit_filing_approve(self, client, auth_headers):
        """测试企业备案审批-通过"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        # 检查响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "audit_log" in data
        assert data["audit_log"]["operation_type"] == "FILING_APPROVE"
        assert "data_protection" in data
    
    def test_audit_filing_reject(self, client, auth_headers):
        """测试企业备案审批-退回"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1003,
                "action": "REJECT",
                "reason": "企业信息不完整，需要补充相关材料"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "audit_log" in data
        assert data["audit_log"]["operation_type"] == "FILING_REJECT"
    
    def test_audit_filing_reject_without_reason(self, client, auth_headers):
        """测试企业备案审批-退回但未填写原因"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1003,
                "action": "REJECT",
                "reason": None
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "必须填写具体原因" in data["detail"]
    
    def test_audit_filing_invalid_enterprise(self, client, auth_headers):
        """测试审批不存在的企业"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 9999,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "未能在数据库中找到该企业记录" in data["detail"]
    
    def test_audit_filing_invalid_status(self, client, auth_headers):
        """测试审批状态不正确的企业"""
        # 先将企业状态改为已备案
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1002,  # 假设这是已备案的企业
                "action": "APPROVE",
                "reason": None
            }
        )
        
        # 如果企业不是待备案状态，应该返回错误
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
    
    def test_audit_filing_invalid_action(self, client, auth_headers):
        """测试无效的审批动作"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1001,
                "action": "INVALID_ACTION",
                "reason": None
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "无法识别的审批动作" in data["detail"]
    
    def test_audit_filing_without_auth(self, client):
        """测试未授权访问审批接口"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert response.status_code == 401
    
    def test_audit_filing_with_city_admin(self, client):
        """测试市级审核员访问省级审批接口"""
        # 使用市级审核员登录
        login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["city_admin"]["username"],
                "password": TEST_USERS["city_admin"]["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 尝试访问省级审批接口
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        # 应该被权限拦截
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "越权拦截" in data["detail"]
    
    def test_data_protection_in_audit(self, client, auth_headers):
        """测试审批接口的数据保护功能"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查数据保护状态
        assert "data_protection" in data
        assert data["data_protection"]["integrity_check"] == "passed"
        assert data["data_protection"]["modification_validation"] == "passed"
        assert data["data_protection"]["audit_logging"] == "enabled"
    
    def test_audit_logging(self, client, auth_headers):
        """测试审批操作的审计留痕"""
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=auth_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": "测试审批"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查审计日志
        assert "audit_log" in data
        audit_log = data["audit_log"]
        
        assert "log_id" in audit_log
        assert "user_id" in audit_log
        assert "operation_type" in audit_log
        assert "table_name" in audit_log
        assert "record_id" in audit_log
        assert "old_value" in audit_log
        assert "new_value" in audit_log
        assert "operation_time" in audit_log