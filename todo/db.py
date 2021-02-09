from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:////mnt/data/todo.db", connect_args={"timeout": 15})

Base = declarative_base()


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
