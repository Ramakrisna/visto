from sqlalchemy import Column, String, Integer
from tornado_sqlalchemy import declarative_base
from tornado_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()
DB.configure(url='postgresql://rama@localhost:5432/rama')
Base = declarative_base()


class Urls(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    from_domain = Column(String(255), nullable=False)
    full_url = Column(String(255), nullable=False)
    get_tag = Column(String(255), nullable=False)
