# app/db/init_db.py - 完整修复版本，包含所有必要字段
import os
import sqlite3
from pathlib import Path
from app.db.database import engine, Base

def clean_database():
    """清理现有数据库"""
    print("🧹 清理现有数据库...")
    
    # 删除SQLite数据库文件
    db_files = ["interview_app.db", "interview_app.db-journal", "interview_app.db-wal", "interview_app.db-shm"]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✅ 删除文件: {db_file}")
            except Exception as e:
                print(f"⚠️ 删除 {db_file} 失败: {e}")

def create_tables():
    """创建所有数据库表"""
    print("🚀 开始创建数据库表...")
    
    # 确保导入所有模型
    try:
        from app.models import user, profile
        print("✅ 导入用户相关模型")
    except ImportError as e:
        print(f"❌ 导入用户模型失败: {e}")
        return False
    
    try:
        from app.models import resume
        print("✅ 导入简历模型")
    except ImportError as e:
        print(f"⚠️ 简历模型导入失败: {e}")
    
    try:
        from app.models import question
        print("✅ 导入题目模型")
    except ImportError as e:
        print(f"⚠️ 题目模型导入失败: {e}")
    
    try:
        from app.models import interview
        print("✅ 导入面试相关模型")
    except ImportError as e:
        print(f"❌ 面试模型导入失败: {e}")
        return False
    
    # 创建所有表
    try:
        # 🔥 强制删除现有表定义并重新创建
        Base.metadata.drop_all(bind=engine)
        print("✅ 清理现有表定义")
        
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建完成！")
        
        print("\n📊 已创建的表列表：")
        print("👤 用户系统:")
        print("  - users (用户基本信息)")
        print("  - user_profiles (用户详细资料)")
        
        print("📄 简历系统:")
        print("  - resumes (简历文件)")
        
        print("❓ 题目系统:")
        print("  - questions (面试题库)")
        print("  - question_categories (题目分类)")
        print("  - user_question_progress (用户学习进度)")
        
        print("🎯 面试系统:")
        print("  - interviews (面试记录主表)")
        print("  - interview_questions (面试题目关联)")
        print("  - interview_answers (用户回答记录)")
        print("  - interview_statistics (用户面试统计)")
        print("  - interview_trend_data (趋势分析数据)")
        
        print(f"\n📈 评分维度:")
        print("  1. 专业知识 (professional) - 硬性专业知识和开放性创新能力")
        print("  2. 技能匹配 (skill_match) - 工具/技术是否匹配岗位")
        print("  3. 语言表达 (language_expression) - 语速、音量、情感")
        print("  4. 逻辑思维 (logical_thinking) - 过渡、语言逻辑")
        print("  5. 综合素养 (comprehensive_quality) - 表情+动作(仪态+抗压能力)")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_tables():
    """检查数据库表是否正确创建"""
    print("🔍 检查数据库表状态...")
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'user_profiles', 'resumes', 'questions',
            'question_categories', 'user_question_progress',
            'interviews', 'interview_questions', 'interview_answers',
            'interview_statistics', 'interview_trend_data'
        ]
        
        print(f"📋 现有表 ({len(existing_tables)}个): {existing_tables}")
        
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            print(f"❌ 缺失表: {missing_tables}")
            return False
        else:
            print("✅ 所有必要的表都存在")
            
            # 检查interviews表结构
            check_interviews_table_structure()
            return True
            
    except Exception as e:
        print(f"❌ 检查表状态失败: {e}")
        return False

def check_interviews_table_structure():
    """检查interviews表的字段结构"""
    print("\n🔍 检查interviews表结构...")
    
    try:
        conn = sqlite3.connect('interview_app.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(interviews)")
        columns = cursor.fetchall()
        
        print("📊 interviews表字段:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 检查关键字段是否存在，包括新增的字段
        column_names = [col[1] for col in columns]
        critical_fields = [
            'id', 'user_id', 'type', 'status', 'position', 'difficulty',
            'overall_score', 'professional_score', 'skill_match_score',
            'language_expression_score', 'logical_thinking_score',
            'comprehensive_quality_score', 'is_paused', 'current_phase',
            # 🔥 新增的必要字段
            'recorded_audio_blob', 'recording_duration', 'transcript_text'
        ]
        
        missing_fields = set(critical_fields) - set(column_names)
        if missing_fields:
            print(f"❌ 缺失关键字段: {missing_fields}")
            print("🔧 需要重新创建表结构")
        else:
            print("✅ 所有关键字段都存在")
        
        # 额外检查：显示所有字段总数
        print(f"📈 interviews表总字段数: {len(column_names)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查interviews表结构失败: {e}")

def verify_field_compatibility():
    """验证字段兼容性"""
    print("\n🔍 验证字段兼容性...")
    
    try:
        # 检查模型定义
        from app.models.interview import Interview
        
        # 获取模型的所有字段
        model_columns = Interview.__table__.columns.keys()
        print(f"📋 模型定义字段 ({len(model_columns)}个):")
        for col in sorted(model_columns):
            print(f"  - {col}")
        
        # 检查数据库实际字段
        conn = sqlite3.connect('interview_app.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(interviews)")
        db_columns = [col[1] for col in cursor.fetchall()]
        print(f"\n📋 数据库实际字段 ({len(db_columns)}个):")
        for col in sorted(db_columns):
            print(f"  - {col}")
        
        # 对比差异
        missing_in_db = set(model_columns) - set(db_columns)
        extra_in_db = set(db_columns) - set(model_columns)
        
        if missing_in_db:
            print(f"\n❌ 数据库中缺失的字段: {missing_in_db}")
        if extra_in_db:
            print(f"\n⚠️ 数据库中多余的字段: {extra_in_db}")
        
        if not missing_in_db and not extra_in_db:
            print("\n✅ 字段完全匹配！")
            
        conn.close()
        return len(missing_in_db) == 0
        
    except Exception as e:
        print(f"❌ 验证字段兼容性失败: {e}")
        return False

def init_sample_data():
    """初始化示例数据"""
    print("📝 初始化示例数据...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.question import Question, QuestionCategory
        
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 检查是否已有数据
        existing_questions = db.query(Question).count()
        if existing_questions > 0:
            print(f"ℹ️ 已有 {existing_questions} 道题目，跳过示例数据初始化")
            db.close()
            return True
        
        print("📂 创建题目分类...")
        categories = [
            QuestionCategory(
                name="行为面试",
                description="了解候选人的工作经历、沟通能力等",
                icon="User",
                sort_order=1
            ),
            QuestionCategory(
                name="技术深度",
                description="考察专业技术能力和深度",
                icon="Code",
                sort_order=2
            ),
            QuestionCategory(
                name="项目经验",
                description="了解项目实战经验",
                icon="Briefcase",
                sort_order=3
            )
        ]
        
        for category in categories:
            existing_cat = db.query(QuestionCategory).filter(
                QuestionCategory.name == category.name
            ).first()
            if not existing_cat:
                db.add(category)
        
        db.commit()
        
        print("📝 创建示例题目...")
        sample_questions = [
            Question(
                title="请做一下自我介绍",
                description="包括教育背景、工作经验、技能特长等",
                category="行为面试",
                difficulty="简单",
                tags='["自我介绍", "开场", "基础"]',
                answer="自我介绍应该包含：1) 个人基本信息 2) 教育背景 3) 工作经验 4) 技能特长 5) 求职意向。要简洁明了，突出重点。",
                key_points='["控制时间在2-3分钟", "突出与岗位相关的经验", "展示个人特色"]',
                related_topics='["沟通表达", "职业规划", "个人品牌"]',
                interviewer_perspective="这是开场题，主要了解候选人的基本情况和表达能力。"
            ),
            Question(
                title="介绍一个你负责的项目",
                description="详细说明项目背景、你的职责、技术栈、遇到的挑战和解决方案",
                category="项目经验",
                difficulty="中等",
                tags='["项目经验", "技术栈", "问题解决"]',
                answer="项目介绍要遵循STAR法则：Situation(情况)、Task(任务)、Action(行动)、Result(结果)。重点说明自己的贡献和技术细节。",
                key_points='["项目背景和规模", "个人职责和贡献", "技术选型理由", "遇到的挑战", "解决方案", "项目成果"]',
                related_topics='["项目管理", "团队协作", "技术选型"]',
                interviewer_perspective="考察候选人的项目经验、技术深度和解决问题的能力。"
            ),
            Question(
                title="如何进行前端性能优化？",
                description="从加载优化、渲染优化、代码优化等方面说明",
                category="技术深度",
                difficulty="中等",
                tags='["性能优化", "前端", "技术深度"]',
                answer="前端性能优化包括：1) 加载优化：压缩文件、CDN、懒加载等 2) 渲染优化：减少重排重绘、虚拟滚动等 3) 代码优化：代码分割、Tree Shaking等",
                key_points='["网络层面优化", "渲染层面优化", "代码层面优化", "监控和分析工具"]',
                related_topics='["浏览器原理", "HTTP协议", "构建工具"]',
                interviewer_perspective="考察候选人对前端性能优化的理解深度和实践经验。"
            ),
            Question(
                title="描述一次团队冲突的处理经验",
                description="说明冲突背景、你的角色、处理方式和最终结果",
                category="行为面试", 
                difficulty="中等",
                tags='["团队协作", "冲突处理", "沟通能力"]',
                answer="处理团队冲突需要：1) 了解冲突根源 2) 倾听各方观点 3) 寻找共同目标 4) 制定解决方案 5) 跟进执行效果",
                key_points='["保持中立客观", "促进有效沟通", "寻求双赢方案", "建立长效机制"]',
                related_topics='["领导力", "沟通技巧", "团队建设"]',
                interviewer_perspective="考察候选人的人际关系处理能力和团队协作精神。"
            ),
            Question(
                title="你的职业规划是什么？",
                description="说明短期和长期的职业目标，以及实现路径",
                category="行为面试",
                difficulty="简单", 
                tags='["职业规划", "个人发展", "目标设定"]',
                answer="职业规划应该包括：1) 短期目标（1-2年）2) 中期目标（3-5年）3) 长期愿景 4) 能力提升计划 5) 与公司发展的结合点",
                key_points='["具体可行的目标", "持续学习的计划", "与岗位的匹配度", "展现上进心"]',
                related_topics='["自我认知", "学习能力", "发展潜力"]',
                interviewer_perspective="了解候选人的职业目标和发展规划，判断稳定性和发展潜力。"
            )
        ]
        
        for question in sample_questions:
            db.add(question)
        
        db.commit()
        print(f"✅ 已添加 {len(sample_questions)} 道示例题目")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 初始化示例数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_directories():
    """创建必要的目录"""
    print("📁 创建必要的目录...")
    
    directories = [
        "uploads",
        "uploads/audio", 
        "uploads/video",
        "uploads/resumes",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        except Exception as e:
            print(f"❌ 创建目录 {directory} 失败: {e}")

def fix_bcrypt_issue():
    """修复bcrypt版本问题"""
    print("🔧 检查bcrypt版本...")
    
    try:
        import bcrypt
        # 尝试访问版本信息
        try:
            version = bcrypt.__version__
            print(f"✅ bcrypt版本: {version}")
        except AttributeError:
            print("⚠️ bcrypt版本信息访问异常，但功能正常")
            
        # 测试bcrypt功能
        test_password = "test123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        verified = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
        
        if verified:
            print("✅ bcrypt功能测试通过")
        else:
            print("❌ bcrypt功能测试失败")
            
    except Exception as e:
        print(f"❌ bcrypt检查失败: {e}")
        print("💡 建议运行: pip install --upgrade bcrypt")

def test_interview_creation():
    """测试面试创建功能"""
    print("\n🧪 测试面试创建功能...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.interview import Interview
        from app.models.user import User
        import datetime
        
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 创建测试用户（如果不存在）
        test_user = db.query(User).filter(User.username == "test_user").first()
        if not test_user:
            test_user = User(
                username="test_user",
                email="test@example.com",
                hashed_password="test_hash",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("✅ 创建测试用户")
        
        # 创建测试面试记录
        test_interview = Interview(
            user_id=test_user.id,
            type="practice",
            status="in_progress",
            position="frontend",
            company="测试公司",
            difficulty="medium",
            interview_style="gentle",
            interviewer_id=1,
            round_type="first",
            scheduled_duration=30,
            started_at=datetime.datetime.utcnow(),
            settings='{"test": true}',
            is_paused=False,
            pause_count=0,
            current_phase="intro",
            is_recording=False,
            last_activity=datetime.datetime.utcnow(),
            # 🔥 测试新增字段
            recorded_audio_blob=None,
            recording_duration=None,
            transcript_text=None,
            is_emergency_exit=False
        )
        
        db.add(test_interview)
        db.commit()
        
        print("✅ 测试面试记录创建成功")
        print(f"📝 测试面试ID: {test_interview.id}")
        
        # 清理测试数据
        db.delete(test_interview)
        db.delete(test_user)
        db.commit()
        db.close()
        
        print("✅ 测试数据清理完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试面试创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数 - 一键修复所有数据库问题"""
    print("🎯 面试系统数据库一键修复（包含所有必要字段）")
    print("=" * 70)
    
    # 步骤1: 修复bcrypt问题
    fix_bcrypt_issue()
    print()
    
    # 步骤2: 创建必要目录
    create_directories()
    print()
    
    # 步骤3: 清理现有数据库
    clean_database()
    print()
    
    # 步骤4: 创建数据库表
    if not create_tables():
        print("❌ 数据库表创建失败，退出")
        return False
    print()
    
    # 步骤5: 检查表结构
    if not check_tables():
        print("❌ 数据库表验证失败")
        return False
    print()
    
    # 步骤6: 验证字段兼容性
    if not verify_field_compatibility():
        print("❌ 字段兼容性验证失败")
        return False
    print()
    
    # 步骤7: 测试面试创建
    if not test_interview_creation():
        print("❌ 面试创建测试失败")
        return False
    print()
    
    # 步骤8: 初始化示例数据
    if not init_sample_data():
        print("❌ 示例数据初始化失败")
        return False
    print()
    
    print("🎉 数据库修复完成！")
    print("✅ 所有字段已正确创建，包括:")
    print("   - recorded_audio_blob (录音数据)")
    print("   - recording_duration (录音时长)")
    print("   - transcript_text (语音转文字)")
    print()
    print("💡 现在可以启动服务: uvicorn app.main:app --reload")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 修复过程中出现错误，请检查上述错误信息")
        exit(1)
    else:
        print("\n✅ 所有修复操作成功完成！")
        print("🚀 数据库表结构已与代码模型完全同步")