### Various useful functions ###

import itertools

def isplit(iterable,marker):
        ### splits an iterable in groups delimited by marker ###
        return[list(g) for k,g in itertools.groupby(iterable,lambda x:x in marker) if not k]


def extract_proj(path):
	### Takes a path /aaa/bbb/ccc and returns /aaa/bbb ###
	path_in_list = list(path)
	path_in_parts = isplit(path_in_list,'/')
	new_parts = ["".join(x) for x in path_in_parts[:-1]]
	new_path = "/"+"/".join(new_parts)	
	return(new_path)

def extract_calc(path):
	### Takes a path /aaa/bbb/ccc and returns ccc ###
	path_in_list = list(path)
	path_in_parts = isplit(path_in_list,'/')
	new_path = "".join(path_in_parts[-1])	
	return(new_path)

def read_lines(input_file):
    ### returns a list of lines by reading a file. Full path must be included. ###
    with open(input_file,'r') as reading_input:
        lines = reading_input.readlines()
    return(lines)

def write_lines(content,output_file):
    ### writes content (a list of lines) on output_file. Full path must be included. ###
    with open(output_file,'w') as writing_output:
        writing_output.writelines(content)

