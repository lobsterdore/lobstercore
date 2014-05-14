import pysolr, json, datetime
from abc import ABCMeta, abstractmethod, abstractproperty
from time import mktime

class Driver:
	__metaclass__ = ABCMeta

	config = {}

	__init__(self, config):
		self.config = config

	@abstractmethod
	def update_search(mapper, connection, target):
		pass

	@abstractmethod
	def remove_from_search(mapper, connection, target):
		pass

class Solr(Driver):

	def update_search(mapper, connection, target):
		solr = pysolr.Solr(config.get('search', 'endpoint'), timeout=10)
		search_document = target.get_search_document()
		search_data = {
			"id": search_document.id,
			"type":search_document.type,
			"title": search_document.title,
			"text": search_document.text,
			"category": search_document.category,
			"data":search_document.data
		}
		solr.add(search_data)

	    '''
	    solr.add([
	        {
	            "id": target.id,
	            "type": "Content",
	            "title": target.title,
	            #"slug": target.slug,
	            "text": target.body,
	            "category": target.section.title,
	            "data": json.dumps( target.to_dict({'section' : {}}), cls = DatetimeJsonEncoder)
	            #"publish_date": target.publish_date,
	            #"section_title": target.section.title,
	            #"section_slug": target.section.slug
	        }
	    ])
	    '''

	def remove_from_search(mapper, connection, target):
		solr = pysolr.Solr(config.get('search', 'endpoint'), timeout=10)
		search_document = target.get_search_document()
		solr.delete(id=search_document.id)

Driver.register(Solr)

