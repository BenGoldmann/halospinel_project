#!/bin/bash -l
#$ -N LSC3005
#$ -l mem=2G
#$ -pe mpi 96
#$ -cwd
#$ -o stdout.out
#$ -e stderr.error
#$ -A FARADAY_MSM_bjm
#$ -l h_rt=24:00:00
#$ -ac allow=K
#$ -P Gold

ulimit -s unlimited
ulimit -m unlimited

module load gcc-libs/4.9.2
module load compilers/intel/2018/update3
module load mpi/intel/2018/update3/intel

gerun /path/to/your/binary/vasp_std > vasp_out