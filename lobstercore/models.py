from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Table,
    ForeignKey,
    DateTime,
    event,
)
from sqlalchemy.orm import relationship, backref, ColumnProperty, object_mapper
from sqlalchemy.ext.declarative import declarative_base
from time import mktime
import datetime, json
from lobstercore.utils import DatetimeJsonEncoder

Base = declarative_base()


class BaseEntity:
    __default_deep__ = {}
    __default_exclude__ = []

    def to_dict(self, deep={}, exclude=[]):
        """Generate a JSON-style nested dict/list structure from an selfect."""
        col_prop_names = [
            p.key
            for p in object_mapper(self).iterate_properties
            if isinstance(p, ColumnProperty)
        ]
        data = dict(
            [
                (name, getattr(self, name))
                for name in col_prop_names
                if name not in exclude
            ]
        )

        # objects can provide a default view
        if not deep:
            deep = self.__default_deep__
        if not exclude:
            exclude = self.__default_exclude__

        if deep:
            for rname, rdeep in deep.items():
                dbdata = getattr(self, rname)
                # FIXME: use attribute names (ie coltoprop) instead of column names
                fks = object_mapper(self).get_property(rname).remote_side
                exclude = [c.name for c in fks]
                if dbdata is None:
                    data[rname] = None
                elif isinstance(dbdata, list):
                    data[rname] = [o.to_dict(rdeep, exclude) for o in dbdata]
                else:
                    data[rname] = dbdata.to_dict(rdeep, exclude)
        return data


class Site(Base, BaseEntity):
    __name__ = "site"
    __tablename__ = "site"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True)
    shortcode = Column(String(20), unique=True)

    def __init__(self, title, shortcode):
        self.title = title
        self.shortcode = shortcode

    def __repr__(self):
        return "%r" % (self.title)


class Section(Base, BaseEntity):
    __name__ = "section"
    __tablename__ = "section"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("site.id"))
    title = Column(String(250))
    slug = Column(String(250), unique=True)

    site = relationship(
        "Site", backref=backref("sections", order_by=id, cascade="all,delete")
    )

    def __init__(self, title, slug, site):
        self.title = title
        self.slug = slug
        self.site = site

    def __repr__(self):
        return "%r" % (self.title)


class Content(Base, BaseEntity):
    __name__ = "content"
    __tablename__ = "content"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}
    __default_deep__ = {"section": {}}

    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("section.id"))
    title = Column(String(250))
    slug = Column(String(250), unique=True)
    meta_title = Column(String(250))
    meta_description = Column(String(250))
    body = Column(Text())
    publish_date = Column(DateTime(), nullable=True)
    created_on = Column(DateTime, default=datetime.datetime.now)
    updated_on = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    section = relationship(
        "Section",
        backref=backref("contents", order_by=id, cascade="all,delete"),
    )

    def __init__(
        self,
        title,
        slug,
        meta_title,
        meta_description,
        body,
        publish_date,
        section,
    ):
        self.title = title
        self.slug = slug
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.body = body
        self.publish_date = publish_date
        self.section = section

    def __repr__(self):
        return "%r" % (self.title)


user_site = Table(
    "user_site",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("site_id", Integer, ForeignKey("site.id")),
)


class User(Base, BaseEntity):
    __name__ = "user"
    __tablename__ = "user"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}
    id = Column(Integer, primary_key=True)
    email = Column(String(250), unique=True)
    password = Column(String(250))

    sites = relationship(
        "Site",
        secondary=user_site,
        backref=backref("users", order_by=id, cascade="all,delete"),
    )

    def __init__(self, email, password, sites):
        self.email = email
        self.password = password
        self.sites = sites

    def __repr__(self):
        return "%r" % (self.email)
