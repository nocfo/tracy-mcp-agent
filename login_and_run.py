from jwt_utils import generate_token
import asyncio
import os
from main import main  # main入口 async 方法

# 模拟用户登录
def login(username: str, company_id: str) -> str:
    print(f"🔐 Logging in user: {username} for company: {company_id}")

    # 使用更长的token过期时间
    token = generate_token(user_id=username, company_id=company_id, expires_in=43200)
    print("[DEBUG] Authentication token generated successfully")

    return token

# 运行整个流程
if __name__ == "__main__":
    print("=== Virtual CFO System Login ===")
    username = input("Username: ").strip()
    company_id = input("Company ID: ").strip()

    try:
        token = login(username, company_id)
        print(f"[DEBUG] Login successful. Token will be valid for 12 hours.")

        # 写入到临时文件
        with open("user_token.txt", "w") as f:
            f.write(token)
        print(f"[DEBUG] Token saved to user_token.txt")

        print("\n=== Starting MCP Agent System ===")
        asyncio.run(main())  # 启动代理流程
    except Exception as e:
        print(f"[ERROR] Login process failed: {str(e)}")