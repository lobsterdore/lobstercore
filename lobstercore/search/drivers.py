import pysolr, json, datetime, ConfigParser, os
from abc import ABCMeta, abstractmethod, abstractproperty
from time import mktime
from sqlalchemy import event
from lobstercore.models import Content

class Driver:
	__metaclass__ = ABCMeta
	config = {}

	def __init__(self, config):
		self.config = config

	@abstractmethod
	def update(self, mapper, connection, target):
		pass

	@abstractmethod
	def delete(self, mapper, connection, target):
		pass

class Solr(Driver):

	def update(self, mapper, connection, target):
		solr = pysolr.Solr(self.config['endpoint'], timeout=10)
		search_document = target.get_search_document()
		search_data = [{
			"id": search_document.id,
			"type":search_document.type,
			"title": search_document.title,
			"text": search_document.text,
			"category": search_document.category,
			"data":search_document.data
		}]
		solr.add(search_data)

	def delete(self, mapper, connection, target):
		solr = pysolr.Solr(config.get('search', 'endpoint'), timeout=10)
		search_document = target.get_search_document()
		solr.delete(id=search_document.id)

def register():
	event.listen(Content, 'after_insert', dispatch_update)
	event.listen(Content, 'after_update', dispatch_update)
	event.listen(Content, 'after_delete', dispatch_delete)

def get_driver():
	driver = False

	config = ConfigParser.ConfigParser()
	config.read(os.environ.get('LOBSTERCORE_CONFIG'))
	driver_config = dict(config.items('search'))

	if config.get('search', 'enabled', False) is False:
		return driver

	if config.get('search', 'driver') == 'solr':
		driver = Solr(driver_config);

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
