# James

A set of tools for launching and managing Gaussian calculations on a Slurm platform.\
James.py is designed to work in a project/ folder, containing james.py, writer.py and a sub.sh file.\
Within project/ , batch/ folders are created for every batch of calculations. A batch/ folder should include a link to james.py , a copy of writer.py and a sub.sh file.\
As james.py is used to launch calculations, it will produce an index file keeping track of all the calculations contained in the batch/.\
Within project/batch/ , single folders named as numbers contain single calculations.

Dependencies:
- Python 2.7.x
- Gaussian 09
- Pandas >=0.22.0
- openpyxl >=2.6.0

Installation:

Copy james.py and writer.py in project/ , include project/ into PYTHONPATH.\
For a quicker use of some important functions, add the following aliases to .bashrc.\
alias update='python james.py update'\
alias mass_restart='python james.py mass_restart'\
alias status='python james.py check status; vim status'\
alias statusf='python james.py check status freq; vim status'\

Available functions:

- prepare

Prepares a batch folder, creating it and copying sub.sh, writer.py, and a link to james.py  
>>> python james.py prepare folder_name 

- run

Launches a gaussian calculation creating a new folder and renaming all files coherently.\
Note: a sub.sh file must be present in the same folder as the script.
>>> python james.py run input_com output_number

- write

Launches multiple calculations iterating on different parts of the .com file.\
Each element can be given as a single element (to be repeated), as a list (to be iterated), or as a tuple (composed of single elements and lists).\
Files are named as progressive numbers starting from the given first_number.\
Coordinates are retrieved from a coords_file.\
Note: all elements must have the same length (unless they are single, in which case they will be replicated to adapt the length of other elements).\
Note: the coords_file must include one single empty line between different structures, and no other empty line (neither at the beginning, nor at the end).\
>>> python james.py write coords_file first_number

- check

Checks the status of the calculations listed in index, and stores data in a status file.\
If frequency_mode = True, it reads free-energy values. Useful for frequency calculations.\
Note: for the description of the calculation to be successfully included in the results file, it must begin with 'Dscr'.
>>> python james.py check results_file (frequency_mode)

- convert

Converts the result of an optimization in a new .com file.\
Note: (termination_line) parameter must be a line, found in the .log file, that follows the particular optimization step from which we want to extract the geometry. For example, the 'Maximum Displacement ...' line can be used. If no parameter is given, the last structure is selected
>>> python james.py convert log_file com_file (termination_line)

- restart

Prepares a calculation to be restarted, from a particular selected structure.\
Note: works from the main directory.
>>> python james.py restart input_number termination_line

- mass_restart

Launches a gaussian calculation creating a new folder and renaming all files coherently. \
NOTE: a sub.sh file must be present in the same folder as the script.
>>> python james.py run input_com output_number

- branch

Restarts a calculation multiple times, allowing the user to modify its execution parameters.\
Note: give 'done' as an input to stop producing new calculations.
>>> python james.py branch input_number termination_line

- update

Updates the index file to include all the folders existing at the moment.
Branches are listed under their parent calculation.
>>> python james.py update

- rename

Renames a calculation folder, changing the name in all the files within the folder. Updates the index.
>>> python james.py rename old_name new_name 

- collect

Reads the last configurations obtained by a sequence of calculations, and stores them in a coordinates_file.\
Note: numbers can be given as a space separated list within '' (ex. '1 2 4 5 12') or as a '-' separated interval (es 5-10). In the second case, it includes the extremes.
>>> python james.py collect calculations_numbers coordinates_file

- unpack

Splits a coords_file containing multiple structures into individual .xyz files.
>>> python james.py unpack coords_file xyz_name_nonumber

- repack

Takes all the files xyz_name_nonumber_N.xyz, with N included in numbers, and packs them in a single coordinates file.\
Note: numbers can be given as a space separated list within '' (ex. '1 2 4 5 12') or as a '-' separated interval (es 5-10). In the second case, it includes the extremes.
>>> python james.py repack xyz_name_nonumber numbers coordinates_file

- rmsd

Takes the .log file of an optimization and returns the Root Mean Square Displacement of every geometry optimization step.
>>> python james.py rmsd logfile results

- excel

Stores the current status of the batch in a numerical_status.xlsx file.
>>> python james.py excel
