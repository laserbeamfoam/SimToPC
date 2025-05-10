#!/bin/bash -l
#SBATCH -N 1
#SBATCH --ntasks=80
#SBATCH --cpus-per-task=1
#SBATCH -p cpu
#SBATCH -q default
#SBATCH --time 48:00:00
#SBATCH --account=p200734
#SBATCH --job-name=Test1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=simon.rodriguezluzardo@ucd.ie


#Load OpenMPI module
module load OpenMPI

source ~/foam/foam-extend-4.0/etc/bashrc

# decomposePar

#LaserMeltFoam execution
mpirun -n 80 laserMeltFoam -parallel

reconstructPar

rm -r proc*

touch finished.txt