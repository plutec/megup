import settings
import mega as mega_library

class UploaderMega(object):
	"""
	This class is use for managing files and folders with mega
	"""

	mega = None
	def __init__(self):
		"""
		Constructor
		"""
		self.mega = mega_library.Mega({'verbose':
											settings.settings['mega_verbose']})
		#print settings.settings['mega_mail']
		self.mega.login(email=settings.settings['mega_mail'],
							password=settings.settings['mega_passw'])

	def upload(self, path, filename):
		"""
		Upload a file to Mega
		Params:
			self, the object
			path, string with remote path
			filename, string with path and filename in local
		Return:
			Nothing
		"""
		# Save in mega in folder 'path' with the original name
		folder = self.mega.find(path)
		if not folder:
			self.mkdir(path)
			folder = self.mega.find(path)
		self.mega.upload(filename, folder[0])
		

	def get_last_upload(self):
		"""
		Get time of the last upload to Mega
		"""
		pass

	def get_user_info(self):
		"""
		Obtain mega user information in json format
		"""
		details = self.mega.get_user() #Make up this data. :)
		return details

	def find_folder(self, foldername):
		"""
		Find a folder in mega.
		Params:
			self, the object
			foldername, string with the name of folder
		Return:
			dictionary with information about the folder
		"""
		return self.mega.find_folder(foldername)
		
	def mkdir(self, dirname):
		"""
		Create a remote folder
		Params:
			dirname: string with the complete path (i.e.: pepito/lechuga/fria)
		"""
		folders = dirname.split('/')
		parent_desc = self.mega.get_root_descriptor()
		for folder in folders:
			#Exists folder with this parent?
			exists = self.mega.find_folder(folder, parent=parent_desc)
			if not exists:
				data = self.mega.create_folder(folder, parent_desc)
				parent_desc = data['f'][0]['h']
			else:
				parent_desc = exists[0]


	def exists_dir(self, dirname):
		"""
		Check if a directory exists in mega
		Params:
			self, the object
			dirname, string with complete remote path
		"""
		folder = self.mega.find(dirname)
		if folder: return True
		return False

	def free_space(self):
		"""
		Obtain the remote space left in Mega
		"""
		return self.mega.get_storage_space()#bytes=True)

