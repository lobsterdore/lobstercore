
class Document:
	id = None

	def __init__(self, id):
		self.id = id

class ContentDocument(Document):
	id = None
	type = None
	title = None
	text = None
	category = None
	data = None

	def __init__(self, id, type, title, text, category, data):
		self.id = id
		self.type = type
		self.title = title
		self.text = text
		self.category = category
		self.data = data
