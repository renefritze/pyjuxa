import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'

    def __init__(self, name):
        self.name = name

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Config(Base):
    __tablename__ = 'configs'

    def __init__(self, name, project_id):
        self.name = name
        self.project_id = project_id

    id = Column(Integer, primary_key=True)
    name = Column(String)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project")


class Testsuite(Base):
    __tablename__ = 'suites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project")
    errors = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    failures = Column(Integer, default=0)
    skips = Column(Integer, default=0)
    tests = Column(Integer, default=0)
    runtime = Column(Integer)
    __table_args__ = (
        CheckConstraint(errors >= 0, name='check_counts_positive'),
        {})


'''
<testcase name="test_almost_equal[compatible_vector_array_pair0-compatible_vector_array_pair_without_reserve0]"
    classname="src.pymortests.algorithms.basic"
    time="0.006150484085083008"></testcase>
<testcase name="Timing"
    classname="ProfilerTest"
    time="0.451"
    status="run" />'''
class Testcase(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    suite_id = Column(Integer, ForeignKey('suites.id'))
    suite = relationship("Testsuite")
    runtime = Column(Integer)
    classname = Column(String)


def connect(db_path):
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///{}'.format(db_path))
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

