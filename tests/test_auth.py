"""
认证接口测试用例
"""
import pytest
import httpx
from tests.conftest import BASE_URL, API_PREFIX, TEST_USERS


class TestAuthAPI:
    """认证接口测试类"""
    
    @pytest.fixture
    def client(self):
        """创建HTTP客户端"""
        return httpx.Client(base_url=BASE_URL, timeout=10.0)
    
    def test_login_success(self, client):
        """测试成功登录"""
        response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user_info" in data
        assert data["user_info"]["username"] == TEST_USERS["admin"]["username"]
    
    def test_login_invalid_username(self, client):
        """测试无效用户名登录"""
        response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": "invalid_user",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_invalid_password(self, client):
        """测试无效密码登录"""
        response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user(self, client):
        """测试获取当前用户信息"""
        # 先登录获取token
        login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 使用token获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{API_PREFIX}/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert data["username"] == TEST_USERS["admin"]["username"]
    
    def test_get_current_user_without_token(self, client):
        """测试未提供token获取用户信息"""
        response = client.get(f"{API_PREFIX}/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """测试使用无效token获取用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get(f"{API_PREFIX}/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_multi_role_login(self, client):
        """测试多角色登录"""
        roles = ["admin", "city_admin", "enterprise"]
        
        for role in roles:
            response = client.post(
                f"{API_PREFIX}/auth/login",
                data={
                    "username": TEST_USERS[role]["username"],
                    "password": TEST_USERS[role]["password"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "user_info" in data
            assert data["user_info"]["role_name"] == TEST_USERS[role]["role"]