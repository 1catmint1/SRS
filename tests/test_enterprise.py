"""
企业填报接口测试用例
"""
import pytest
import httpx
from tests.conftest import BASE_URL, API_PREFIX, TEST_USERS, TEST_SURVEY_DATA


class TestEnterpriseAPI:
    """企业填报接口测试类"""
    
    @pytest.fixture
    def auth_headers(self):
        """获取企业用户认证头"""
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)
        response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["enterprise"]["username"],
                "password": TEST_USERS["enterprise"]["password"]
            }
        )
        
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def admin_headers(self):
        """获取管理员认证头"""
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
    
    def test_submit_survey_data_success(self, client, auth_headers):
        """测试成功提交调查数据"""
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "survey_id" in data
        assert "data" in data
        assert "validation" in data
        assert "audit_log" in data
        
        # 检查数据
        survey_data = data["data"]
        assert survey_data["enterprise_id"] == TEST_SURVEY_DATA["enterprise_id"]
        assert survey_data["report_month"] == TEST_SURVEY_DATA["report_month"]
        assert survey_data["total_employees"] == TEST_SURVEY_DATA["total_employees"]
    
    def test_validate_survey_data_success(self, client, auth_headers):
        """测试预校验调查数据-成功"""
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "validation" in data
        assert data["validation"]["is_valid"] == True
    
    def test_validate_survey_data_with_errors(self, client, auth_headers):
        """测试预校验调查数据-有错误"""
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["total_employees"] = 1000
        invalid_data["employed_count"] = 800  # 不等于 total_employees - unemployed_count
        
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "validation" in data
        # 数据不合法，应该有错误
        assert not data["validation"]["is_valid"]
        assert len(data["validation"]["errors"]) > 0
    
    def test_submit_survey_data_invalid_phone(self, client, auth_headers):
        """测试提交无效手机号的调查数据"""
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["contact_phone"] = "1234567890"  # 无效的手机号
        
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        # 应该包含手机号格式错误
        error_detail = str(data["detail"])
        assert "联系电话" in error_detail or "phone" in error_detail.lower()
    
    def test_submit_survey_data_invalid_email(self, client, auth_headers):
        """测试提交无效邮箱的调查数据"""
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["contact_email"] = "invalid_email"  # 无效的邮箱
        
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_get_enterprise_surveys(self, client, auth_headers):
        """测试获取企业调查数据列表"""
        response = client.get(
            f"{API_PREFIX}/enterprise/survey/list",
            headers=auth_headers,
            params={"enterprise_id": TEST_SURVEY_DATA["enterprise_id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "enterprise_id" in data
        assert "total" in data
        assert "surveys" in data
    
    def test_get_survey_detail(self, client, auth_headers):
        """测试获取调查数据详情"""
        # 先提交一条数据
        submit_response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert submit_response.status_code == 200
        survey_id = submit_response.json()["survey_id"]
        
        # 获取详情
        response = client.get(
            f"{API_PREFIX}/enterprise/survey/{survey_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "survey" in data
        assert data["survey"]["survey_id"] == survey_id
    
    def test_update_survey_data(self, client, auth_headers):
        """测试更新调查数据"""
        # 先提交一条数据
        submit_response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert submit_response.status_code == 200
        survey_id = submit_response.json()["survey_id"]
        
        # 更新数据
        update_data = {
            "total_employees": 1300,
            "employed_count": 1250,
            "unemployed_count": 50
        }
        
        update_response = client.put(
            f"{API_PREFIX}/enterprise/survey/{survey_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["status"] == "success"
        assert data["survey"]["total_employees"] == 1300
    
    def test_delete_survey_data(self, client, auth_headers):
        """测试删除调查数据"""
        # 先提交一条数据
        submit_response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert submit_response.status_code == 200
        survey_id = submit_response.json()["survey_id"]
        
        # 删除数据
        delete_response = client.delete(
            f"{API_PREFIX}/enterprise/survey/{survey_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["status"] == "success"
    
    def test_get_survey_statistics(self, client, auth_headers):
        """测试获取调查统计数据"""
        response = client.get(
            f"{API_PREFIX}/enterprise/survey/statistics",
            headers=auth_headers,
            params={"survey_period_id": TEST_SURVEY_DATA["survey_period_id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "survey_period" in data
        assert "statistics" in data
        assert "industry_statistics" in data
    
    def test_submit_without_auth(self, client):
        """测试未授权提交调查数据"""
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            json=TEST_SURVEY_DATA
        )
        
        assert response.status_code == 401
    
    def test_submit_with_admin_user(self, client, admin_headers):
        """测试管理员用户提交调查数据"""
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=admin_headers,
            json=TEST_SURVEY_DATA
        )
        
        # 管理员没有ENT_SUBMIT权限，应该被拦截
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "越权拦截" in data["detail"]
    
    def test_dynamic_validation_unemployment_rate(self, client, auth_headers):
        """测试动态校验-失业率过高警告"""
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["total_employees"] = 100
        invalid_data["employed_count"] = 40
        invalid_data["unemployed_count"] = 60  # 60%失业率，过高
        
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "validation" in data
        validation = data["validation"]
        
        # 失业率过高应该有警告
        assert len(validation["warnings"]) > 0
        assert any("失业率" in warning for warning in validation["warnings"])
    
    def test_dynamic_validation_enterprise_scale(self, client, auth_headers):
        """测试动态校验-企业规模不匹配警告"""
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["total_employees"] = 200  # 200人应该是小型企业
        invalid_data["business_scale"] = "微型"  # 但填的是微型
        
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "validation" in data
        validation = data["validation"]
        
        # 企业规模不匹配应该有警告
        assert len(validation["warnings"]) > 0
        assert any("企业规模" in warning for warning in validation["warnings"])
    
    def test_audit_logging_in_submit(self, client, auth_headers):
        """测试提交操作的审计留痕"""
        response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=auth_headers,
            json=TEST_SURVEY_DATA
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查审计日志
        assert "audit_log" in data
        audit_log = data["audit_log"]
        
        assert audit_log["operation"] == "SURVEY_SUBMIT"
        assert "user" in audit_log
        assert "time" in audit_log