# reset_database.py - 重置数据库脚本
import os
from app.db.init_db import reset_database, create_tables

def main():
    print("🔄 开始重置数据库...")
    print("⚠️  这将删除所有现有数据！")
    
    # 如果使用 SQLite，直接删除数据库文件
    db_file = "app.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ 已删除数据库文件: {db_file}")
        except Exception as e:
            print(f"❌ 删除数据库文件失败: {e}")
            return
    
    # 重新创建表
    try:
        create_tables()
        print("✅ 数据库重置成功！")
        
        # 创建测试用户
        create_test_user()
        
    except Exception as e:
        print(f"❌ 重置数据库失败: {e}")
        import traceback
        traceback.print_exc()

def create_test_user():
    """创建测试用户"""
    try:
        from app.db.database import SessionLocal
        from app.models.user import User
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        # 检查测试用户是否已存在
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("ℹ️  测试用户已存在")
            db.close()
            return
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("123456"),
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ 创建测试用户成功:")
        print(f"   用户名: testuser")
        print(f"   密码: 123456")
        print(f"   用户ID: {test_user.id}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 创建测试用户失败: {e}")

if __name__ == "__main__":
    main()