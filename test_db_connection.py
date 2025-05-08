import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载 .env 文件
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 从 .env 读取数据库 URL
db_url = os.getenv("DATABASE_URL")
print(f"Using DATABASE_URL: {db_url}")

# 创建数据库引擎
engine = create_engine(db_url)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful! Result:", result.scalar())
except Exception as e:
    print("Database connection failed:", e)
