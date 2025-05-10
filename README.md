# simulationDriver

`simulationDriver` is a Python-based driver framework for setting up, executing, and post-processing laser-material interaction simulations using the [`laserbeamFoam`](https://github.com/laserbeamfoam/laserbeamFoam) suite. This tool is tailored for researchers and engineers working in laser-based additive manufacturing, allowing for rapid configuration and analysis of laser energy deposition in metallic substrates.

## Features

- Modular script architecture for full simulation workflows
- Customizable input parameters via structured Python files and `.txt` configurations
- Built-in post-processing for thermal and melt pool data extraction
- Example base case setup for use with OpenFOAM solvers


## Requirements

- Python 3.6+
- OpenFOAM (tested with versions compatible with `laserbeamFoam` suite)
- NumPy, matplotlib, and other scientific computing libraries

### Who do I talk to? ###

    Simon Rodriguez
    simon.rodriguezluzardo@ucdconnect.ie
    https://www.linkedin.com/in/simonrodriguezl/
    
    Petar Cosic
    petar.cosic@ucdconnect.ie 
    
    Thomas Flint
    tom.flint@manchester.ac.uk
    https://www.linkedin.com/in/tom-flint-87ba9748/
    
    Philip Cardiff
    philip.cardiff@ucd.ie
    https://www.linkedin.com/in/philipcardiff/

### References

Flint, T. F., Robson, J. D., Parivendhan, G., & Cardiff, P. (2023). laserbeamFoam: Laser ray-tracing and thermally induced state transition simulation toolkit. SoftwareX, 21, 101299.

Flint, T. F., Parivendhan, G., Ivankovic, A., Smith, M. C., & Cardiff, P. (2022). beamWeldFoam: Numerical simulation of high energy density fusion and vapourisation-inducing processes. SoftwareX, 18, 101065.

Flint, T. F., et al. A fundamental analysis of factors affecting chemical homogeneity in the laser powder bed fusion process. International Journal of Heat and Mass Transfer 194 (2022): 122985.

Flint, T. F., T. Dutilleul, and W. Kyffin. A fundamental investigation into the role of beam focal point, and beam divergence, on thermo-capillary stability and evolution in electron beam welding applications. International Journal of Heat and Mass Transfer 212 (2023): 124262.

Parivendhan, G., Cardiff, P., Flint, T., Tuković, Ž., Obeidi, M., Brabazon, D., Ivanković, A. (2023) A numerical study of processing parameters and their effect on the melt-track profile in Laser Powder Bed Fusion processes, Additive Manufacturing, 67, 10.1016/j.addma.2023.103482.

### Disclaimer

This offering is not approved or endorsed by OpenCFD Limited, producer and distributor of the OpenFOAM software via www.openfoam.com, and owner of the OPENFOAM® and OpenCFD® trade marks.

### Acknowledgement

OPENFOAM® is a registered trademark of OpenCFD Limited, producer and distributor of the OpenFOAM software via www.openfoam.com.
