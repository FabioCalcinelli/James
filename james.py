### Tools for working with Gaussian 09 and slurm ###
### python james.py function (parameters) ###
### functions:  run	
#		convert
#		read
#		check
#		write
#		collect
#		unpack	
#		repack
#		rmsd
#		restart

import subprocess
import sys
import itertools
import math
import glob
import os

elements = {0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49:
'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96:
'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm', 101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt', 110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'}

current_dir = (subprocess.check_output(['pwd'])).strip()

################################################################################################
##################################### Auxiliary Functions ######################################
################################################################################################

def read_lines(input_file):
	### returns a list of lines by reading a file ###
	### folder must be included in the name ###
	with open(input_file,'r') as reading_input:
		lines = reading_input.readlines()
	return lines

def write_lines(content,output_file):
	### writes content (a list of lines) on output_file ###
	### folder must be included in output_file name ###
	with open(output_file,'w') as writing_output:
		writing_output.writelines(content)

def read_description(log_lines):
	### extracts the description of the calculation from a .log file ###
	### the .log file must be given as a list of lines ###
	### the description must begin with 'Dscr'
	for line in log_lines:
		if line.strip():
			if line.split()[0] == 'Dscr':
				return(line.strip())

def evaluate_status(log_lines):
	### evaluates if a .log file corresponds to a completed, failed or progressing calculation. Returns 'Mistery' if something is really wrong ###
	### the .log file must be given as a list of lines ###
	normal = False
        error = False
        if " ".join(log_lines[-1].split()[:2]) == 'Normal termination':
                normal = True
        if " ".join(log_lines[-3].split()[:2]) == 'Error termination' or " ".join(log_lines[-2].split()[:2]) == 'Error termination' or " ".join(log_lines[-1].split()[:2]) == 'Error termination' :
                error = True
        if normal == True and error == False:
                return('Success')
        if normal == False and error == True:
                return('Failure')
        if normal == False and error == False:
                return('Working')
        if normal == True and error ==True:
                return('Mistery')

def read_energy(log_lines,freq_mode):
	### reads the energy of the configuration resulting from a successful calculation. If the calculation includes frequency calculation, freq_mode must be True ###
	### the .log file must be given as a list of lines ###
	if freq_mode:
                for line in log_lines:
                        if len(line.split()) >= 7:
                                if " ".join(line.split()[:7]) == 'Sum of electronic and thermal Free Energies=':
                                        return(line.split()[7])
        else:
                for line in log_lines:
                        if len(line.split()) >= 3:
                                if " ".join(line.split()[:2]) == 'SCF Done:':
                                        value = (line.split()[4])
                return value

def check_minimum(log_lines):
	### verifies that the resulting structure of an optimization is actually a local minimum (has no negative vib. frequency) ###
	### the .log file must be given as a list of lines ###
	on = False
        negs=[]
        all_positives = True
        for line in log_lines:
                if len(line.split()) >= 7:
                        if " ".join(line.split()[:7]) == 'Sum of electronic and thermal Free Energies=':
                                on = True
                        if line.split()[0] == 'Eigenvalues':
                                if on:
                                        if float(line.split()[2]) < 0:
                                                negativ_eigen = float(line.split()[2])
                                                negs += [negativ_eigen]
                                                all_positives = False
        if all_positives:
                return ('(Confirmed local minimum)')
        else:
                return('***WARNING: negative eigenvalue detected: '+str(negs)+' *** ')

def read_opt_status(log_lines):
	### returns a tuple containing the number of geometry opt. steps completed so far and the convergence parameters of the last one
	result=[0,None,None,None,None]
        for line in log_lines:
                if line.strip():
                        if line[:14] == ' Maximum Force':
                                result[0] += 1
                                result[1]=line.split()[2]
                        if line[:14] == ' RMS     Force':
                                result[2]=line.split()[2]
                        if line[:14] == ' Maximum Displ':
                                result[3]=line.split()[2]
                        if line[:14] == ' RMS     Displ':
                                result[4]=line.split()[2]
        return(tuple(result))

def read_coords(coords_file):
	### reads a coordinates_file and returns a list (scructures) of lists (atoms)	
	### (NOTE: the file must contain NO empty line, except ONE between structures)

	with open((coords_file),'U') as coords:
        	coords_text = coords.read()
        	blocks = coords_text.split('\n\n')
        	if len(blocks) == 1:
                	coordinates = [str(blocks[0]).strip()]
        	else:
                	coordinates = blocks
                	coordinates[-1] = coordinates[-1][:-1]
	return coordinates

def get_numbers_range(str_numbers):
		### Extracts number range from string. Numbers can be given as a space separated list within '' (ex. '1 2 4 5 12') or as a '-' separated interval (es 5-10). In the second case, it includes the extremes.
	if '-' in str(str_numbers):
        	first=''
        	second=''
        	got=False
        	for char in str(str_numbers):
                	if char=='-':
                        	got=True
                	else:
                        	if got:
                                	second+=char
                        	else:
                                	first+=char
        	first=int(first)
        	last=int(second)
        	numbers = [str(x) for x in range(first,last+1)]
	else:
        	numbers = [str(x) for x in str(str_numbers).split(' ')]
	return numbers

def isplit(iterable,marker):	
	### splits an iterable in groups delimited by marker ###
    	return[list(g) for k,g in itertools.groupby(iterable,lambda x:x in marker) if not k]

def calc_rmsd(one,two):
	### computes the Root Mean Square Displacement between two structures ###
        summatory=0
        for n in range(len(one)):
                first=one[n]
                second=two[n]
                delta2=(float(first)-float(second))**2
                summatory+=delta2
        rmsd = math.sqrt(summatory/len(one))
        return(rmsd)


###############################################################################################
################################### Main Functions ############################################
###############################################################################################

def run(input_com,output_number,current_dir):
	### Executes a gaussian calculation smartly. ###
	
	###_____>>> python james.py run input_com output_number <<<_____
	
	### NOTE: a sub.sh file must be present in the same folder as the script 
	
	### 1) Creates a folder \output_number
	new_dir = (str(current_dir)+'/'+str(output_number))
	subprocess.call(['mkdir',new_dir])
		
	### 2) Copies input_com and sub.sh in the new folder
	new_input_com = new_dir+str('/'+output_number+'.com')
	subprocess.call(['cp',input_com,new_input_com])
	subprocess.call(['cp','sub.sh',new_dir])

	### 3) Edits the sub.sh, changing job_name, input and output
	lines = read_lines(current_dir+'/sub.sh')
	new_lines = []
	for line in lines:
		if line[:19]=="#SBATCH --job-name=":
                        new_lines += '#SBATCH --job-name='+output_number+'\n'
                elif line [:4] == 'srun':
                        new_lines += 'srun --ntasks=1 --hint=nomultithread --cpus-per-task=32 --mem_bind=v,local ${GAUSSIAN09_HOME}/g09 < '+output_number+'.com > '+output_number+'.log'
                else:
                        new_lines += line
	subprocess.call(['rm','sub.sh'],cwd=new_dir)
	write_lines(new_lines,new_dir+'/sub.sh')

	### 4) Submits the calculation
	subprocess.call(['sbatch','sub.sh'],cwd=new_dir)

def convert(log_file,com_file,termination_parameter,current_dir):
	### Converts the result of an optimization in a new .com file ###	

	###_____>>> python james.py convert log_file com_file (termination parameter) <<<_____

	### NOTE: termination parameter is a line following the desired structure. If no parameter is given, last structure is selected
			
	### 1) Sets up some initial objects
	in_lines = read_lines(current_dir+'/'+log_file)
	out_lines = []
	geometry_rec_1 = False
	geometry_rec_2 = False
	geometry = []
	command_lines = []
	charge_rec = True
	command_rec = False
	comment = ''
	for line in in_lines:
		### 2) Records the execution parameters
		if line.strip():
        		if line[1] == '%':
            			command_lines += ["".join(line[1:])]
			elif line[1] == '#':
				command_lines += ["".join(line[1:])]	
				command_rec = True
        		elif line.split()[0] == 'Charge':
				if charge_rec:
            				charge_spin = "".join(line.split()[2]+' '+line.split()[5])
					charge_rec = False
			elif line.split()[0] == 'Dscr':
				comment += line[1:]
			elif command_rec:
				if line[1] != '-':
					command_lines[-1] = command_lines[-1][:-1]
					command_lines[-1] += str(line)[1:]
				command_rec = False
		### 3) Detects a new geometry: cancels the old one and prepares to record the new one
		if line.strip() =='Number     Number       Type             X           Y           Z':
		        geometry_rec_1 = True
        		geometry = []
		### 4) Records the geometry ...
		if line.strip() and line.split()[0] == '1':
		        if geometry_rec_1:
            			geometry_rec_2 = True
		### ... until the geometry ends ...
		if geometry_rec_2 and geometry_rec_1:
			if line[1] == '-':
				geometry_rec_2 = False
				geometry_rec_1 = False
		### ... converting atomic numbers to symbols
		if geometry_rec_2 and geometry_rec_1:
            		data = line.split()
         		symbol = elements[int(data[1])]
            		new_line = [symbol+line[(29+len(symbol)):]]
            		geometry += new_line
		### 5) If a termination parameter is chosen, stops when it encounters it
		if termination_parameter != None and line.strip() == termination_parameter:
			break
	### 6) Composes and writes the new .com file
	out_lines += command_lines
	out_lines += ['\n'+comment+'\n']
	out_lines += [charge_spin+'\n']
	out_lines += geometry+['\n']	
	write_lines(out_lines,com_file)

def read(index_file,results_file,freq_mode,current_dir):
	### Reads the results of all the calculations listed in index, and writes them in a results file ###       

        ###_____>>> python james.py read index_file results_file ('freq' for reading a freq calc.) <<<_____

	### NOTE: for the description of the calculation to be successfully included in the results file, it must begin with 'Dscr'

	### 1) Sets up initial dicts
	results = dict()
	descriptions = dict()
	numbers=[]
	### 2) Reads the index, and passes through each calculation listed there
	index = read_lines(current_dir+'/'+index_file)
	for line in index:
		if line.strip():
			### 3) Records the description of the calculation in descriptions dict
			words = line.split()
			number = words[0]
			numbers.append(number)
			description = ' '.join(words[2:])
			log_lines = read_lines(current_dir+'/'+number+'/'+number+'.log') 
			descriptions[number] = read_description(log_lines) 
			### 4) Evaluates the status of the calculation and stores it as success, failure, working or mistery
			decision = evaluate_status(log_lines)
			if decision == 'Working':
                results[number] = ['In progress']+[""]+[""]
            elif decision == 'Success':
			### 5) If the calculation is successful, records its result
		if freq_mode:                
			results[number] = ['Completed: ']+[str(read_energy(log_lines,freq_mode))]+[str(check_minimum(log_lines))]
		else:
			results[number] = ['Completed: ']+[str(read_energy(log_lines,freq_mode))]
            elif decision == 'Failure':
                results[number] = ['Failed']+[""]+[""]
            elif decision == 'Mistery':
                results[number] = ['*** Anomaly ***']+["tt"]+["tt"]
	### 6) Writes down the collected data
	lines = []
	for number in numbers:
                line = ('{0:2}{1:5}{2:50}{3:15}{4:15}{5:20}'.format(str(number),' --> ',descriptions[number],str(results[number][0]),str(results[number][1]),str(results[number][2])))
                lines.append(line)
                lines.append('\n'+'\n')
	write_lines(lines,current_dir+'/'+results_file)
	
def check(index_file,results_file,current_dir):
	### Checks the status of the calculations listed in index, and returns the number of steps executed so far and the data about the last cycle ###

        ###_____>>> python james.py check index_file results_file  <<<_____

	### NOTE: for the description of the calculation to be successfully included in the results file, it must begin with 'Dscr'

	### 1) Sets up initial dicts
	opt_status = dict()
	descriptions = dict()
	numbers = []
	### 2) Reads the index
	lines = read_lines(current_dir+'/'+index_file)
	for line in lines:
                if line.strip():
                        words = line.split()
                        number = words[0]
                        numbers.append(number)
                        description = ' '.join(words[2:])
                        ### 3) Collect informations for each calculation
                        log_lines = read_lines(current_dir+'/'+number+'/'+number+'.log')
                        opt_status[number]=read_opt_status(log_lines) 
                        descriptions[number] = read_description(log_lines)
	### 4) Records optimization status on results file	
	out_lines = [('{0:4}{1:1}{2:53}{3:15}{4:15}{5:15}{6:15}{7:15}'.format('Num.','','Description','N. iterations','Max. Force','RMS Force','Max. disp.','RMS disp.'))+'\n']
	for number in numbers:
                line = ('{0:2}{1:5}{2:55}{3:15}{4:15}{5:15}{6:15}{7:15}'.format(str(number),' --> ',descriptions[number],str(opt_status[number][0]),opt_status[number][1],opt_status[number][2],opt_status[number][3],opt_status[number][4]))
                out_lines.append(line)
                out_lines.append('\n'+'\n')
	write_lines(out_lines,current_dir+'/'+results_file)

def write(coords_file,index_file,first_number,current_dir):	
	### Prepares multiple calculations iterating on different parts of the .com file. Each element can be given as a single element (to be repeated), as a list (to be iterated), or as a tuple (composed of single elements and lists). Files are named as progressive numbers starting from the given first_number ###

        ###_____>>> python james.py write coords_file index_file first_number <<<_____

	### NOTE: all elements must have the same length (unless they are single, in which case they will be replicated to adapt the length of other elements)
	
	### 1) Defines execution parameters
	intro = "%nprocshared=32 \n%mem=122GB \n%chk=q.chk"
	### 2) Defines command line
	command = "#pbe1pbe/Def2TZVP scf=(xqc, maxconventionalcycles=2000) SCRF=(SMD,Solvent=water) opt"
	### 3) Defines comment (NOTE: 'Dscr' will be added automatically)
	comment = (['1','2H','2F','3H','3F']*7, ['Fe(III) S 4']*5+['Fe(III) S 2']*5+['Fe(II) S 5']*5+['Fe(II) S 3']*5+['Fe(II) S 1']*5+['Fe(I) S 4']*5+['Fe(I) S 1']*5)
	### 4) Defines charge and spin
	charge_spin = ['1 4']*5+['1 2']*5+['0 5']*5+['0 3']*5+['0 1']*5+['-1 4']*5+['-1 2']*5
	### 5) Defines coordinates (NOTE: the file must contain NO empty line, except ONE between structures)
	coords = read_coords(current_dir+'/'+coords_file)
	coordinates = coords*7
	### 6) Defines final instructions block
	post_coord_lines = ''
	### 7) Defines a dict for the elements, and an ordered list of keys
	elements=elements = ['intro','command','comment','charge_spin','coordinates','post_coord_lines']
	elements_dict = {'intro':intro,'command':command,'comment':comment,'charge_spin':charge_spin,'coordinates':coordinates,'post_coord_lines':post_coord_lines}
	
	### 8) Checks that all iterable elements have the same length
	iterable_elements = []
	for element in elements:
        	if type(elements_dict[element]) == list:
                	iterable_elements += [elements_dict[element]]
        	elif type(elements_dict[element]) == tuple:
                	for part in elements_dict[element]:
                        	if type(part) == list:
                                	iterable_elements += [part]
	length = len(iterable_elements[0])
	for el in iterable_elements:
        	if len(el) != length:
                	print('Incongruent length: ', el)
                	exit()
	
	### 9) Prepares parallel lists of all the elements
	parallel_lists = dict()
	for element in elements:
        	if type(elements_dict[element]) is str:
                	parallel_lists[element]=[elements_dict[element] for n in range(length)]
        	elif type(elements_dict[element]) is list:
                	parallel_lists[element]=elements_dict[element]
        	elif type(elements_dict[element]) is tuple:
                	new_tuple_list=[]
                	for part in elements_dict[element]:
                        	if type(part) is str:
                                	new_tuple_list+=[[part for n in range(length)]]
                        	elif type(part) is list:
                                	new_tuple_list+=[part]
                	new_tuple = tuple(new_tuple_list)
                	parallel_lists[element]=[(" ".join([part[n] for part in new_tuple])) for n in range(length)]
	
	### 10) Writes the .com files, with the correct spacing, adding 'Dscr' to the description
	name_number = int(first_number)
	for cont in range(length):
        	with open(str(current_dir+'/'+str(name_number)+'.com'),'w') as com_file :
                	#### compose the .com file with the correct spacings and adding Dscr
                	com_file.write(parallel_lists['intro'][cont])
                	com_file.write('\n')
                	com_file.write(parallel_lists['command'][cont])
                	com_file.write('\n\n')
                	com_file.write('Dscr '+parallel_lists['comment'][cont])
                	com_file.write('\n\n')
                	com_file.write(parallel_lists['charge_spin'][cont])
                	com_file.write('\n')
                	com_file.write(parallel_lists['coordinates'][cont])
                	com_file.write('\n\n')
                	com_file.write(parallel_lists['post_coord_lines'][cont])
                	com_file.write('\n\n')
	
	### 11) Runs the calculation calling the 'run' function, recording on index and eliminating the already-copied .com file
        	run(str(name_number)+'.com',str(name_number),current_dir)
		with open(str(current_dir+'/'+'index'),'a') as index:
                	index.write(str(name_number)+'\n')
		subprocess.call(['rm',str(name_number)+'.com'])
		name_number+=1

def collect(numbers,coords_file,current_dir):	
	### Reads the last configurations obtained by a sequence of calculations, and stores them in a coordinates_file ###

        ###_____>>> python james.py collect numbers coordinates_file <<<_____

	### NOTE: numbers can be given as a space separated list within '' (ex. '1 2 4 5 12') or as a '-' separated interval (es 5-10). In the second case, it includes the extremes.

	### 1) Scans each file
	total_lines = []	
	geometry = []
	geometry_rec_1 = False
	geometry_rec_2 = False
	for number in numbers:
		in_lines = read_lines(current_dir+'/'+number+'/'+number+'.log')
		for line in in_lines:
                	### 2) Detects a new geometry: cancels the old one and prepares to record the new one
                	if line.strip() =='Number     Number       Type             X           Y           Z':
                        	geometry_rec_1 = True
                        	geometry = []
               		### 3) Records the geometry ...
                	if line.strip() and line.split()[0] == '1':
                        	if geometry_rec_1:
                                	geometry_rec_2 = True
                	### ... until the geometry ends ...
                	if geometry_rec_2 and geometry_rec_1:
                        	if line[1] == '-':
                                	geometry_rec_2 = False
                                	geometry_rec_1 = False
                	### ... converting atomic numbers to symbols
                	if geometry_rec_2 and geometry_rec_1:
                        	data = line.split()
                        	symbol = elements[int(data[1])]
                        	new_line = [symbol+line[(29+len(symbol)):]]
                        	geometry += new_line
		total_lines += geometry
		total_lines += '\n'
	### 4) Records the final result (deleting the last empty line)
	write_lines(total_lines[:-1],current_dir+'/'+coords_file)

def unpack(coords_file,xyz_name,current_dir):
	### Splits a multistructure coords_file in individual .xyz files ###
	
        ###_____>>> python james.py unpack coords_file xyz_name_nonumber numbers coordinates_file <<<_____
	
	### 1) Opens file and splits the different structures
	lines = read_lines(current_dir+'/'+coords_file)	
	strus = isplit(lines,"\n")
	### 2) Creates individual files
	cont = 1
	for stru in strus:
		with open(str(current_dir+'/'+xyz_name+'_'+str(cont)+'.xyz'),'w') as output:
	                output.write(str(len(stru)))
        	        output.write('\n\n')
                	output.writelines(stru)
                cont += 1


def repack(xyz_name,numbers,coords_file,current_dir):
	### Takes the all the files NAME_N.xyz, with N included in numbers, and packs them in a coordinates file ###

        ###_____>>> python james.py repack xyz_name_nonumber numbers coordinates_file <<<_____

	### NOTE: numbers can be given as a space separated list within '' (ex. '1 2 4 5 12') or as a '-' separated interval (es 5-10). In the second case, it includes the extremes.
	
	total_lines=[]
	for num in numbers:
		lines = read_lines(current_dir+'/'+xyz_name+'_'+str(num)+'.xyz')
		coords = lines[2:]+['\n']
		total_lines += coords
	write_lines(total_lines[:-1],current_dir+'/'+coords_file)
	
def rmsd(logfile,results,current_dir):
	### Takes the .log file of an optimization and returns the Root Mean Square Displacement of every geometry optimization step ###

        ###_____>>> python james.py rmsd logfile results <<<_____

	### 1) Defines initial lists
	rmsds=[]
	geometry=[]
	geometry_rec_1=False
	geometry_rec_2=False
	first = True
	### 2) Open files and begins scanning
	in_lines = read_lines(current_dir+'/'+logfile)
	for line in in_lines:
                ### 3) Detects a new geometry: cancels the old one and prepares to record the new one
                if line.strip() =='Number     Number       Type             X           Y           Z':
                        geometry_rec_1 = True
                        geometry = []
                ### 4) Records the geometry ...
                if line.strip() and line.split()[0] == '1':
                        if geometry_rec_1:
                                geometry_rec_2 = True
                ### ... until the geometry ends ...
                if geometry_rec_2 and geometry_rec_1:
                        if line[1] == '-':
                                geometry_rec_2 = False
                                geometry_rec_1 = False
				if first :
					### ... stores the first geometry ...	
					initial = geometry
					first = False
				else:
					### ... and compares all the others to it ...
					value = calc_rmsd(geometry,initial)       
					rmsds.append(value)
		### ... after having written down the coordinates.
		if geometry_rec_2 and geometry_rec_1:
                        data = line.split()[3:]
                        geometry += data

	### 5) Writes down the results as csv
	with open(results,'w') as output:
        	for num in rmsds:
                	output.write(str(num)+',')

def restart(input_number,termination_line,current_dir):
	### Prepares a calculation to be restarted, from a particular selected structure ###

	###____>>> python james.py restart input_number termination_line <<<____###
	
	### NOTE: works from the main directory.
	
	### 1) Calls the convert function on the selecteds structure, and stores the temporary result in the main directory
	if termination_line == None:
		subprocess.call(['python','james.py','convert',input_number+'/'+input_number+'.log','temp_conversion'])
	else:
		subprocess.call(['python','james.py','convert',input_number+'/'+input_number+'.log','temp_conversion',termination_line])
	### 2) Cleans up the input_number folder
	files = glob.glob(current_dir+"/"+input_number+'/Gau*')+glob.glob(current_dir+"/"+input_number+'/std*')+glob.glob(current_dir+"/"+input_number+'/*.chk')+glob.glob(current_dir+"/"+input_number+'/'+input_number+'*')
	for one_file in files:
		os.remove(one_file)
	### 3) Moves back the temporary .com in the folder
	subprocess.call(['mv','temp_conversion',input_number+'/'+input_number+'.com'])

##########################################################################################
################################# Function selection #####################################
##########################################################################################

if sys.argv[1]=='run':
	input_file = sys.argv[2]
	exec_name = sys.argv[3]
	run(input_file,exec_name,current_dir)
elif sys.argv[1]=='convert':
	log_file=sys.argv[2]
	com_file=sys.argv[3]
	if len(sys.argv) >= 5:
		termination_parameter = sys.argv[4]
	else:
		termination_parameter = None
	convert(log_file,com_file,termination_parameter,current_dir)
elif sys.argv[1]=='read':
	freq_mode = False
	index_file = sys.argv[2]
	results_file = sys.argv[3]
	if len(sys.argv)==5:
		if sys.argv[4]=='freq':
			freq_mode=True
	read(index_file,results_file,freq_mode,current_dir)
elif sys.argv[1]=='check':
	index_file = sys.argv[2]
	results_file = sys.argv[3]
	check(index_file,results_file,current_dir)
elif sys.argv[1]=='write':
	coords_file = sys.argv[2]
	index_file = sys.argv[3]
	first_number = sys.argv[4]
	write(coords_file,index_file,first_number,current_dir)
elif sys.argv[1]=='collect':
	numbers = get_numbers_range(str(sys.argv[2]))
	destination_file = str(sys.argv[3])
	collect(numbers,destination_file,current_dir)
elif sys.argv[1]=='unpack':
	coords_file = sys.argv[2]
	output_name = sys.argv[3]	
	unpack(coords_file,output_name,current_dir)
elif sys.argv[1]=='repack':
	xyz_name = sys.argv[2]
	numbers = get_numbers_range(sys.argv[3])
	coords_file = sys.argv[4]
	repack(xyz_name,numbers,coords_file,current_dir)
elif sys.argv[1]=='rmsd':
	logfile = sys.argv[2]
	results = sys.argv[3]
	rmsd(logfile,results,current_dir)
elif sys.argv[1]=='restart':
	input_number = sys.argv[2]
	if len(sys.argv) >= 4:
                termination_line = sys.argv[3]
        else:
                termination_line = None

	restart(input_number,termination_line,current_dir)
