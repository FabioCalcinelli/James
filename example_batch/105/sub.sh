#!/bin/bash
#SBATCH --account=k1212
#SBATCH --partition=workq
#SBATCH --job-name=105
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --exclusive
#SBATCH --err=std.err
#SBATCH --output=std.out
#----------------------------------------------------------#
module load gaussian09/d.01/
ulimit -c 0
ulimit -d hard
ulimit -f hard
ulimit -l hard
ulimit -m hard
ulimit -n hard
ulimit -s hard
ulimit -t hard
ulimit -u hard
export CRAY_ROOTFS=DSL
export GAUSS_SCRDIR=`pwd`
#----------------------------------------------------------#
echo "The job "${SLURM_JOB_ID}" is running on "${SLURM_JOB_NODELIST}
#----------------------------------------------------------#
srun --ntasks=1 --hint=nomultithread --cpus-per-task=32 --mem_bind=v,local ${GAUSSIAN09_HOME}/g09 < 105.com > 105.log

