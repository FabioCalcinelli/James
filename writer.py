#### Specifies the input for a series of calculations. Each element can be given as a string, a list or a tuple.
#### An element given as string will be repeated for every calculation.
#### An element given as list will be iterated over the calculations
#### An element given as tuple can be composed of different parts, and each part can be a string or a list

### 1) Intro 

intro ='%nprocshared=32 \n%mem=122GB \n%chk=q.chk'

### 2) Command

command = '#pbe1pbe/TZVP scf=(xqc, maxconventionalcycles=2000) opt Int=(Grid=Ultrafine) EmpiricalDispersion=GD3BJ'

### 3) Comment (NOTE: 'Dscr' will be added automatically)

comment = ('3F',['Fe(III)','Fe(III)','Fe(II)','Fe(I)','Fe(I)','Fe(O)'],['S2','S4','S3','S2','S4','S3'])

### 4) Charge and spin 

charge_spin = (['1 2','1 4','0 3','-1 2','-1 4','-2 3'])

### 5) Coordinates multiplicative factor 

mult_factor = 6

### 6) Defines final instructions block

final_block = ''

