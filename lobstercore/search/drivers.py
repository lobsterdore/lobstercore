import datetime
import json
import os

import app

from abc import ABCMeta, abstractmethod, abstractproperty
from time import mktime
from sqlalchemy import event
from elasticsearch import Elasticsearch
from lobstercore.models import Content


class Driver:
    __metaclass__ = ABCMeta
    config = {}

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def drop_index(self):
        pass

    @abstractmethod
    def create_index(self):
        pass

    @abstractmethod
    def reindex(self, db_session):
        pass

    @abstractmethod
    def update(self, mapper, connection, target):
        pass

    @abstractmethod
    def delete(self, mapper, connection, target):
        pass

    @abstractmethod
    def search(self, doc_type, query):
        pass


class ElasticsearchDriver(Driver):
    __connection__ = False

    def connect(self):
        if not self.__connection__:
            self.__connection__ = Elasticsearch(
                self.config["endpoint"], request_timeout=15
            )
        return self.__connection__

    def drop_index(self):
        es = self.connect()
        es.indices.delete(
            index=self.config["index"],
            allow_no_indices=True,
            ignore_unavailable=True,
        )

    def create_index(self):
        es = self.connect()
        es.indices.create(
            index=self.config["index"],
            body={
                "settings": {
                    "index": {"number_of_shards": 1, "number_of_replicas": 0}
                }
            },
        )

    def reindex(self, db_session):
        es = self.connect()
        contents = db_session.query(Content).order_by(Content.id)
        for content in contents:
            es.index(
                index=self.config["index"],
                doc_type=content.__name__,
                body=content.to_dict(),
                id=content.id,
            )

    def update(self, mapper, connection, target):
        es = self.connect()
        es.index(
            index=self.config["index"],
            doc_type=target.__name__,
            body=target.to_dict(),
            id=target.id,
        )

    def delete(self, mapper, connection, target):
        es = self.connect()
        es.delete(
            index=self.config["index"], doc_type=target.__name__, id=target.id
        )

    def search(self, doc_type, query):
        es = self.connect()
        results = es.search(
            index=self.config["index"], doc_type=doc_type.lower(), q=query
        )
        resultset = []
        if results["hits"]["total"] == 0:
            return resultset

        for result in results["hits"]["hits"]:
            resultset.append(result["_source"])

        return resultset


def register():
    event.listen(Content, "after_insert", dispatch_update)
    event.listen(Content, "after_update", dispatch_update)
    event.listen(Content, "after_delete", dispatch_delete)


def get_driver():
    driver = False

    if app.config["search"]["driver"] == "elasticsearch":
        driver = ElasticsearchDriver(dict(app.config["search"]))

    return driver


def dispatch_update(mapper, connection, target):
    driver = get_driver()
    if driver is False:
        return
    driver.update(mapper, connection, target)


def dispatch_delete(mapper, connection, target):
    driver = get_driver()
    if driver is False:
        return
    driver.delete(mapper, connection, target)


def initialise(db_session):
    driver = get_driver()
    if driver is False:
        return
    driver.drop_index()
    driver.create_index()
    driver.reindex(db_session)


def search(doc_type, query):
    driver = get_driver()
    if driver is False:
        return
    return driver.search(doc_type, query)
