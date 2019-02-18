#!/bin/bash
#SBATCH --account=test
#SBATCH --partition=test
#SBATCH --job-name=test
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --exclusive
#SBATCH --err=std.err
#SBATCH --output=std.out
#----------------------------------------------------------#
module load gaussian09/d.01/
#----------------------------------------------------------#
srun --ntasks=1 --hint=nomultithread --cpus-per-task=32 --mem_bind=v,local ${GAUSSIAN09_HOME}/g09 < test.com > test.log


