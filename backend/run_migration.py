# run_migration.py - 放在项目根目录
"""
简单的数据库迁移运行脚本
使用方法: python run_migration.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🎯 面试系统数据库迁移")
    print("=" * 50)
    
    try:
        # 导入迁移函数
        print("📦 导入迁移模块...")
        from app.db.migrate_interview_tables import (
            migrate_interview_tables, 
            create_new_tables, 
            insert_default_interviewers
        )
        print("✅ 模块导入成功")
        
        # 执行迁移
        print("\n🚀 步骤1: 迁移现有表...")
        migrate_interview_tables()
        
        print("\n🆕 步骤2: 创建新表...")
        create_new_tables()
        
        print("\n👨‍💼 步骤3: 插入默认数据...")
        insert_default_interviewers()
        
        print("\n🎉 所有迁移步骤完成！")
        print("💡 现在可以重新启动服务并测试面试功能了")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("🔧 请确保:")
        print("  1. 已将 migrate_interview_tables.py 放在 app/db/ 目录下")
        print("  2. app/db/ 目录中有 __init__.py 文件")
        print("  3. 在项目根目录下运行此脚本")
        
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        print("🔧 请检查:")
        print("  1. 数据库连接是否正常")
        print("  2. 数据库文件是否有写入权限")
        print("  3. app/db/database.py 中的数据库配置是否正确")

if __name__ == "__main__":
    main()