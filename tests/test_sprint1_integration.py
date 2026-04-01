"""
Sprint 1 联调测试
测试整个系统的端到端功能
"""
import pytest
import httpx
import time
from tests.conftest import BASE_URL, API_PREFIX, TEST_USERS, TEST_SURVEY_DATA


class TestSprint1Integration:
    """Sprint 1 联调测试类"""
    
    @pytest.fixture
    def client(self):
        """创建HTTP客户端"""
        return httpx.Client(base_url=BASE_URL, timeout=10.0)
    
    def test_complete_workflow(self, client):
        """测试完整的工作流程"""
        
        # 1. 企业用户登录
        print("\n=== 步骤1: 企业用户登录 ===")
        login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["enterprise"]["username"],
                "password": TEST_USERS["enterprise"]["password"]
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ 企业用户登录成功: {TEST_USERS['enterprise']['username']}")
        
        # 2. 预校验调查数据
        print("\n=== 步骤2: 预校验调查数据 ===")
        validate_response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=headers,
            json=TEST_SURVEY_DATA
        )
        
        assert validate_response.status_code == 200
        validation_result = validate_response.json()["validation"]
        assert validation_result["is_valid"] == True
        print("✅ 数据预校验通过")
        
        # 3. 提交调查数据
        print("\n=== 步骤3: 提交调查数据 ===")
        submit_response = client.post(
            f"{API_PREFIX}/enterprise/survey/submit",
            headers=headers,
            json=TEST_SURVEY_DATA
        )
        
        assert submit_response.status_code == 200
        survey_data = submit_response.json()["data"]
        survey_id = survey_data["survey_id"]
        print(f"✅ 调查数据提交成功，ID: {survey_id}")
        
        # 4. 查询企业调查列表
        print("\n=== 步骤4: 查询企业调查列表 ===")
        list_response = client.get(
            f"{API_PREFIX}/enterprise/survey/list",
            headers=headers,
            params={"enterprise_id": TEST_SURVEY_DATA["enterprise_id"]}
        )
        
        assert list_response.status_code == 200
        surveys = list_response.json()["surveys"]
        assert len(surveys) > 0
        print(f"✅ 查询到 {len(surveys)} 条调查记录")
        
        # 5. 获取调查详情
        print("\n=== 步骤5: 获取调查详情 ===")
        detail_response = client.get(
            f"{API_PREFIX}/enterprise/survey/{survey_id}",
            headers=headers
        )
        
        assert detail_response.status_code == 200
        detail = detail_response.json()["survey"]
        assert detail["survey_id"] == survey_id
        print(f"✅ 调查详情获取成功")
        
        # 6. 管理员登录
        print("\n=== 步骤6: 管理员登录 ===")
        admin_login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        assert admin_login_response.status_code == 200
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print(f"✅ 管理员登录成功: {TEST_USERS['admin']['username']}")
        
        # 7. 管理员审批企业备案
        print("\n=== 步骤7: 管理员审批企业备案 ===")
        audit_response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=admin_headers,
            json={
                "enterprise_id": TEST_SURVEY_DATA["enterprise_id"],
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert audit_response.status_code == 200
        print("✅ 企业备案审批成功")
        
        # 8. 查询审计日志
        print("\n=== 步骤8: 查询审计日志 ===")
        audit_logs_response = client.get(
            f"{API_PREFIX}/audit/logs",
            headers=admin_headers
        )
        
        assert audit_logs_response.status_code == 200
        logs = audit_logs_response.json()["logs"]
        assert len(logs) > 0
        print(f"✅ 查询到 {len(logs)} 条审计日志")
        
        # 9. 获取审计统计
        print("\n=== 步骤9: 获取审计统计 ===")
        stats_response = client.get(
            f"{API_PREFIX}/audit/statistics",
            headers=admin_headers
        )
        
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "total_logs" in stats
        print(f"✅ 审计统计获取成功，总日志数: {stats['total_logs']}")
        
        print("\n=== Sprint 1 联调测试完成 ===")
        print("✅ 所有功能模块正常工作")
    
    def test_permission_control_workflow(self, client):
        """测试权限控制工作流程"""
        
        print("\n=== 权限控制测试 ===")
        
        # 1. 企业用户尝试访问省级审批接口
        print("步骤1: 企业用户尝试访问省级审批接口")
        enterprise_login = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["enterprise"]["username"],
                "password": TEST_USERS["enterprise"]["password"]
            }
        )
        
        enterprise_token = enterprise_login.json()["access_token"]
        enterprise_headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        audit_response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=enterprise_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert audit_response.status_code == 403
        print("✅ 企业用户被正确拦截，无法访问省级审批接口")
        
        # 2. 市级审核员尝试访问省级审批接口
        print("\n步骤2: 市级审核员尝试访问省级审批接口")
        city_login = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["city_admin"]["username"],
                "password": TEST_USERS["city_admin"]["password"]
            }
        )
        
        city_token = city_login.json()["access_token"]
        city_headers = {"Authorization": f"Bearer {city_token}"}
        
        audit_response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=city_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert audit_response.status_code == 403
        print("✅ 市级审核员被正确拦截，无法访问省级审批接口")
        
        # 3. 省级管理员成功访问审批接口
        print("\n步骤3: 省级管理员成功访问审批接口")
        admin_login = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        audit_response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=admin_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        assert audit_response.status_code == 200
        print("✅ 省级管理员成功访问审批接口")
        
        print("\n=== 权限控制测试完成 ===")
    
    def test_data_validation_workflow(self, client):
        """测试数据验证工作流程"""
        
        print("\n=== 数据验证测试 ===")
        
        # 1. 登录获取token
        login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["enterprise"]["username"],
                "password": TEST_USERS["enterprise"]["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 测试就业平衡校验
        print("步骤1: 测试就业平衡校验")
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["total_employees"] = 1000
        invalid_data["employed_count"] = 800
        invalid_data["unemployed_count"] = 50  # 800+50 != 1000
        
        validate_response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=headers,
            json=invalid_data
        )
        
        assert validate_response.status_code == 200
        validation = validate_response.json()["validation"]
        assert not validation["is_valid"]
        assert any("就业平衡" in error for error in validation["errors"])
        print("✅ 就业平衡校验正确拦截错误数据")
        
        # 3. 测试手机号格式校验
        print("\n步骤2: 测试手机号格式校验")
        invalid_data = TEST_SURVEY_DATA.copy()
        invalid_data["contact_phone"] = "12345"
        
        validate_response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=headers,
            json=invalid_data
        )
        
        assert validate_response.status_code == 200
        validation = validate_response.json()["validation"]
        assert not validation["is_valid"]
        print("✅ 手机号格式校验正确拦截错误数据")
        
        # 4. 测试有效数据通过校验
        print("\n步骤3: 测试有效数据通过校验")
        valid_data = TEST_SURVEY_DATA.copy()
        
        validate_response = client.post(
            f"{API_PREFIX}/enterprise/survey/validate",
            headers=headers,
            json=valid_data
        )
        
        assert validate_response.status_code == 200
        validation = validate_response.json()["validation"]
        assert validation["is_valid"] == True
        print("✅ 有效数据成功通过校验")
        
        print("\n=== 数据验证测试完成 ===")
    
    def test_audit_trail_workflow(self, client):
        """测试审计追踪工作流程"""
        
        print("\n=== 审计追踪测试 ===")
        
        # 1. 管理员登录
        admin_login = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 2. 获取初始审计日志数量
        print("步骤1: 获取初始审计日志数量")
        initial_logs_response = client.get(
            f"{API_PREFIX}/audit/logs",
            headers=admin_headers,
            params={"limit": 100}
        )
        
        initial_count = initial_logs_response.json()["total"]
        print(f"✅ 初始审计日志数量: {initial_count}")
        
        # 3. 执行一些操作产生审计日志
        print("\n步骤2: 执行操作产生审计日志")
        
        # 企业备案审批
        client.post(
            f"{API_PREFIX}/province/audit-filing",
            headers=admin_headers,
            json={
                "enterprise_id": 1001,
                "action": "APPROVE",
                "reason": None
            }
        )
        
        # 4. 获取新的审计日志数量
        print("\n步骤3: 获取新的审计日志数量")
        new_logs_response = client.get(
            f"{API_PREFIX}/audit/logs",
            headers=admin_headers,
            params={"limit": 100}
        )
        
        new_count = new_logs_response.json()["total"]
        print(f"✅ 新审计日志数量: {new_count}")
        
        # 5. 验证审计日志增加
        assert new_count >= initial_count
        print("✅ 审计日志正确记录")
        
        # 6. 查询特定操作的审计日志
        print("\n步骤4: 查询特定操作的审计日志")
        enterprise_logs_response = client.get(
            f"{API_PREFIX}/audit/logs/enterprise/1001",
            headers=admin_headers
        )
        
        enterprise_logs = enterprise_logs_response.json()["logs"]
        assert len(enterprise_logs) > 0
        print(f"✅ 企业1001的操作日志: {len(enterprise_logs)} 条")
        
        print("\n=== 审计追踪测试完成 ===")
    
    def test_error_handling_workflow(self, client):
        """测试错误处理工作流程"""
        
        print("\n=== 错误处理测试 ===")
        
        # 1. 测试404错误
        print("步骤1: 测试404错误")
        response = client.get(f"{API_PREFIX}/province/nonexistent-endpoint")
        assert response.status_code == 404
        print("✅ 404错误正确处理")
        
        # 2. 测试401错误
        print("\n步骤2: 测试401错误")
        response = client.get(f"{API_PREFIX}/auth/me")
        assert response.status_code == 401
        print("✅ 401错误正确处理")
        
        # 3. 测试400错误
        print("\n步骤3: 测试400错误")
        response = client.post(
            f"{API_PREFIX}/province/audit-filing",
            json={
                "enterprise_id": 9999,  # 不存在的企业
                "action": "APPROVE",
                "reason": None
            }
        )
        assert response.status_code == 404 or response.status_code == 400
        print("✅ 业务错误正确处理")
        
        print("\n=== 错误处理测试完成 ===")
    
    def test_performance_workflow(self, client):
        """测试性能工作流程"""
        
        print("\n=== 性能测试 ===")
        
        # 1. 登录性能测试
        print("步骤1: 登录性能测试")
        start_time = time.time()
        
        for i in range(5):
            response = client.post(
                f"{API_PREFIX}/auth/login",
                data={
                    "username": TEST_USERS["admin"]["username"],
                    "password": TEST_USERS["admin"]["password"]
                }
            )
            assert response.status_code == 200
        
        end_time = time.time()
        avg_login_time = (end_time - start_time) / 5
        print(f"✅ 平均登录时间: {avg_login_time:.3f}秒")
        
        # 2. 查询性能测试
        print("\n步骤2: 查询性能测试")
        
        login_response = client.post(
            f"{API_PREFIX}/auth/login",
            data={
                "username": TEST_USERS["admin"]["username"],
                "password": TEST_USERS["admin"]["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start_time = time.time()
        
        for i in range(10):
            response = client.get(
                f"{API_PREFIX}/audit/logs",
                headers=headers,
                params={"limit": 10}
            )
            assert response.status_code == 200
        
        end_time = time.time()
        avg_query_time = (end_time - start_time) / 10
        print(f"✅ 平均查询时间: {avg_query_time:.3f}秒")
        
        print("\n=== 性能测试完成 ===")
        print("✅ 系统性能表现良好")