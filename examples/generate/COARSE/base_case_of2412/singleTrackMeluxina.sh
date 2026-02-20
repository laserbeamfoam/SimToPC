#!/bin/bash
# All the information about queues can be obtained using 'sinfo'

# Slurm flags
#SBATCH -N 2
#SBATCH --job-name=test80cores_portedcode
# Mail me on job start & end
#SBATCH --mail-user=simon.rodriguezluzardo@ucd.ie
#SBATCH --time=00:15:00
#SBATCH --account=p200734
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --cpus-per-task=1       
#SBATCH --ntasks-per-node=40     

source /etc/profile

# Cargar el mismo entorno funcional que en sesión interactiva
module load env/release/2024.1
module load NVHPC/25.1-CUDA-12.6.0
module load OpenMPI/5.0.7-NVHPC-25.1-CUDA-12.6.0


# Source OpenFOAM
source /project/home/p200734/OpenFOAM-v2412/etc/bashrc

cp -r initial 0
blockMesh 
setSolidFraction 
decomposePar 

# # Run simulation in parallel
mpirun -np 80 laserMeltFoam -parallel

# Reconstruct the files
reconstructPar

rm -r processor*
touch finished.txt
