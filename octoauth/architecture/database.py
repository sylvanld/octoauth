import uuid
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from octoauth.exceptions import ObjectNotFoundException
from octoauth.settings import SETTINGS

engine_options = {}
if ":memory:" in SETTINGS.DATABASE_URI:
    engine_options["connect_args"] = {"check_same_thread": False}
    engine_options["poolclass"] = StaticPool

engine = create_engine(SETTINGS.DATABASE_URI, **engine_options)
Session = scoped_session(session_factory=sessionmaker(bind=engine))


class QueryProperty(object):
    def __get__(self, instance, model) -> Query:
        return Session.query(model)


def generate_uid():
    return uuid.uuid4().hex


class CRUDMixin:
    __tablename__: str

    query: Query = QueryProperty()

    @classmethod
    def find_one(cls, **filters):
        instance = Session.query(cls).filter_by(**filters).first()
        if instance is None:
            query_description = ", ".join("=".join((str(filter_), str(value))) for filter_, value in filters.items())
            raise ObjectNotFoundException(f"No {cls.__tablename__} found with {query_description}")
        return instance

    @classmethod
    def get_by_uid(cls, uid: str):
        return cls.find_one(uid=uid)

    @classmethod
    def create(cls, **data: dict):
        instance = cls(**data)
        Session.add(instance)
        Session.commit()
        return instance

    @classmethod
    def delete_all(cls, *filters):
        Session.query(cls).filter(*filters).delete()
        Session.commit()

    @classmethod
    def delete_by_uid(cls, uid: str):
        instance = cls.get_by_uid(uid)
        Session.delete(instance)
        Session.commit()

    def delete(self):
        Session.delete(self)
        Session.commit()

    def update(self, **updated_properties: dict):
        for attr, value in updated_properties.items():
            if value is not None:
                setattr(self, attr, value)
        Session.commit()


DBModel: Type[CRUDMixin] = declarative_base(bind=engine, cls=CRUDMixin)


def use_database(func):
    """
    Make database session available in the context of decorated function, then close session.
    """

    def wrapper(*args, **kwargs):
        with Session():
            output = func(*args, **kwargs)
        return output

    return func
