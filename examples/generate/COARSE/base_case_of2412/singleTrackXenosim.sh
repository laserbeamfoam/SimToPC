#!/bin/bash
# All the information about queues can be obtained using 'sinfo'

# Slurm flags
#SBATCH --job-name=Coarse_mesh_Single_Track
# Mail me on job start & end
#SBATCH --mail-user=simon.rodriguezluzardo@ucd.ie
#SBATCH --time=100:00:00
#SBATCH --account=p200734
#SBATCH --partition=long
#SBATCH --cpus-per-task=1       
#SBATCH --ntasks=80     
#SBATCH --output=log_%x_%j.out 
#SBATCH --error=log_%x_%j.err  

# Good practice to navigate to the submission directory                                                                                                                                                                                                                           
cd $SLURM_SUBMIT_DIR

# load OpenFOAM
source /usr/lib/openfoam/openfoam2412/etc/bashrc

cp -r initial 0
blockMesh > blockMesh_output.txt 2>&1
setSolidFraction > setSolidFraction.txt 2>&1
decomposePar > decomposePar.txt 2>&1

# # Run simulation in parallel
mpirun -np 80 laserMeltFoam -parallel > laserMeltFoam_output.txt 2>&1

# Reconstruct the files
reconstructPar > reconstructPar.txt 2>&1

rm -r processor*
touch finished.txt
