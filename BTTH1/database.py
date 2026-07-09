from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
DATABASE__URL="mysql+pymysql://root:giahan19@localhost:3306/fastapi_db"

engine=create_engine(DATABASE__URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=SessionLocal();
    try:
        yield db
    finally:
        db.close()
