#!/bin/bash -l
#$ -N $job_name
#$ -l mem=2G
#$ -pe mpi $ncores
#$ -cwd
#$ -o stdout.out
#$ -e stderr.error
#$ -A $project_code
#$ -l h_rt=$hours:00:00
#$ -ac allow=$node_type
#$ -P $queue_type

ulimit -s unlimited
ulimit -m unlimited

module load gcc-libs/4.9.2
module load compilers/intel/2018/update3
module load mpi/intel/2018/update3/intel

gerun $vasp_bin > vasp_out