
#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -m n
#$ -N mon
#$ -V
#$ -o _scheduler-stdout.txt
#$ -e _scheduler-stderr.txt
#$ -P Gold
#$ -A Faraday_CATMAT
#$ -pe mpi 80
#$ -l mem=314572K
#$ -l h_rt=6:00:00
#$ -ac allow=A

module load lammps/7Aug19/userintel/intel-2018

'gerun' '/shared/ucl/apps/lammps/7Aug2019/USERINTEL/intel-2018/lammps/bin/lmp_default' '-in' 'monoclinic_3x3x3_300k.inp'
