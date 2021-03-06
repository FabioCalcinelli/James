import os
import subprocess
import glob
import utilities


class open_log(object):
	""" A open_log object. It is created from a .log file opened as a list of lines """
	def __init__(self,log_lines):
		self.content = log_lines

	def __str__(self):
		return('james.py open_log object')

class open_com(object):
	""" A open_com object. It is created from a .com file opened as a list of lines """
	def __init__(self,com_lines):	
		### The content should always be consistent with the content of the real .com file ###
		self.content = com_lines
		self.settings = None	
		self.parameters = None
		self.description = None
		self.charge_spin = None
		self.coordinates = None
		self.read_content()
	
	def read_content(self):
		### Reads the content of the lines and updates the attributes ###
		self.settings = []	
		self.parameters = []
		self.description = []
		self.charge_spin = []
		self.coordinates = []
		got_to_descr = False
		finished_descr = False
		got_to_coords = False
		for line in self.content:
			if line[0] == '%':
				self.settings += [line]
			elif line[0] == '#':
				self.parameters += [line]
			elif line == '\n':
				if not(got_to_descr):
					got_to_descr = True
				elif got_to_descr:
					got_to_descr = False
					finished_descr = True
			if got_to_descr and line != '\n':
				self.description += [line]
			if finished_descr and not(got_to_coords) and line != '\n':
				self.charge_spin += [line]
				got_to_coords = True
			if got_to_coords and line != '\n':
				self.coordinates += [line]

	def write_content(self):
		### Reads the attributes and updates the content of the lines ###
		if None not in (self.settings,self.parameters,self.description,self.charge_spin,self.coordinates):
			content = self.settings+self.parameters+['\n']+self.description+['\n']+self.charge_spin+self.coordinates+['\n']
			self.content = content
		else:
			raise Exception('Not all content is correctly specified') 		
	
	def __str__(self):
		return('james.py open_com object')

class open_subsh(object):
	""" A open_subsh object. It is created from a sub.sh file opened as a list of lines """
	def __init__(self,subsh_lines):
		self.content = subsh_lines	
		### a more detailed control over sub.sh is to be implemented ###
		self.job_name = None
		self.output_number = None
		self.read_content()
	
	def read_content(self):
		### Reads the content and updates the attributes ###
		for line in self.content:
			if line[:19]=="#SBATCH --job-name=":
				self.job_name = line[20:] 
			elif line [:4] == 'srun': 
				words = line.split()
				self.output_number = words[-1][:-4]	


	def write_content(self):
		### Reads the attributes and updates the content of the lines ###	
		lines = self.content
		new_lines = []
		for line in lines:
			if line[:19]=="#SBATCH --job-name=":
				new_lines += '#SBATCH --job-name='+self.output_number+'\n'
			elif line [:4] == 'srun':
				new_lines += 'srun --ntasks=1 --hint=nomultithread --cpus-per-task=32 --mem_bind=v,local ${GAUSSIAN09_HOME}/g09 < '+self.output_number+'.com > '+self.output_number+'.log'
			else:
				new_lines += line
		self.content = new_lines

	def __str__(self):
		return('james.py open_subsh object')

class calculation(object):
	"""A calculation is associated with a folder, in which all the relative files are stored."""
	def __init__(self,calc_folder):
		### The calculation is defined by its input (.com), output (.log), and sub.sh ###
		if '/' not in list(calc_folder):
			calc_folder = (subprocess.check_output(['pwd'])).strip()+'/'+calc_folder 
		self.name = utilities.extract_calc(calc_folder)
		self.location = self.get_location(calc_folder)
		self.folder_content = self.update_folder_content()
		self.log = self.create_open_file('.log') 
		self.com = self.create_open_file('.com')
		self.subsh = self.create_open_file('sub.sh')
		self.status = self.get_calculation_status()

	def get_location(self,calc_folder):
		### If a folder calc_folder exists, saves it as location. Otherwise, creates it. ###
		batch_dir = utilities.extract_batch(calc_folder)
		folders = glob.glob(batch_dir+'/*')
		if calc_folder not in folders:
			subprocess.call(['mkdir',calc_folder])
		return(calc_folder)

	def get_calculation_status(self):
		### Possible status: Not started , Running , Complete , Error, Something's weird ###
		normal = False
		error = False
		if self.log == None:
			no_log = True
		else:
			lines=self.log.content
			no_log = False
			if " ".join(lines[-1].split()[:2]) == 'Normal termination':
				normal = True
			if " ".join(lines[-3].split()[:2]) == 'Error termination' or " ".join(lines[-2].split()[:2]) == 'Error termination' or " ".join(lines[-1].split()[:2]) == 'Error termination':
				error=True
		error_std = self.check_stderr()
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
	
	def create_open_file(self,file_type):
		### If .com/.log/sub.sh is present, reads it. Otherwise, returns None ###
		if file_type == ".com":
			file_name = self.location+'/'+self.name+'.com'
		elif file_type == ".log":
			file_name = self.location+'/'+self.name+'.log'
		elif file_type == "sub.sh":
			file_name = self.location+'/'+file_type
		else:
			return(None)
		self.update_folder_content
		if file_name in self.folder_content:
			file_lines = utilities.read_lines(file_name)	
			if file_lines == [] or file_lines == ['\n']:
				return(None)
			else:
				if file_type == ".com":
					opened = open_com(file_lines)
				elif file_type == ".log":
					opened = open_log(file_lines)
				elif file_type == "sub.sh":
					opened = open_subsh(file_lines)
				return(opened)
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
		if err_name in self.folder_content:
			err_lines = utilities.read_lines(err_name)
			if 'Error: software termination\n' in err_lines:
				return(True)
			elif 'Error: segmentation violation\n' in err_lines:
				return(True)
			else:
				return(False)
		else:
			return(None)

	def write_com_sub(self):
		### Writes down .com and sub.sh files as per self.file.content ###		
		com_name = self.location+'/'+self.name+'.com'
		utilities.write_lines(self.com.content,com_name)
		sub_name = self.location+'/'+'sub.sh'
		utilities.write_lines(self.subsh.content,sub_name)

	def run(self):
		subprocess.call(['sbatch','sub.sh'],cwd=self.location)		

	def __str__(self):
		return(self.name+" | "+self.status+"\n")		
				
class batch(object):
	"""A batch is associated with a folder. Each batch is composed of several calculations, each one associated with a secondary folder."""
	def __init__(self,batch_folder):
		### the batch  is defined by its calculations, sub.sh file, status file, parameters file, structures file###
		self.name = utilities.extract_calc(batch_folder)
		self.father_project_folder = utilities.extract_batch(batch_folder)
		self.location = self.get_location()
		self.folder_content = self.update_folder_content()
		self.calculations = self.get_calculations()
		self.status = self.read_status()
		self.subsh_prototype = self.read_subsh()
		self.write_down_status()
		self.execution_parameters = self.read_parameters()
	
	def get_location(self):
		### Reads the location of the batch main folder. If location doesn't exist, creates it. ###
		batch_dir = self.father_project_folder+'/'+self.name
		folders = glob.glob(self.father_project_folder+'/*')
		if batch_dir not in folders:
			subprocess.call(['mkdir',batch_dir])
		return(batch_dir)

	def get_calculations(self):
		### Checks all the subfolders in the batch folder, creates a calculation object for each, and appends them as attributes of the batch object ###
		calculations=[]
		folder_content = glob.glob(self.location+'/*')
		for entity in folder_content:
			if os.path.isdir(entity):
				calc = calculation(entity)		
				calculations += [calc]
		return(calculations)
	
	def read_status(self):
		### Read from james ###
		""" Collects informations from each calculations and records it in a status object """
		return(None)
	
	def write_down_status(self):
		""" Writes down the status object in a text 'status' file """
		return(None)
		
	def read_subsh(self):
		### If sub.sh is present, and not empty, reads it. Otherwise, returns None ###
		file_name = self.location+'/sub.sh'
		self.update_folder_content
		if file_name in self.folder_content:
			file_lines = utilities.read_lines(file_name)	
			if file_lines == [] or file_lines == ['\n']:
				return(None)
			else:
				opened = open_subsh(file_lines)
				return(opened)
		else:
			return(None)

	def read_parameters(self):
		self.update_folder_content

	def update_folder_content(self):
		contents = glob.glob(self.location+'/*')
		return(contents)

	def launch_calculations(self,parameters,coordinates):
		

	def __str__(self):
		calculations = ""
		for calc in self.calculations:
			calculations += str(calc)
		return(self.name+"  |  "+"james.py batch object"+"\n"+"Location: "+self.location+'\n'+"Calculations:"+"\n"+calculations)
#### da formattare per bene ####


class project(object):
	"""A project is associated with a folder. Each project is composed of several batches, each one associated with a secondary folder."""
	def __init__(self,project_name):
		### the project is defined by its batches, including a special 'complete' batch ###
		self.name = str(project_name)
		self.location = self.get_location()
		self.batches = self.get_batches()
	
	def get_location(self):
		### Reads the location of the project main folder. If location doesn't exist, creates it. ###
		working_dir = (subprocess.check_output(['pwd'])).strip()
		project_dir = working_dir+'/'+self.name
		folders = glob.glob(working_dir+'/*')
		if project_dir not in folders:
			subprocess.call(['mkdir',project_dir])
		return(project_dir)

	def get_batches(self):
		### Checks all the subfolders in the project folder, creates a batch object for each, and appends them as attributes of the project object ###
		batches=[]
		folder_content = glob.glob(self.location+'/*')
		for entity in folder_content:
			if os.path.isdir(entity):
				bat = batch(entity)		
				batches += [bat]
		return(batches)
	
	def update_folder_content(self):
		contents = glob.glob(self.location+'/*')
		return(contents)

	def __str__(self):
		batches = ""
		for bat in self.batches:
			batches += str(bat)
		return(self.name+"  |  "+"james.py project object"+"\n"+"Location: "+self.location+'\n'+"Batches:"+"\n"+batches)
#### da formattare per bene ####
		
