"""
import rsync
import mega

#https://github.com/richardasaurus/mega.py
mega = mega.Mega({'verbose':True})

m = mega.login(email='asanchez@plutec.net',password='sdfasdfasdf)

details = m.get_user()


#print details
# specify unit output kilo, mega, gig, else bytes will output
space = m.get_storage_space(giga=True)

#print space

folder = m.find('syncpy')
#m.upload('test_files/1.pdf', folder[0])

"""
import settings
import mega as mega_library

class UploaderMega(object):
	mega = None
	def __init__(self):
		self.mega = mega_library.Mega({'verbose':settings.settings['mega_verbose']})
		#print settings.settings['mega_mail']
		self.mega.login(email=settings.settings['mega_mail'],
							password=settings.settings['mega_passw'])
	def upload(self, path, filename):
		# Save in mega in folder 'path' with the original name
		folder = self.mega.find(path)
		if not folder:
			self.mkdir(path)
			folder = self.mega.find(path)
		self.mega.upload(filename, folder[0])
		

	def get_last_upload(self):
		pass

	def get_user_info(self):
		details = self.mega.get_user() #Make up this data. :)
		return details

	def find_folder(self, foldername):
		self.mega.find_folder(foldername)
		
	def mkdir(self, dirname): #Something like pepito/lechuga/fria
		#TODO
		folders = dirname.split('/')
		acum = folders[0]
		dest = self.mega.find(acum)
		for folder in folders[1:]:
			self.mega.create_folder(folder, dest[0])
			acum = '%s/%s' % (acum,folder)
			dest = self.mega.find(acum)


	def exists_dir(self, dirname):
		folder = self.mega.find(dirname)
		if folder: return True
		return False

	def free_space(self):
		return self.mega.get_storage_space()#bytes=True)

	

u = UploaderMega()
u.exists_dir('syncpy')
#print u.free_space()