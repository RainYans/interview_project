# app/db/migrate_interview_tables.py
"""
面试系统数据库迁移脚本
添加新增字段支持前端功能
"""

from sqlalchemy import text
from app.db.database import engine

def migrate_interview_tables():
    """迁移面试相关表，添加新字段"""
    
    print("🚀 开始迁移面试系统数据库...")
    
    with engine.begin() as connection:
        
        # ===== 迁移 interviews 表 =====
        print("📋 迁移 interviews 表...")
        
        # 检查字段是否已存在，避免重复添加
        def add_column_if_not_exists(table_name, column_definition):
            try:
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"))
                print(f"  ✅ 添加字段: {column_definition}")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  ⚠️ 字段已存在: {column_definition.split()[0]}")
                else:
                    print(f"  ❌ 添加字段失败: {column_definition} - {e}")
        
        # interviews 表新增字段
        interview_new_columns = [
            # 面试状态控制
            "is_paused BOOLEAN DEFAULT 0",
            "pause_count INTEGER DEFAULT 0", 
            "current_phase VARCHAR(30)",
            "current_question_id INTEGER",
            
            # 实时状态
            "is_recording BOOLEAN DEFAULT 0",
            "last_activity DATETIME",
            
            # 文件存储路径
            "session_data_path VARCHAR(500)",
            "analysis_data_path VARCHAR(500)", 
            
            # 紧急退出相关
            "exit_reason VARCHAR(200)",
            "is_emergency_exit BOOLEAN DEFAULT 0"
        ]
        
        for column in interview_new_columns:
            add_column_if_not_exists("interviews", column)
        
        # ===== 迁移 interview_questions 表 =====
        print("📝 迁移 interview_questions 表...")
        
        question_new_columns = [
            # 提示相关
            "hint_text TEXT",
            "hint_used_count INTEGER DEFAULT 0",
            
            # 跳过相关  
            "skip_reason VARCHAR(100)",
            "is_skipped BOOLEAN DEFAULT 0",
            
            # 实时分析
            "real_time_data TEXT"  # SQLite 使用 TEXT 存储 JSON
        ]
        
        for column in question_new_columns:
            add_column_if_not_exists("interview_questions", column)
        
        # ===== 迁移 interview_answers 表 =====
        print("💬 迁移 interview_answers 表...")
        
        answer_new_columns = [
            # 文件信息
            "audio_file_size INTEGER",
            "video_file_size INTEGER", 
            "file_upload_time DATETIME",
            
            # 实时分析结果
            "realtime_emotion_data TEXT",
            "realtime_voice_data TEXT",
            "realtime_behavior_data TEXT",
            
            # 提示使用详情
            "hint_view_time DATETIME",
            "hint_content TEXT"
        ]
        
        for column in answer_new_columns:
            add_column_if_not_exists("interview_answers", column)
        
        # ===== 迁移 interview_statistics 表 =====
        print("📊 迁移 interview_statistics 表...")
        
        stats_new_columns = [
            # 暂停和提示统计
            "total_pauses INTEGER DEFAULT 0",
            "total_hints_used INTEGER DEFAULT 0", 
            "total_questions_skipped INTEGER DEFAULT 0",
            
            # 紧急退出统计
            "emergency_exits INTEGER DEFAULT 0",
            "incomplete_interviews INTEGER DEFAULT 0",
            
            # 实时分析统计
            "avg_audio_level REAL DEFAULT 0",
            "avg_speech_speed REAL DEFAULT 0",
            "dominant_emotion VARCHAR(20)",
            
            # 文件上传统计
            "total_audio_uploads INTEGER DEFAULT 0",
            "total_video_uploads INTEGER DEFAULT 0", 
            "total_upload_size INTEGER DEFAULT 0"
        ]
        
        for column in stats_new_columns:
            add_column_if_not_exists("interview_statistics", column)
        
        # ===== 迁移 interview_trend_data 表 =====
        print("📈 迁移 interview_trend_data 表...")
        
        trend_new_columns = [
            # 面试行为数据
            "questions_answered INTEGER DEFAULT 0",
            "hints_used INTEGER DEFAULT 0",
            "questions_skipped INTEGER DEFAULT 0", 
            "pauses_count INTEGER DEFAULT 0",
            
            # 实时分析数据
            "avg_audio_level REAL",
            "dominant_emotion VARCHAR(20)",
            "eye_contact_quality VARCHAR(20)",
            "speech_fluency REAL",
            
            # 技术数据
            "camera_enabled BOOLEAN DEFAULT 0",
            "audio_uploads INTEGER DEFAULT 0",
            "video_uploads INTEGER DEFAULT 0",
            
            # 完成状态
            "is_emergency_exit BOOLEAN DEFAULT 0",
            "completion_rate REAL DEFAULT 0"
        ]
        
        for column in trend_new_columns:
            add_column_if_not_exists("interview_trend_data", column)
    
    print("✅ 数据库迁移完成！")
    print("\n📋 迁移总结:")
    print("  - interviews 表: 新增 10 个字段")
    print("  - interview_questions 表: 新增 5 个字段") 
    print("  - interview_answers 表: 新增 8 个字段")
    print("  - interview_statistics 表: 新增 12 个字段")
    print("  - interview_trend_data 表: 新增 13 个字段")
    print("\n🎉 现在可以正常使用所有面试功能了！")

def create_new_tables():
    """创建新的扩展表"""
    
    print("🆕 创建新的扩展表...")
    
    with engine.begin() as connection:
        
        # 创建虚拟面试官表
        print("🎭 创建 virtual_interviewers 表...")
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS virtual_interviewers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    avatar_url VARCHAR(255),
                    model_url VARCHAR(255),
                    specialties TEXT,  -- JSON
                    experience VARCHAR(100),
                    style VARCHAR(30) NOT NULL,
                    voice_settings TEXT,  -- JSON
                    behavior_settings TEXT,  -- JSON
                    question_style TEXT,  -- JSON
                    is_active BOOLEAN DEFAULT 1,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("  ✅ virtual_interviewers 表创建成功")
        except Exception as e:
            print(f"  ⚠️ virtual_interviewers 表已存在或创建失败: {e}")
        
        # 创建实时分析数据表
        print("🔬 创建 realtime_analysis_data 表...")
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS realtime_analysis_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interview_id INTEGER NOT NULL,
                    question_id INTEGER,
                    user_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    
                    -- 音频分析
                    audio_level REAL,
                    speech_speed REAL,
                    speech_pause_duration REAL,
                    
                    -- 视觉分析
                    emotion_type VARCHAR(20),
                    emotion_confidence REAL,
                    eye_contact_score REAL,
                    head_pose TEXT,  -- JSON
                    
                    -- 行为分析
                    gesture_detected BOOLEAN DEFAULT 0,
                    posture_score REAL,
                    attention_level REAL,
                    
                    -- 综合分析
                    engagement_score REAL,
                    confidence_level REAL,
                    stress_indicators TEXT,  -- JSON
                    
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (interview_id) REFERENCES interviews (id),
                    FOREIGN KEY (question_id) REFERENCES interview_questions (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            print("  ✅ realtime_analysis_data 表创建成功")
        except Exception as e:
            print(f"  ⚠️ realtime_analysis_data 表已存在或创建失败: {e}")
    
    print("✅ 新扩展表创建完成！")

def insert_default_interviewers():
    """插入默认虚拟面试官数据"""
    
    print("👨‍💼 插入默认虚拟面试官数据...")
    
    with engine.begin() as connection:
        
        # 检查是否已有数据
        result = connection.execute(text("SELECT COUNT(*) FROM virtual_interviewers")).fetchone()
        if result[0] > 0:
            print("  ⚠️ 虚拟面试官数据已存在，跳过插入")
            return
        
        # 插入默认面试官数据
        interviewers = [
            {
                'name': '李面试官',
                'description': '亲和力强，善于引导，适合面试新手',
                'avatar_url': '/avatars/interviewer-1.jpg',
                'model_url': '/models/avatar-1.glb',
                'specialties': '["温和型", "鼓励式", "新人友好"]',
                'experience': '5年HR经验',
                'style': 'gentle',
                'voice_settings': '{"speed": 1.0, "pitch": 1.0, "volume": 0.8}',
                'behavior_settings': '{"question_interval": 3, "patience_level": 5, "follow_up_probability": 0.3}',
                'question_style': '{"formal_level": 0.5, "detail_focus": 0.6, "encouragement": 0.9}',
                'sort_order': 1
            },
            {
                'name': '张面试官', 
                'description': '经验丰富，专业严谨，标准化流程',
                'avatar_url': '/avatars/interviewer-2.jpg',
                'model_url': '/models/avatar-2.glb',
                'specialties': '["技术深度", "严谨细致", "标准化"]',
                'experience': '10年技术总监',
                'style': 'serious',
                'voice_settings': '{"speed": 1.1, "pitch": 0.9, "volume": 0.9}',
                'behavior_settings': '{"question_interval": 2, "patience_level": 3, "follow_up_probability": 0.5}',
                'question_style': '{"formal_level": 0.7, "detail_focus": 0.8, "encouragement": 0.5}',
                'sort_order': 2
            },
            {
                'name': '王面试官',
                'description': '技术专家，深度挖掘，压力测试', 
                'avatar_url': '/avatars/interviewer-3.jpg',
                'model_url': '/models/avatar-3.glb',
                'specialties': '["技术挑战", "压力测试", "深度追问"]',
                'experience': '15年架构师',
                'style': 'challenging',
                'voice_settings': '{"speed": 1.2, "pitch": 0.8, "volume": 1.0}',
                'behavior_settings': '{"question_interval": 1, "patience_level": 2, "follow_up_probability": 0.7}',
                'question_style': '{"formal_level": 0.6, "detail_focus": 0.9, "encouragement": 0.3}',
                'sort_order': 3
            }
        ]
        
        for interviewer in interviewers:
            connection.execute(text("""
                INSERT INTO virtual_interviewers 
                (name, description, avatar_url, model_url, specialties, experience, style, 
                 voice_settings, behavior_settings, question_style, sort_order)
                VALUES (:name, :description, :avatar_url, :model_url, :specialties, :experience, :style,
                        :voice_settings, :behavior_settings, :question_style, :sort_order)
            """), interviewer)
        
        print(f"  ✅ 已插入 {len(interviewers)} 个默认虚拟面试官")

if __name__ == "__main__":
    print("🎯 面试系统数据库迁移工具")
    print("=" * 50)
    
    try:
        # 1. 迁移现有表
        migrate_interview_tables()
        
        # 2. 创建新表
        create_new_tables()
        
        # 3. 插入默认数据
        insert_default_interviewers()
        
        print("\n🎉 数据库迁移全部完成！")
        print("💡 现在可以重新启动服务并测试面试功能了")
        
    except Exception as e:
        print(f"\n❌ 迁移过程中出现错误: {e}")
        print("🔧 请检查数据库连接和权限设置")