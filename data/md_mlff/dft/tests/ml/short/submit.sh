#!/bin/bash -l
#$ -N ml_600
#$ -l mem=2G
#$ -pe mpi 120
#$ -cwd
#$ -o stdout.out
#$ -e stderr.error
#$ -A Faraday_CATMAT
#$ -l h_rt=48:00:00
#$ -ac allow=K
#$ -P Gold

ulimit -s unlimited
ulimit -m unlimited

vasp_gam=/home/mmm0863/bin/vasp-6.3.0/vasp_gam

module unload compilers
module unload mpi

module load compilers/intel/2019/update5
module load mpi/intel/2019/update5/intel

gerun $vasp_gam > vasp_out
