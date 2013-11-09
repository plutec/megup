import settings
import uploader
import os
import filesystem

class Backup(object):

	recursive = None
	path = None
	uploader = None
	filesystem = None

	def __init__(self, path):
		self.recursive = True
		self.path = path
		self.uploader = uploader.UploaderMega()
		self.now_path = path

	def prepare_to_init_backup(self):
		self.uploader.mkdir(settings.settings['remote_folder'])


	def visit_path(self):
		"""
		Visit path and create summary file in binary
		"""
		level = 0
		for root, subfolders, files in os.walk(self.path):
			#print root
			if not level:
				actual_remote_folder = settings.settings['remote_folder']
			else:
				actual_remote_folder = '%s/%s' % \
					(actual_remote_folder, root.split('/')[-1])


			#For each files
			for fil in files:
				print "SUBO %s a %s" % (fil ,actual_remote_folder)
				file_path = os.path.join(root, fil) 
				print "ORIGEN %s" % file_path
				#print file_path
				self.uploader.upload(actual_remote_folder, file_path)
			
			#For each subfolder
			for subfolder in subfolders:
				print "CREO carpeta %s" % actual_remote_folder+'/'+subfolder
				folder = os.path.join(actual_remote_folder, subfolder)
				self.uploader.mkdir(folder)
			level += 1
			print ('*'*80)

			#print root
			#print files
			#print subfolders