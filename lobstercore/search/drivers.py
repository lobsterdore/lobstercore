import json, datetime, ConfigParser, os
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
       self.__connection__ = Elasticsearch(self.config['endpoint'], request_timeout=15)
    return self.__connection__

  def drop_index(self):
    es = self.connect()
    es.indices.delete(index = self.config['index'])
    pass

  def create_index(self):
    es = self.connect()
    es.indices.create(index = self.config['index'])
    pass

  def reindex(self, db_session):
    es = self.connect()
    contents = db_session.query(Content).order_by(Content.id)
    for content in contents:
      es.index(
        index = self.config['index'],
        doc_type = content.__name__,
        body = content.to_dict(),
        id = content.id
      )

  def update(self, mapper, connection, target):
    es = self.connect()
    es.index(
      index = self.config['index'],
      doc_type = target.__name__,
      body = target.to_dict(),
      id = target.id
    )

  def delete(self, mapper, connection, target):
    es = self.connect()
    es.delete(
      index = self.config['index'],
      doc_type = target.__name__,
      id = target.id
    )

  def search(self, doc_type, query):
    es = self.connect()
    return es.search(
      index = self.config['index'],
      doc_type = doc_type,
      q = query
    )

def register():
  event.listen(Content, 'after_insert', dispatch_update)
  event.listen(Content, 'after_update', dispatch_update)
  event.listen(Content, 'after_delete', dispatch_delete)

def get_driver():
  driver = False
  config = ConfigParser.ConfigParser()
  config.read('/etc/lobstercms.conf')
  driver_config = dict(config.items('search'))

  if config.get('search', 'enabled', False) is False:
    return driver

  if config.get('search', 'driver') == 'solr':
    driver = SolrDriver(driver_config);

  if config.get('search', 'driver') == 'elasticsearch':
    driver = ElasticsearchDriver(driver_config);

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
