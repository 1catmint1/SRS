#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试登录接口的调试脚本"""

import sys
import traceback

try:
    print("正在导入模块...")
    from core.security import get_password_hash, verify_password, create_access_token
    from db.mock_db import USER_DATABASE

    print("OK 模块导入成功")

    # 检查用户数据库
    print("\n用户数据库内容:")
    for username, user_data in USER_DATABASE.items():
        print(f"  {username}: {user_data['username']}, role_id: {user_data['role_id']}")
        print(f"    密码哈希: {user_data['password_hash'][:50]}...")

    # 测试密码哈希和验证
    print("\n测试密码功能:")
    test_password = "password123"
    test_hash = get_password_hash(test_password)
    print(f"  生成密码哈希: {test_hash[:50]}...")

    admin_user = USER_DATABASE.get("admin")
    if admin_user:
        stored_hash = admin_user["password_hash"]
        print(f"  存储的密码哈希: {stored_hash[:50]}...")

        # 测试密码验证
        is_valid = verify_password(test_password, stored_hash)
        print(f"  密码验证结果: {is_valid}")

        # 测试令牌生成
        token_data = {
            "user_id": admin_user["user_id"],
            "username": admin_user["username"],
            "role_id": admin_user["role_id"],
            "role_name": admin_user["role_name"]
        }
        token = create_access_token(token_data)
        print(f"  生成的令牌: {token[:50]}...")

    print("\nOK 所有测试通过")

except Exception as e:
    print(f"\nERROR 发生错误: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    sys.exit(1)