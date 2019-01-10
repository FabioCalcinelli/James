import os
import subprocess
import glob
import utilities

class calculation(object):
	"""A calculation is associated with a folder, within which all the relative files are stored."""
	def __init__(self,calc_folder):
		### The calculation is defined by its input (.com), output (.log), and sub.sh ###
		if '/' not in list(calc_folder):
			calc_folder = (subprocess.check_output(['pwd'])).strip()+'/'+calc_folder 
		self.name = utilities.extract_calc(calc_folder)
		self.location = self.get_location(calc_folder)
		self.folder_content = self.update_folder_content()
		self.status = self.get_calculation_status()
		
	def get_location(self,calc_folder):
		### If a folder calc_folder exists, saves it as location. Otherwise, creates it. ###
		project_dir = utilities.extract_proj(calc_folder)
		folders = glob.glob(project_dir+'/*')
		if calc_folder not in folders:
			subprocess.call(['mkdir',calc_folder])
		return(calc_folder)

	def get_calculation_status(self):
		### Possible status: Not started , Running , Complete , Error, Something's weird
		log_lines = self.open_log_in_lines()
		normal = False
		error = False
		if log_lines == None:
			no_log = True

		else:
    			no_log = False
        		if " ".join(log_lines[-1].split()[:2]) == 'Normal termination':
                		normal = True
        		if " ".join(log_lines[-3].split()[:2]) == 'Error termination' or " ".join(log_lines[-2].split()[:2]) == 'Error termination' or " ".join(log_lines[-1].split()[:2]) == 'Error termination' :
                		error = True
		error_std = self.check_stderr()
		print('normal: ',normal)
		print('error: ',error)
		print('no_log: ',no_log)
		print('error_std: ',error_std)
		print('self.name: ',self.name)
		print('self.location: ',self.location)
		if no_log == True and error_std == None and normal == False and error == False:
			return('Not started')
		elif no_log == False and error_std == False and normal == False and error == False:
			return('Running')
		elif no_log == False and error_std == False and normal == True and error == False:
			return('Complete')
		elif no_log == False and normal == False and (error == True or error_std == True) == True:
			return('Error')
		else:
			return("Something's weird")
			
			
	def open_log_in_lines(self):
		### If .log is present, reads it. Otherwise, returns None. ###
		log_name = self.location+'/'+self.name+'.log'
		print(log_name)
		self.update_folder_content
		if log_name in self.folder_content:
			log_lines = utilities.read_lines(log_name)
			return(log_lines)
		else:
			return(None)

	def update_folder_content(self):
		### Updates the list reporting the content of the calculation folder ###
		contents = glob.glob(self.location+'/*')
		return(contents)
	
	def check_stderr(self):
		### Checks if a std.err file is present in the folder, and if it reports an error ###
		self.update_folder_content
		err_name = self.location+'/std.err'
		print('err_name',err_name)
		if err_name in self.folder_content:
			err_lines = utilities.read_lines(err_name)
			print(err_lines)
			if 'Error: software termination\n' in err_lines:
				return(True)
			else:
				return(False)
		else:
			return(None)
	def __str__(self):
		return("I'm a calculation!")		
		
class project(object):
	"""A project is associated with a main folder. Each project is composed of several calculations, each one associated with a secondary folder."""
	def __init__(self,project_name):
		### The project is defined by its calculations, by its sub.sh prototype file, and by its status and results files ###
		self.name = str(project_name)
		self.location = self.get_location()
		self.calculations = self.get_calculations()
		self.status = self.read_status()
		self.results = self.read_results()
		self.subsh_prototype = self.read_subsh()
	
	def get_location(self):
		### Reads the location of the project main folder. If location doesn't exist, creates it. ###
		working_dir = (subprocess.check_output(['pwd'])).strip()
		project_dir = working_dir+'/'+self.name
		folders = glob.glob(working_dir+'/*')
		if project_dir not in folders:
			subprocess.call(['mkdir',project_dir])
		return(project_dir)

	def get_calculations(self):
		### Checks all the subfolders in the project folder, creates a calculation object for each, and appends them as attributes of the project object ###
		calculations=[]
		folder_content = glob.glob(self.location+'/*')
		for entity in folder_content:
			if os.path.isdir(entity):
				calc = calculation(entity)		
				print('ENTITY',entity)
		return(None)
	
	def read_status(self):
		return(None)

	def read_results(self):
		return(None)
		
	def read_subsh(self):
		### If a sub.sh file is located in the project folder, reads it and appends its content as attribute of the project object. If no sub.sh file exists, writes a warning ###
		return(None)
	
	def update_folder_content(self):
		contents = glob.glob(self.location+'/*')
		return(contents)
	def __str__(self):
		return("I'm a project!")

