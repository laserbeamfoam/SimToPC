import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#  Input parameters

domain_size = (200, 800, 200)  # Size of the domain  domain_size = (X, Y, Z) [ micrometers ]
number_of_cells_x = 50  #  Number of cells in the x direciton, the number of cells in y and z direction will be calculated so the cells are perfect squares 

#  The total number of processors that will be used to parallelize the domain
total_num_of_processors = 16 

#  The number of divisios the domain will be split in the x direction, the number of divisions in the y direciton will be calculated 
#     based on the number of total processors and the processor_divisions_in_x, z will always be 1. These numbers might change if the cell count per processor is not int.
processor_divisions_in_x = 8

#  Settings the flags
PLOT_FLAG = 0  #  plot the mesh:  1 - YES  /  0 - NO    // This might take a while to plot depending on the number of cells
BLOCK_MESH_DICT_FLAG = 1  #  create the blockMeshDict file:  1 - YES  /  0 - NO
DECOMPOSE_PAR_DICT_FLAG = 1  #  create the decomposeParDict file:  1 - YES  /  0 - NO


#                                                                          *------------------------*
#                                                                       *  |                      * |
#                                                                   *      |                  *     |
#                                                              *           |              *         |
#                                                          *               |          *             |
#                                                     *                    |      *                 |      Z 
#                                                   *-------------------------*                     |        
#                                                   |                      |  |                     |
#                                                   |                      |  |                     |
#                                                   |                      *------------------------*
#                                                   |                  *      |                  *
#                                                   |              *          |              *      
#                                                   |          *              |          *        
#                                                   |      *                  |       *           Y 
#                                                   |  *    num of cells x    |   *     
#                                                   *---|---|--|---|---|---|--*              
#                                                                   
#                                                                   X

#  ------------------------------------------------------- Calculating ---------------------------------------------------------------------

num_cells = (number_of_cells_x, int(domain_size[1]/domain_size[0]*number_of_cells_x) , int(domain_size[2]/domain_size[0]*number_of_cells_x)) 

# Creating blockMeshDict ------------------------------------------------------------------------------------------------------

if BLOCK_MESH_DICT_FLAG: 

  blockMeshDict_content = f"""
/*--------------------------------*- C++ -*----------------------------------* \\
| =========                 |                                                 |
| \\      /  F ield         | foam-extend: Open Source CFD                    |
|  \\    /   O peration     | Version:     4.0                                |
|   \\  /    A nd           | Web:         http://www.foam-extend.org         |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1.0;

vertices
(
    (0    0    0)         //0
    ({domain_size[0]}e-6    0    0)        //1
    ({domain_size[0]}e-6    {domain_size[1]}e-6    0)        //2
    (0    {domain_size[1]}e-6    0)        //3
    (0    0    {domain_size[2]}e-6)        //4
    ({domain_size[0]}e-6    0    {domain_size[2]}e-6)        //5
    ({domain_size[0]}e-6 {domain_size[1]}e-6    {domain_size[2]}e-6)        //6
    (0    {domain_size[1]}e-6    {domain_size[2]}e-6)        //7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({num_cells[0]} {num_cells[1]} {num_cells[2]}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    back
    {{
        type wall;
        faces
        (
            (0 4 7 3)
        );
    }}
    front
    {{
        type wall;
        faces
        (
            (1 2 6 5)
        );
    }}
    leftWall
    {{
        type wall;
        faces
        (
            (1 5 4 0)
        );
    }}
    rightWall
    {{
        type patch;
        faces
        (
            (3 7 6 2)
        );
    }}
    topWall
    {{   
        type patch;
        faces
        (
            (4 5 6 7)
        );
    }}
    bottomWall
    {{
        type patch;
        faces
        (
            (0 3 2 1)
        );
    }}
    solidInterface
    {{  
        type patch;
        faces
        ();
    }}
);

mergePatchPairs
(
);


// ************************************************************************* //
"""

  # Write the content to a file
  with open('blockMeshDict', 'w') as file:
      file.write(blockMeshDict_content)


# Creating decomposeParDict ------------------------------------------------------------------------------------------------------

if DECOMPOSE_PAR_DICT_FLAG: 

  processor_divisions_in_z = 1
  cells_per_processor_z = int(num_cells[2])
  cells_per_processor_x = num_cells[0]/processor_divisions_in_x

  while(cells_per_processor_x != int(cells_per_processor_x)):
    processor_divisions_in_x = processor_divisions_in_x - 1
    cells_per_processor_x = num_cells[0]/processor_divisions_in_x

  cells_per_processor_x = int(cells_per_processor_x)

  processor_divisions_in_y = int(total_num_of_processors / processor_divisions_in_x)
  cells_per_processor_y = num_cells[1] / processor_divisions_in_y
 
  while(cells_per_processor_y != int(cells_per_processor_y)):
    processor_divisions_in_y = processor_divisions_in_y - 1
    cells_per_processor_y = num_cells[1]/processor_divisions_in_y

  cells_per_processor_y = int(cells_per_processor_y)
  new_total_num_of_processors = processor_divisions_in_y*processor_divisions_in_x
  total_cells_per_processor = cells_per_processor_x*cells_per_processor_y*cells_per_processor_z

  print("----------------- Info -----------------")

  if new_total_num_of_processors!=total_num_of_processors:
    print(f"New total number of processors: {new_total_num_of_processors}")
  else:
    print(f"Total number of processors: {total_num_of_processors}")
  print(f"Divisions in x: {processor_divisions_in_x}")
  print(f"Divisions in y: {processor_divisions_in_y}")
  print(f"Divisions in z: {processor_divisions_in_z}")
  print(f"Number of cells per processor in x direction: {cells_per_processor_x}")
  print(f"Number of cells per processor in y direction: {cells_per_processor_y}")
  print(f"Number of cells per processor in z direction: {cells_per_processor_z}")
  print(f"Total number of cells per processor: {total_cells_per_processor}")
  cell_size = round(domain_size[0]/num_cells[0],3)
  print(f"Size of the cell {cell_size} µm")

  print(f"""
                                                                     +------------------------*
                                                                   * |                     *  |
                                                                *    |                   *    |
                                                              *      |                 *      |
                                                           *         |               *        |
                                                        *            |             *          |
                                                      +-------------------------*             |
                                                      |              |          |             |    {cell_size} µm
                                                      |              |          |             |
                                                      |              |          |             |
                                                      |              |          |             |
                                                      |              |          |             |
                                                      |              *----------|-------------*
                                                      |           *             |          *    
                                                      |        *                |       *       
                                                      |     *                   |     *      {cell_size} µm    
                                                      |  *                      |  *            
                                                      +---|---|--|---|---|---|--*              
                                                                    
                                                                    {cell_size} µm

  """)



  decomposeParDict_content = f"""
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | foam-extend: Open Source CFD                    |
|  \\    /   O peration     | Version:     4.0                                |
|   \\  /    A nd           | Web:         http://www.foam-extend.org         |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains {new_total_num_of_processors};

method          simple;

simpleCoeffs
{{
    n               ( {processor_divisions_in_x} {processor_divisions_in_y} {processor_divisions_in_z} );
    delta           0.001;
}}

hierarchicalCoeffs
{{
    n               ( 1 1 1 );
    delta           0.001;
    order           xyz;
}}

metisCoeffs
{{
    //processorWeights ( 1 1 1 1 );
}}

manualCoeffs
{{
    dataFile        "";
}}

distributed     no;

roots           ( );


// ************************************************************************* //
"""

  # Write the content to a file
  with open('decomposeParDict', 'w') as file:
      file.write(decomposeParDict_content)



# Drawing ----------------------------------------------------------------------------------------------------------------------------------

if PLOT_FLAG: 

  # Functions --------------------------------------------------------------------------------------------------------------------------------
  def generate_3d_mesh(domain_size, num_cells):
    """
    Generates a 3D mesh for a given domain size and number of cells along each axis.

    Parameters:
    domain_size (tuple): A tuple (x_size, y_size, z_size) for the size of the domain.
    num_cells (tuple): A tuple (nx, ny, nz) for the number of cells along each axis.

    Returns:
    mesh (tuple): A tuple (x, y, z) where x, y, z are arrays representing the mesh grid.
    """
    x_size, y_size, z_size = domain_size
    nx, ny, nz = num_cells

    # Generate coordinate points for each axis
    x = np.linspace(0, x_size, nx + 1)  # nx+1 because we need the cell faces, not just the cell centers
    y = np.linspace(0, y_size, ny + 1)
    z = np.linspace(0, z_size, nz + 1)

    # Create mesh grid for 3D coordinates
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    return X, Y, Z


  def modifyAxis(ax):
    ax.set(facecolor = "white")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('w')
    ax.yaxis.pane.set_edgecolor('w')
    ax.zaxis.pane.set_edgecolor('w')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal')
    ax.set_xlim([0, domain_size[0]])
    ax.set_ylim([0, domain_size[1]])
    ax.set_zlim([0, domain_size[2]])
    ax.grid(0)


  X, Y, Z = generate_3d_mesh(domain_size, num_cells)

  # Create a figure with 4 subplots to visualize all grids
  fig = plt.figure(figsize=(16, 12))

  # Subplot 1: Boundary 3D Surface
  ax1 = fig.add_subplot(221, projection='3d')
  for i in range(X.shape[0]):
    for j in range(Y.shape[1]):
      for k in range(Z.shape[2]):
        if i == 0 or i == X.shape[0] - 1 or j == 0 or j == Y.shape[1] - 1 or k == 0 or k == Z.shape[2] - 1:
          if i + 1 < X.shape[0]:
            if j == 0 or k == 0 or k == Z.shape[2]-1 or j == Y.shape[1]-1:
              ax1.plot([X[i, j, k], X[i+1, j, k]], [Y[i, j, k], Y[i+1, j, k]], [Z[i, j, k], Z[i+1, j, k]], color=[0.5,0.5,0.5])
          if j + 1 < Y.shape[1]:
            if k == 0 or i == 0 or k == Z.shape[2]-1 or i == X.shape[0] - 1:
              ax1.plot([X[i, j, k], X[i, j+1, k]], [Y[i, j, k], Y[i, j+1, k]], [Z[i, j, k], Z[i, j+1, k]], color=[0.5,0.5,0.5])
          if k + 1 < Z.shape[2]:
            if j == 0 or i == 0 or i == X.shape[0] - 1 or j == Y.shape[1]-1:
              ax1.plot([X[i, j, k], X[i, j, k+1]], [Y[i, j, k], Y[i, j, k+1]], [Z[i, j, k], Z[i, j, k+1]], color=[0.5,0.5,0.5])
  ax1.set_title('3D Mesh Surface')
  modifyAxis(ax1)

  # Subplot 2: XY Plane at Z=0
  ax2 = fig.add_subplot(222, projection='3d')
  for i in range(X.shape[0]):
    for j in range(Y.shape[1]):
      k = 0
      if i + 1 < X.shape[0]:
        ax2.plot([X[i, j, k], X[i+1, j, k]], [Y[i, j, k], Y[i+1, j, k]], [Z[i, j, k], Z[i+1, j, k]], color=[0.5,0.5,0.5])
      if j + 1 < Y.shape[1]:
        ax2.plot([X[i, j, k], X[i, j+1, k]], [Y[i, j, k], Y[i, j+1, k]], [Z[i, j, k], Z[i, j+1, k]], color=[0.5,0.5,0.5])
  ax2.set_title('XY Plane at Z=0')
  modifyAxis(ax2)


  # Subplot 3: XZ Plane at Y=0
  ax3 = fig.add_subplot(223, projection='3d')
  for i in range(X.shape[0]):
    for k in range(Z.shape[2]):
      j = 0
      if i + 1 < X.shape[0]:
        ax3.plot([X[i, j, k], X[i+1, j, k]], [Y[i, j, k], Y[i+1, j, k]], [Z[i, j, k], Z[i+1, j, k]], color=[0.5,0.5,0.5])
      if k + 1 < Z.shape[2]:
        ax3.plot([X[i, j, k], X[i, j, k+1]], [Y[i, j, k], Y[i, j, k+1]], [Z[i, j, k], Z[i, j, k+1]], color=[0.5,0.5,0.5])
  ax3.set_title('XZ Plane at Y=0')
  modifyAxis(ax3)

  # Subplot 4: YZ Plane at X=0
  ax4 = fig.add_subplot(224, projection='3d')
  for j in range(Y.shape[1]):
    for k in range(Z.shape[2]):
      i = 0
      if j + 1 < Y.shape[1]:
        ax4.plot([X[i, j, k], X[i, j+1, k]], [Y[i, j, k], Y[i, j+1, k]], [Z[i, j, k], Z[i, j+1, k]], color=[0.5,0.5,0.5])
      if k + 1 < Z.shape[2]:
        ax4.plot([X[i, j, k], X[i, j, k+1]], [Y[i, j, k], Y[i, j, k+1]], [Z[i, j, k], Z[i, j, k+1]], color=[0.5,0.5,0.5])
  ax4.set_title('YZ Plane at X=0')
  modifyAxis(ax4)

  # Show the combined plot
  # plt.tight_layout()
  plt.show()

