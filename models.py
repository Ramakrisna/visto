from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, Integer
from tornado_sqlalchemy import SQLAlchemy

DB_USER = 'visto'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_USER}'
DB = SQLAlchemy(url=DB_URL)
engine = create_engine(DB_URL)

if not inspect(engine).has_table('urls'):
    metadata = MetaData(engine)
    Table('urls',
          metadata,
          Column('id', Integer, primary_key=True, nullable=False),
          Column('from_domain', String(255)),
          Column('complete_url', String(255)),
          Column('get_tag', String(255))
          )
    metadata.create_all()


class Urls(DB.Model):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    from_domain = Column(String(255), nullable=False)
    complete_url = Column(String(255), nullable=False)
    get_tag = Column(String(255), nullable=False)
