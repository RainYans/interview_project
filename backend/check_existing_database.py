# check_existing_database.py - 检查现有数据库结构
import sqlite3
import os
from pathlib import Path

def check_database_structure():
    """检查现有数据库的表结构"""
    print("🔍 检查现有数据库结构...")
    print("=" * 50)
    
    db_file = "app.db"
    
    # 1. 检查文件是否存在
    if not os.path.exists(db_file):
        print("❌ 数据库文件不存在")
        return False
    
    # 2. 显示文件信息
    file_size = os.path.getsize(db_file)
    print(f"📁 数据库文件: {db_file}")
    print(f"📊 文件大小: {file_size} bytes")
    print(f"📂 绝对路径: {Path(db_file).absolute()}")
    
    try:
        # 3. 连接数据库
        print("\n🔗 连接数据库...")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 4. 检查所有表
        print("\n📋 检查所有表...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ 数据库中没有任何表")
            return False
        
        print("📋 现有表:")
        table_names = []
        for table in tables:
            table_name = table[0]
            table_names.append(table_name)
            print(f"  - {table_name}")
        
        # 5. 检查 interviews 表是否存在
        if 'interviews' not in table_names:
            print("\n❌ interviews 表不存在")
            return False
        
        # 6. 检查 interviews 表结构
        print(f"\n🔍 检查 interviews 表结构...")
        cursor.execute("PRAGMA table_info(interviews)")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ interviews 表没有列信息")
            return False
        
        print("📋 interviews 表列:")
        column_names = []
        for col in columns:
            column_names.append(col[1])
            print(f"  {col[0]:2d}. {col[1]:25s} ({col[2]})")
        
        # 7. 检查关键列是否存在
        required_columns = [
            'id', 'user_id', 'type', 'status', 'position', 
            'company', 'difficulty', 'interview_style', 'interviewer_id',
            'round_type', 'scheduled_duration', 'started_at'
        ]
        
        print(f"\n✅ 检查必需列:")
        missing_columns = []
        for col in required_columns:
            if col in column_names:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (缺失)")
                missing_columns.append(col)
        
        # 8. 总结
        if missing_columns:
            print(f"\n❌ 缺失列: {missing_columns}")
            print("🔧 需要修复数据库结构")
            return False
        else:
            print(f"\n✅ 所有必需列都存在")
            print("🎉 数据库结构正常")
            return True
        
    except Exception as e:
        print(f"❌ 检查数据库时发生错误: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def fix_missing_columns():
    """修复缺失的列"""
    print("\n🔧 修复缺失的列...")
    
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        
        # 检查并添加缺失的列
        cursor.execute("PRAGMA table_info(interviews)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        columns_to_add = [
            ("company", "VARCHAR(100)"),
            ("interview_style", "VARCHAR(30)"),
            ("interviewer_id", "INTEGER"),
            ("round_type", "VARCHAR(20)"),
            ("scheduled_duration", "INTEGER"),
            ("actual_duration", "INTEGER"),
            ("settings", "JSON"),
            ("ai_feedback", "TEXT"),
            ("key_feedback", "TEXT"),
            ("improvement_suggestions", "TEXT"),
            ("total_questions", "INTEGER DEFAULT 0"),
            ("answered_questions", "INTEGER DEFAULT 0"),
            ("hints_used", "INTEGER DEFAULT 0"),
        ]
        
        added_columns = []
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE interviews ADD COLUMN {column_name} {column_type}"
                    print(f"  添加列: {column_name}")
                    cursor.execute(sql)
                    added_columns.append(column_name)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"  ❌ 添加 {column_name} 失败: {e}")
        
        if added_columns:
            conn.commit()
            print(f"✅ 成功添加 {len(added_columns)} 个列: {added_columns}")
        else:
            print("ℹ️ 没有需要添加的列")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复列时发生错误: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🎯 数据库结构检查工具")
    print()
    
    # 检查数据库结构
    is_structure_ok = check_database_structure()
    
    if not is_structure_ok:
        print("\n" + "=" * 50)
        choice = input("🔧 是否尝试修复数据库结构? (y/N): ").strip().lower()
        
        if choice == 'y':
            if fix_missing_columns():
                print("\n🔍 重新检查数据库结构...")
                check_database_structure()
            else:
                print("\n❌ 修复失败，建议重新创建数据库")
                print("💡 运行: python force_recreate_database.py")
        else:
            print("\n💡 建议:")
            print("1. 运行: python force_recreate_database.py")
            print("2. 或手动删除 app.db 后重新初始化")
    else:
        print("\n🎉 数据库结构正常！可以正常使用面试功能")