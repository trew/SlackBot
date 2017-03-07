import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, and_

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(String(64), primary_key=True)
    name = Column(String(128))

    @classmethod
    def get_or_create(cls, session, user_id, user_name):
        user = cls.get(session, user_id)
        if user is None:
            user = User(id=user_id, name=user_name)
            session.add(user)

        return user

    @classmethod
    def get(cls, session, user_id):
        return session.query(User).filter(User.id == user_id).first()

    def __repr__(self):
        return "<User(id='%s', name='%s')>" % (self.id, self.name)


class Cofi(Base):
    __tablename__ = 'cofi'

    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, default=datetime.datetime.now)

    user_id = Column(String(64), ForeignKey('users.id'))

    @classmethod
    def count(cls, session, user):
        return session.query(cls).filter(cls.user_id == user.id).count()

    @classmethod
    def add(cls, session, user):
        cofi = Cofi(user_id=user.id)
        session.add(cofi)

    @classmethod
    def get_today(cls, session, user):
        today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + datetime.timedelta(days=1)
        return session.query(cls).filter(and_(cls.user_id == user.id,
                                              cls.datetime >= today,
                                              cls.datetime < tomorrow)).count()

    @classmethod
    def get_total(cls, session, user):
        return session.query(cls).filter(cls.user_id == user.id).count()

    def __repr__(self):
        return "<Cofi(id='%s', user='%s', datetime='%s')" % (
            self.id, self.user_id, self.datetime)


class Database(object):
    def __init__(self, config):
        db_type = config['type']
        if db_type == 'sqlite':
            if 'file' not in config:
                raise RuntimeError('Missing config parameter: file')
            file = config['file']
            self.engine = create_engine('sqlite:///%s' % file)
        elif db_type == 'postgresql' or db_type == 'postgres':
            user = config['user']
            password = config['password']
            host = config['host']
            port = config['port']
            name = config['name']
            self.engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (user, password, host, port, name))
        elif db_type == 'sqlserver' or db_type == 'mssql':
            user = config.get('user')
            password = config.get('password')
            host = config['host']
            port = config['port']
            name = config['name']
            if user is None:
                self.engine = create_engine('mssql+pyodbc://%s:%s/%s?driver=SQL+Server+Native+Client+11.0' % (host, port, name))
            else:
                self.engine = create_engine('mssql+pyodbc://%s:%s@%s:%s/%s' % (user, password, host, port, name))
        else:
            raise RuntimeError('Unsupported database type: %s' % db_type)

        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
