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
  def update(self, mapper, connection, target):
    pass

  @abstractmethod
  def delete(self, mapper, connection, target):
    pass

class ElasticsearchDriver(Driver):

  def connect(self):
    return Elasticsearch(self.config['endpoint'], request_timeout=15)

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
