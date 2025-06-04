'''
License
  This program is free software: you can redistribute it and/or modify 
  it under the terms of the GNU General Public License as published 
  by the Free Software Foundation, either version 3 of the License, 
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful, 
  but WITHOUT ANY WARRANTY; without even the implied warranty of 
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 

  See the GNU General Public License for more details. You should have 
  received a copy of the GNU General Public License along with this 
  program. If not, see <https://www.gnu.org/licenses/>. 

Description
  Script for exporting the meltpool in the laserMeltFoam L-PBF tutorial.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester. All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved
'''


# trace generated using paraview version 5.6.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active source.
mainfoam = OpenFOAMReader(FileName='main.foam')

# Properties modified on mainfoam
mainfoam.MeshRegions = ['back', 'bottomWall', 'front', 'internalMesh', 'leftWall', 'rightWall', 'solidInterface', 'topWall']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1674, 878]

# show data in view
mainfoamDisplay = Show(mainfoam, renderView1)

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')
pLUT.AutomaticRescaleRangeMode = "Grow and update on 'Apply'"
pLUT.InterpretValuesAsCategories = 0
pLUT.AnnotationsInitialized = 0
pLUT.ShowCategoricalColorsinDataRangeOnly = 0
pLUT.RescaleOnVisibilityChange = 0
pLUT.EnableOpacityMapping = 0
pLUT.RGBPoints = [-57219.23828125, 0.231373, 0.298039, 0.752941, 544275.380859375, 0.865003, 0.865003, 0.865003, 1145770.0, 0.705882, 0.0156863, 0.14902]
pLUT.UseLogScale = 0
pLUT.ColorSpace = 'Diverging'
pLUT.UseBelowRangeColor = 0
pLUT.BelowRangeColor = [0.0, 0.0, 0.0]
pLUT.UseAboveRangeColor = 0
pLUT.AboveRangeColor = [0.5, 0.5, 0.5]
pLUT.NanColor = [1.0, 1.0, 0.0]
pLUT.NanOpacity = 1.0
pLUT.Discretize = 1
pLUT.NumberOfTableValues = 256
pLUT.ScalarRangeInitialized = 1.0
pLUT.HSVWrap = 0
pLUT.VectorComponent = 0
pLUT.VectorMode = 'Magnitude'
pLUT.AllowDuplicateScalars = 1
pLUT.Annotations = []
pLUT.ActiveAnnotatedValues = []
pLUT.IndexedColors = []
pLUT.IndexedOpacities = []

# trace defaults for the display properties.
mainfoamDisplay.Representation = 'Surface'
mainfoamDisplay.AmbientColor = [1.0, 1.0, 1.0]
mainfoamDisplay.ColorArrayName = ['POINTS', 'p']
mainfoamDisplay.DiffuseColor = [1.0, 1.0, 1.0]
mainfoamDisplay.LookupTable = pLUT
mainfoamDisplay.MapScalars = 1
mainfoamDisplay.MultiComponentsMapping = 0
mainfoamDisplay.InterpolateScalarsBeforeMapping = 1
mainfoamDisplay.Opacity = 1.0
mainfoamDisplay.PointSize = 2.0
mainfoamDisplay.LineWidth = 1.0
mainfoamDisplay.RenderLinesAsTubes = 0
mainfoamDisplay.RenderPointsAsSpheres = 0
mainfoamDisplay.Interpolation = 'Gouraud'
mainfoamDisplay.Specular = 0.0
mainfoamDisplay.SpecularColor = [1.0, 1.0, 1.0]
mainfoamDisplay.SpecularPower = 100.0
mainfoamDisplay.Luminosity = 0.0
mainfoamDisplay.Ambient = 0.0
mainfoamDisplay.Diffuse = 1.0
mainfoamDisplay.EdgeColor = [0.0, 0.0, 0.5]
mainfoamDisplay.BackfaceRepresentation = 'Follow Frontface'
mainfoamDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
mainfoamDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
mainfoamDisplay.BackfaceOpacity = 1.0
mainfoamDisplay.Position = [0.0, 0.0, 0.0]
mainfoamDisplay.Scale = [1.0, 1.0, 1.0]
mainfoamDisplay.Orientation = [0.0, 0.0, 0.0]
mainfoamDisplay.Origin = [0.0, 0.0, 0.0]
mainfoamDisplay.Pickable = 1
mainfoamDisplay.Texture = None
mainfoamDisplay.Triangulate = 0
mainfoamDisplay.UseShaderReplacements = 0
mainfoamDisplay.ShaderReplacements = ''
mainfoamDisplay.NonlinearSubdivisionLevel = 1
mainfoamDisplay.UseDataPartitions = 0
mainfoamDisplay.OSPRayUseScaleArray = 0
mainfoamDisplay.OSPRayScaleArray = 'p'
mainfoamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mainfoamDisplay.OSPRayMaterial = 'None'
mainfoamDisplay.Orient = 0
mainfoamDisplay.OrientationMode = 'Direction'
mainfoamDisplay.SelectOrientationVectors = 'U'
mainfoamDisplay.Scaling = 0
mainfoamDisplay.ScaleMode = 'No Data Scaling Off'
mainfoamDisplay.ScaleFactor = 7.999999797903001e-05
mainfoamDisplay.SelectScaleArray = 'p'
mainfoamDisplay.GlyphType = 'Arrow'
mainfoamDisplay.UseGlyphTable = 0
mainfoamDisplay.GlyphTableIndexArray = 'p'
mainfoamDisplay.UseCompositeGlyphTable = 0
mainfoamDisplay.UseGlyphCullingAndLOD = 0
mainfoamDisplay.LODValues = []
mainfoamDisplay.ColorByLODIndex = 0
mainfoamDisplay.GaussianRadius = 3.999999898951501e-06
mainfoamDisplay.ShaderPreset = 'Sphere'
mainfoamDisplay.CustomTriangleScale = 3
mainfoamDisplay.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
mainfoamDisplay.Emissive = 0
mainfoamDisplay.ScaleByArray = 0
mainfoamDisplay.SetScaleArray = ['POINTS', 'p']
mainfoamDisplay.ScaleArrayComponent = ''
mainfoamDisplay.UseScaleFunction = 1
mainfoamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mainfoamDisplay.OpacityByArray = 0
mainfoamDisplay.OpacityArray = ['POINTS', 'p']
mainfoamDisplay.OpacityArrayComponent = ''
mainfoamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mainfoamDisplay.DataAxesGrid = 'GridAxesRepresentation'
mainfoamDisplay.SelectionCellLabelBold = 0
mainfoamDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
mainfoamDisplay.SelectionCellLabelFontFamily = 'Arial'
mainfoamDisplay.SelectionCellLabelFontFile = ''
mainfoamDisplay.SelectionCellLabelFontSize = 18
mainfoamDisplay.SelectionCellLabelItalic = 0
mainfoamDisplay.SelectionCellLabelJustification = 'Left'
mainfoamDisplay.SelectionCellLabelOpacity = 1.0
mainfoamDisplay.SelectionCellLabelShadow = 0
mainfoamDisplay.SelectionPointLabelBold = 0
mainfoamDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
mainfoamDisplay.SelectionPointLabelFontFamily = 'Arial'
mainfoamDisplay.SelectionPointLabelFontFile = ''
mainfoamDisplay.SelectionPointLabelFontSize = 18
mainfoamDisplay.SelectionPointLabelItalic = 0
mainfoamDisplay.SelectionPointLabelJustification = 'Left'
mainfoamDisplay.SelectionPointLabelOpacity = 1.0
mainfoamDisplay.SelectionPointLabelShadow = 0
mainfoamDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
mainfoamDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
mainfoamDisplay.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
mainfoamDisplay.GlyphType.TipResolution = 6
mainfoamDisplay.GlyphType.TipRadius = 0.1
mainfoamDisplay.GlyphType.TipLength = 0.35
mainfoamDisplay.GlyphType.ShaftResolution = 6
mainfoamDisplay.GlyphType.ShaftRadius = 0.03
mainfoamDisplay.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
mainfoamDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
mainfoamDisplay.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
mainfoamDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
mainfoamDisplay.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
mainfoamDisplay.DataAxesGrid.XTitle = 'X Axis'
mainfoamDisplay.DataAxesGrid.YTitle = 'Y Axis'
mainfoamDisplay.DataAxesGrid.ZTitle = 'Z Axis'
mainfoamDisplay.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.XTitleFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.XTitleFontFile = ''
mainfoamDisplay.DataAxesGrid.XTitleBold = 0
mainfoamDisplay.DataAxesGrid.XTitleItalic = 0
mainfoamDisplay.DataAxesGrid.XTitleFontSize = 12
mainfoamDisplay.DataAxesGrid.XTitleShadow = 0
mainfoamDisplay.DataAxesGrid.XTitleOpacity = 1.0
mainfoamDisplay.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.YTitleFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.YTitleFontFile = ''
mainfoamDisplay.DataAxesGrid.YTitleBold = 0
mainfoamDisplay.DataAxesGrid.YTitleItalic = 0
mainfoamDisplay.DataAxesGrid.YTitleFontSize = 12
mainfoamDisplay.DataAxesGrid.YTitleShadow = 0
mainfoamDisplay.DataAxesGrid.YTitleOpacity = 1.0
mainfoamDisplay.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.ZTitleFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.ZTitleFontFile = ''
mainfoamDisplay.DataAxesGrid.ZTitleBold = 0
mainfoamDisplay.DataAxesGrid.ZTitleItalic = 0
mainfoamDisplay.DataAxesGrid.ZTitleFontSize = 12
mainfoamDisplay.DataAxesGrid.ZTitleShadow = 0
mainfoamDisplay.DataAxesGrid.ZTitleOpacity = 1.0
mainfoamDisplay.DataAxesGrid.FacesToRender = 63
mainfoamDisplay.DataAxesGrid.CullBackface = 0
mainfoamDisplay.DataAxesGrid.CullFrontface = 1
mainfoamDisplay.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
mainfoamDisplay.DataAxesGrid.ShowGrid = 0
mainfoamDisplay.DataAxesGrid.ShowEdges = 1
mainfoamDisplay.DataAxesGrid.ShowTicks = 1
mainfoamDisplay.DataAxesGrid.LabelUniqueEdgesOnly = 1
mainfoamDisplay.DataAxesGrid.AxesToLabel = 63
mainfoamDisplay.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.XLabelFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.XLabelFontFile = ''
mainfoamDisplay.DataAxesGrid.XLabelBold = 0
mainfoamDisplay.DataAxesGrid.XLabelItalic = 0
mainfoamDisplay.DataAxesGrid.XLabelFontSize = 12
mainfoamDisplay.DataAxesGrid.XLabelShadow = 0
mainfoamDisplay.DataAxesGrid.XLabelOpacity = 1.0
mainfoamDisplay.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.YLabelFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.YLabelFontFile = ''
mainfoamDisplay.DataAxesGrid.YLabelBold = 0
mainfoamDisplay.DataAxesGrid.YLabelItalic = 0
mainfoamDisplay.DataAxesGrid.YLabelFontSize = 12
mainfoamDisplay.DataAxesGrid.YLabelShadow = 0
mainfoamDisplay.DataAxesGrid.YLabelOpacity = 1.0
mainfoamDisplay.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
mainfoamDisplay.DataAxesGrid.ZLabelFontFamily = 'Arial'
mainfoamDisplay.DataAxesGrid.ZLabelFontFile = ''
mainfoamDisplay.DataAxesGrid.ZLabelBold = 0
mainfoamDisplay.DataAxesGrid.ZLabelItalic = 0
mainfoamDisplay.DataAxesGrid.ZLabelFontSize = 12
mainfoamDisplay.DataAxesGrid.ZLabelShadow = 0
mainfoamDisplay.DataAxesGrid.ZLabelOpacity = 1.0
mainfoamDisplay.DataAxesGrid.XAxisNotation = 'Mixed'
mainfoamDisplay.DataAxesGrid.XAxisPrecision = 2
mainfoamDisplay.DataAxesGrid.XAxisUseCustomLabels = 0
mainfoamDisplay.DataAxesGrid.XAxisLabels = []
mainfoamDisplay.DataAxesGrid.YAxisNotation = 'Mixed'
mainfoamDisplay.DataAxesGrid.YAxisPrecision = 2
mainfoamDisplay.DataAxesGrid.YAxisUseCustomLabels = 0
mainfoamDisplay.DataAxesGrid.YAxisLabels = []
mainfoamDisplay.DataAxesGrid.ZAxisNotation = 'Mixed'
mainfoamDisplay.DataAxesGrid.ZAxisPrecision = 2
mainfoamDisplay.DataAxesGrid.ZAxisUseCustomLabels = 0
mainfoamDisplay.DataAxesGrid.ZAxisLabels = []

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
mainfoamDisplay.PolarAxes.Visibility = 0
mainfoamDisplay.PolarAxes.Translation = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.Scale = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.Orientation = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.EnableCustomBounds = [0, 0, 0]
mainfoamDisplay.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
mainfoamDisplay.PolarAxes.EnableCustomRange = 0
mainfoamDisplay.PolarAxes.CustomRange = [0.0, 1.0]
mainfoamDisplay.PolarAxes.PolarAxisVisibility = 1
mainfoamDisplay.PolarAxes.RadialAxesVisibility = 1
mainfoamDisplay.PolarAxes.DrawRadialGridlines = 1
mainfoamDisplay.PolarAxes.PolarArcsVisibility = 1
mainfoamDisplay.PolarAxes.DrawPolarArcsGridlines = 1
mainfoamDisplay.PolarAxes.NumberOfRadialAxes = 0
mainfoamDisplay.PolarAxes.AutoSubdividePolarAxis = 1
mainfoamDisplay.PolarAxes.NumberOfPolarAxis = 0
mainfoamDisplay.PolarAxes.MinimumRadius = 0.0
mainfoamDisplay.PolarAxes.MinimumAngle = 0.0
mainfoamDisplay.PolarAxes.MaximumAngle = 90.0
mainfoamDisplay.PolarAxes.RadialAxesOriginToPolarAxis = 1
mainfoamDisplay.PolarAxes.Ratio = 1.0
mainfoamDisplay.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
mainfoamDisplay.PolarAxes.PolarAxisTitleVisibility = 1
mainfoamDisplay.PolarAxes.PolarAxisTitle = 'Radial Distance'
mainfoamDisplay.PolarAxes.PolarAxisTitleLocation = 'Bottom'
mainfoamDisplay.PolarAxes.PolarLabelVisibility = 1
mainfoamDisplay.PolarAxes.PolarLabelFormat = '%-#6.3g'
mainfoamDisplay.PolarAxes.PolarLabelExponentLocation = 'Labels'
mainfoamDisplay.PolarAxes.RadialLabelVisibility = 1
mainfoamDisplay.PolarAxes.RadialLabelFormat = '%-#3.1f'
mainfoamDisplay.PolarAxes.RadialLabelLocation = 'Bottom'
mainfoamDisplay.PolarAxes.RadialUnitsVisibility = 1
mainfoamDisplay.PolarAxes.ScreenSize = 10.0
mainfoamDisplay.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.PolarAxisTitleOpacity = 1.0
mainfoamDisplay.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
mainfoamDisplay.PolarAxes.PolarAxisTitleFontFile = ''
mainfoamDisplay.PolarAxes.PolarAxisTitleBold = 0
mainfoamDisplay.PolarAxes.PolarAxisTitleItalic = 0
mainfoamDisplay.PolarAxes.PolarAxisTitleShadow = 0
mainfoamDisplay.PolarAxes.PolarAxisTitleFontSize = 12
mainfoamDisplay.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.PolarAxisLabelOpacity = 1.0
mainfoamDisplay.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
mainfoamDisplay.PolarAxes.PolarAxisLabelFontFile = ''
mainfoamDisplay.PolarAxes.PolarAxisLabelBold = 0
mainfoamDisplay.PolarAxes.PolarAxisLabelItalic = 0
mainfoamDisplay.PolarAxes.PolarAxisLabelShadow = 0
mainfoamDisplay.PolarAxes.PolarAxisLabelFontSize = 12
mainfoamDisplay.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.LastRadialAxisTextOpacity = 1.0
mainfoamDisplay.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
mainfoamDisplay.PolarAxes.LastRadialAxisTextFontFile = ''
mainfoamDisplay.PolarAxes.LastRadialAxisTextBold = 0
mainfoamDisplay.PolarAxes.LastRadialAxisTextItalic = 0
mainfoamDisplay.PolarAxes.LastRadialAxisTextShadow = 0
mainfoamDisplay.PolarAxes.LastRadialAxisTextFontSize = 12
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextFontFile = ''
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextBold = 0
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextItalic = 0
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextShadow = 0
mainfoamDisplay.PolarAxes.SecondaryRadialAxesTextFontSize = 12
mainfoamDisplay.PolarAxes.EnableDistanceLOD = 1
mainfoamDisplay.PolarAxes.DistanceLODThreshold = 0.7
mainfoamDisplay.PolarAxes.EnableViewAngleLOD = 1
mainfoamDisplay.PolarAxes.ViewAngleLODThreshold = 0.7
mainfoamDisplay.PolarAxes.SmallestVisiblePolarAngle = 0.5
mainfoamDisplay.PolarAxes.PolarTicksVisibility = 1
mainfoamDisplay.PolarAxes.ArcTicksOriginToPolarAxis = 1
mainfoamDisplay.PolarAxes.TickLocation = 'Both'
mainfoamDisplay.PolarAxes.AxisTickVisibility = 1
mainfoamDisplay.PolarAxes.AxisMinorTickVisibility = 0
mainfoamDisplay.PolarAxes.ArcTickVisibility = 1
mainfoamDisplay.PolarAxes.ArcMinorTickVisibility = 0
mainfoamDisplay.PolarAxes.DeltaAngleMajor = 10.0
mainfoamDisplay.PolarAxes.DeltaAngleMinor = 5.0
mainfoamDisplay.PolarAxes.PolarAxisMajorTickSize = 0.0
mainfoamDisplay.PolarAxes.PolarAxisTickRatioSize = 0.3
mainfoamDisplay.PolarAxes.PolarAxisMajorTickThickness = 1.0
mainfoamDisplay.PolarAxes.PolarAxisTickRatioThickness = 0.5
mainfoamDisplay.PolarAxes.LastRadialAxisMajorTickSize = 0.0
mainfoamDisplay.PolarAxes.LastRadialAxisTickRatioSize = 0.3
mainfoamDisplay.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
mainfoamDisplay.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
mainfoamDisplay.PolarAxes.ArcMajorTickSize = 0.0
mainfoamDisplay.PolarAxes.ArcTickRatioSize = 0.3
mainfoamDisplay.PolarAxes.ArcMajorTickThickness = 1.0
mainfoamDisplay.PolarAxes.ArcTickRatioThickness = 0.5
mainfoamDisplay.PolarAxes.Use2DMode = 0
mainfoamDisplay.PolarAxes.UseLogAxis = 0

# reset view to fit data
renderView1.ResetCamera()

# show color bar/color legend
mainfoamDisplay.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')
pPWF.Points = [-57219.23828125, 0.0, 0.5, 0.0, 1145770.0, 1.0, 0.5, 0.0]
pPWF.AllowDuplicateScalars = 1
pPWF.UseLogScale = 0
pPWF.ScalarRangeInitialized = 1

# get animation scene
animationScene1 = GetAnimationScene()

animationScene1.GoToLast()

# create a new 'Threshold'
threshold1 = Threshold(Input=mainfoam)
threshold1.Scalars = ['POINTS', 'p']
threshold1.ThresholdRange = [-127457.984375, 1145762.5]
threshold1.AllScalars = 1
threshold1.UseContinuousCellRange = 0

# Properties modified on threshold1
threshold1.Scalars = ['POINTS', 'solidificationTime']
threshold1.ThresholdRange = [0.0, 0.0007093548774719238]

# show data in view
threshold1Display = Show(threshold1, renderView1)

# trace defaults for the display properties.
threshold1Display.Representation = 'Surface'
threshold1Display.AmbientColor = [1.0, 1.0, 1.0]
threshold1Display.ColorArrayName = ['POINTS', 'p']
threshold1Display.DiffuseColor = [1.0, 1.0, 1.0]
threshold1Display.LookupTable = pLUT
threshold1Display.MapScalars = 1
threshold1Display.MultiComponentsMapping = 0
threshold1Display.InterpolateScalarsBeforeMapping = 1
threshold1Display.Opacity = 1.0
threshold1Display.PointSize = 2.0
threshold1Display.LineWidth = 1.0
threshold1Display.RenderLinesAsTubes = 0
threshold1Display.RenderPointsAsSpheres = 0
threshold1Display.Interpolation = 'Gouraud'
threshold1Display.Specular = 0.0
threshold1Display.SpecularColor = [1.0, 1.0, 1.0]
threshold1Display.SpecularPower = 100.0
threshold1Display.Luminosity = 0.0
threshold1Display.Ambient = 0.0
threshold1Display.Diffuse = 1.0
threshold1Display.EdgeColor = [0.0, 0.0, 0.5]
threshold1Display.BackfaceRepresentation = 'Follow Frontface'
threshold1Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
threshold1Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
threshold1Display.BackfaceOpacity = 1.0
threshold1Display.Position = [0.0, 0.0, 0.0]
threshold1Display.Scale = [1.0, 1.0, 1.0]
threshold1Display.Orientation = [0.0, 0.0, 0.0]
threshold1Display.Origin = [0.0, 0.0, 0.0]
threshold1Display.Pickable = 1
threshold1Display.Texture = None
threshold1Display.Triangulate = 0
threshold1Display.UseShaderReplacements = 0
threshold1Display.ShaderReplacements = ''
threshold1Display.NonlinearSubdivisionLevel = 1
threshold1Display.UseDataPartitions = 0
threshold1Display.OSPRayUseScaleArray = 0
threshold1Display.OSPRayScaleArray = 'p'
threshold1Display.OSPRayScaleFunction = 'PiecewiseFunction'
threshold1Display.OSPRayMaterial = 'None'
threshold1Display.Orient = 0
threshold1Display.OrientationMode = 'Direction'
threshold1Display.SelectOrientationVectors = 'U'
threshold1Display.Scaling = 0
threshold1Display.ScaleMode = 'No Data Scaling Off'
threshold1Display.ScaleFactor = 6.299999949987978e-05
threshold1Display.SelectScaleArray = 'p'
threshold1Display.GlyphType = 'Arrow'
threshold1Display.UseGlyphTable = 0
threshold1Display.GlyphTableIndexArray = 'p'
threshold1Display.UseCompositeGlyphTable = 0
threshold1Display.UseGlyphCullingAndLOD = 0
threshold1Display.LODValues = []
threshold1Display.ColorByLODIndex = 0
threshold1Display.GaussianRadius = 3.149999974993989e-06
threshold1Display.ShaderPreset = 'Sphere'
threshold1Display.CustomTriangleScale = 3
threshold1Display.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
threshold1Display.Emissive = 0
threshold1Display.ScaleByArray = 0
threshold1Display.SetScaleArray = ['POINTS', 'p']
threshold1Display.ScaleArrayComponent = ''
threshold1Display.UseScaleFunction = 1
threshold1Display.ScaleTransferFunction = 'PiecewiseFunction'
threshold1Display.OpacityByArray = 0
threshold1Display.OpacityArray = ['POINTS', 'p']
threshold1Display.OpacityArrayComponent = ''
threshold1Display.OpacityTransferFunction = 'PiecewiseFunction'
threshold1Display.DataAxesGrid = 'GridAxesRepresentation'
threshold1Display.SelectionCellLabelBold = 0
threshold1Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
threshold1Display.SelectionCellLabelFontFamily = 'Arial'
threshold1Display.SelectionCellLabelFontFile = ''
threshold1Display.SelectionCellLabelFontSize = 18
threshold1Display.SelectionCellLabelItalic = 0
threshold1Display.SelectionCellLabelJustification = 'Left'
threshold1Display.SelectionCellLabelOpacity = 1.0
threshold1Display.SelectionCellLabelShadow = 0
threshold1Display.SelectionPointLabelBold = 0
threshold1Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
threshold1Display.SelectionPointLabelFontFamily = 'Arial'
threshold1Display.SelectionPointLabelFontFile = ''
threshold1Display.SelectionPointLabelFontSize = 18
threshold1Display.SelectionPointLabelItalic = 0
threshold1Display.SelectionPointLabelJustification = 'Left'
threshold1Display.SelectionPointLabelOpacity = 1.0
threshold1Display.SelectionPointLabelShadow = 0
threshold1Display.PolarAxes = 'PolarAxesRepresentation'
threshold1Display.ScalarOpacityFunction = pPWF
threshold1Display.ScalarOpacityUnitDistance = 1.5409649494920656e-05
threshold1Display.SelectMapper = 'Projected tetra'
threshold1Display.SamplingDimensions = [128, 128, 128]
threshold1Display.UseFloatingPointFrameBuffer = 1

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
threshold1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
threshold1Display.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
threshold1Display.GlyphType.TipResolution = 6
threshold1Display.GlyphType.TipRadius = 0.1
threshold1Display.GlyphType.TipLength = 0.35
threshold1Display.GlyphType.ShaftResolution = 6
threshold1Display.GlyphType.ShaftRadius = 0.03
threshold1Display.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
threshold1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
threshold1Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
threshold1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
threshold1Display.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
threshold1Display.DataAxesGrid.XTitle = 'X Axis'
threshold1Display.DataAxesGrid.YTitle = 'Y Axis'
threshold1Display.DataAxesGrid.ZTitle = 'Z Axis'
threshold1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.XTitleFontFamily = 'Arial'
threshold1Display.DataAxesGrid.XTitleFontFile = ''
threshold1Display.DataAxesGrid.XTitleBold = 0
threshold1Display.DataAxesGrid.XTitleItalic = 0
threshold1Display.DataAxesGrid.XTitleFontSize = 12
threshold1Display.DataAxesGrid.XTitleShadow = 0
threshold1Display.DataAxesGrid.XTitleOpacity = 1.0
threshold1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.YTitleFontFamily = 'Arial'
threshold1Display.DataAxesGrid.YTitleFontFile = ''
threshold1Display.DataAxesGrid.YTitleBold = 0
threshold1Display.DataAxesGrid.YTitleItalic = 0
threshold1Display.DataAxesGrid.YTitleFontSize = 12
threshold1Display.DataAxesGrid.YTitleShadow = 0
threshold1Display.DataAxesGrid.YTitleOpacity = 1.0
threshold1Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.ZTitleFontFamily = 'Arial'
threshold1Display.DataAxesGrid.ZTitleFontFile = ''
threshold1Display.DataAxesGrid.ZTitleBold = 0
threshold1Display.DataAxesGrid.ZTitleItalic = 0
threshold1Display.DataAxesGrid.ZTitleFontSize = 12
threshold1Display.DataAxesGrid.ZTitleShadow = 0
threshold1Display.DataAxesGrid.ZTitleOpacity = 1.0
threshold1Display.DataAxesGrid.FacesToRender = 63
threshold1Display.DataAxesGrid.CullBackface = 0
threshold1Display.DataAxesGrid.CullFrontface = 1
threshold1Display.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
threshold1Display.DataAxesGrid.ShowGrid = 0
threshold1Display.DataAxesGrid.ShowEdges = 1
threshold1Display.DataAxesGrid.ShowTicks = 1
threshold1Display.DataAxesGrid.LabelUniqueEdgesOnly = 1
threshold1Display.DataAxesGrid.AxesToLabel = 63
threshold1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.XLabelFontFamily = 'Arial'
threshold1Display.DataAxesGrid.XLabelFontFile = ''
threshold1Display.DataAxesGrid.XLabelBold = 0
threshold1Display.DataAxesGrid.XLabelItalic = 0
threshold1Display.DataAxesGrid.XLabelFontSize = 12
threshold1Display.DataAxesGrid.XLabelShadow = 0
threshold1Display.DataAxesGrid.XLabelOpacity = 1.0
threshold1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.YLabelFontFamily = 'Arial'
threshold1Display.DataAxesGrid.YLabelFontFile = ''
threshold1Display.DataAxesGrid.YLabelBold = 0
threshold1Display.DataAxesGrid.YLabelItalic = 0
threshold1Display.DataAxesGrid.YLabelFontSize = 12
threshold1Display.DataAxesGrid.YLabelShadow = 0
threshold1Display.DataAxesGrid.YLabelOpacity = 1.0
threshold1Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
threshold1Display.DataAxesGrid.ZLabelFontFamily = 'Arial'
threshold1Display.DataAxesGrid.ZLabelFontFile = ''
threshold1Display.DataAxesGrid.ZLabelBold = 0
threshold1Display.DataAxesGrid.ZLabelItalic = 0
threshold1Display.DataAxesGrid.ZLabelFontSize = 12
threshold1Display.DataAxesGrid.ZLabelShadow = 0
threshold1Display.DataAxesGrid.ZLabelOpacity = 1.0
threshold1Display.DataAxesGrid.XAxisNotation = 'Mixed'
threshold1Display.DataAxesGrid.XAxisPrecision = 2
threshold1Display.DataAxesGrid.XAxisUseCustomLabels = 0
threshold1Display.DataAxesGrid.XAxisLabels = []
threshold1Display.DataAxesGrid.YAxisNotation = 'Mixed'
threshold1Display.DataAxesGrid.YAxisPrecision = 2
threshold1Display.DataAxesGrid.YAxisUseCustomLabels = 0
threshold1Display.DataAxesGrid.YAxisLabels = []
threshold1Display.DataAxesGrid.ZAxisNotation = 'Mixed'
threshold1Display.DataAxesGrid.ZAxisPrecision = 2
threshold1Display.DataAxesGrid.ZAxisUseCustomLabels = 0
threshold1Display.DataAxesGrid.ZAxisLabels = []

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
threshold1Display.PolarAxes.Visibility = 0
threshold1Display.PolarAxes.Translation = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.Scale = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.EnableCustomBounds = [0, 0, 0]
threshold1Display.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
threshold1Display.PolarAxes.EnableCustomRange = 0
threshold1Display.PolarAxes.CustomRange = [0.0, 1.0]
threshold1Display.PolarAxes.PolarAxisVisibility = 1
threshold1Display.PolarAxes.RadialAxesVisibility = 1
threshold1Display.PolarAxes.DrawRadialGridlines = 1
threshold1Display.PolarAxes.PolarArcsVisibility = 1
threshold1Display.PolarAxes.DrawPolarArcsGridlines = 1
threshold1Display.PolarAxes.NumberOfRadialAxes = 0
threshold1Display.PolarAxes.AutoSubdividePolarAxis = 1
threshold1Display.PolarAxes.NumberOfPolarAxis = 0
threshold1Display.PolarAxes.MinimumRadius = 0.0
threshold1Display.PolarAxes.MinimumAngle = 0.0
threshold1Display.PolarAxes.MaximumAngle = 90.0
threshold1Display.PolarAxes.RadialAxesOriginToPolarAxis = 1
threshold1Display.PolarAxes.Ratio = 1.0
threshold1Display.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
threshold1Display.PolarAxes.PolarAxisTitleVisibility = 1
threshold1Display.PolarAxes.PolarAxisTitle = 'Radial Distance'
threshold1Display.PolarAxes.PolarAxisTitleLocation = 'Bottom'
threshold1Display.PolarAxes.PolarLabelVisibility = 1
threshold1Display.PolarAxes.PolarLabelFormat = '%-#6.3g'
threshold1Display.PolarAxes.PolarLabelExponentLocation = 'Labels'
threshold1Display.PolarAxes.RadialLabelVisibility = 1
threshold1Display.PolarAxes.RadialLabelFormat = '%-#3.1f'
threshold1Display.PolarAxes.RadialLabelLocation = 'Bottom'
threshold1Display.PolarAxes.RadialUnitsVisibility = 1
threshold1Display.PolarAxes.ScreenSize = 10.0
threshold1Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.PolarAxisTitleOpacity = 1.0
threshold1Display.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
threshold1Display.PolarAxes.PolarAxisTitleFontFile = ''
threshold1Display.PolarAxes.PolarAxisTitleBold = 0
threshold1Display.PolarAxes.PolarAxisTitleItalic = 0
threshold1Display.PolarAxes.PolarAxisTitleShadow = 0
threshold1Display.PolarAxes.PolarAxisTitleFontSize = 12
threshold1Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.PolarAxisLabelOpacity = 1.0
threshold1Display.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
threshold1Display.PolarAxes.PolarAxisLabelFontFile = ''
threshold1Display.PolarAxes.PolarAxisLabelBold = 0
threshold1Display.PolarAxes.PolarAxisLabelItalic = 0
threshold1Display.PolarAxes.PolarAxisLabelShadow = 0
threshold1Display.PolarAxes.PolarAxisLabelFontSize = 12
threshold1Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.LastRadialAxisTextOpacity = 1.0
threshold1Display.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
threshold1Display.PolarAxes.LastRadialAxisTextFontFile = ''
threshold1Display.PolarAxes.LastRadialAxisTextBold = 0
threshold1Display.PolarAxes.LastRadialAxisTextItalic = 0
threshold1Display.PolarAxes.LastRadialAxisTextShadow = 0
threshold1Display.PolarAxes.LastRadialAxisTextFontSize = 12
threshold1Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
threshold1Display.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
threshold1Display.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
threshold1Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''
threshold1Display.PolarAxes.SecondaryRadialAxesTextBold = 0
threshold1Display.PolarAxes.SecondaryRadialAxesTextItalic = 0
threshold1Display.PolarAxes.SecondaryRadialAxesTextShadow = 0
threshold1Display.PolarAxes.SecondaryRadialAxesTextFontSize = 12
threshold1Display.PolarAxes.EnableDistanceLOD = 1
threshold1Display.PolarAxes.DistanceLODThreshold = 0.7
threshold1Display.PolarAxes.EnableViewAngleLOD = 1
threshold1Display.PolarAxes.ViewAngleLODThreshold = 0.7
threshold1Display.PolarAxes.SmallestVisiblePolarAngle = 0.5
threshold1Display.PolarAxes.PolarTicksVisibility = 1
threshold1Display.PolarAxes.ArcTicksOriginToPolarAxis = 1
threshold1Display.PolarAxes.TickLocation = 'Both'
threshold1Display.PolarAxes.AxisTickVisibility = 1
threshold1Display.PolarAxes.AxisMinorTickVisibility = 0
threshold1Display.PolarAxes.ArcTickVisibility = 1
threshold1Display.PolarAxes.ArcMinorTickVisibility = 0
threshold1Display.PolarAxes.DeltaAngleMajor = 10.0
threshold1Display.PolarAxes.DeltaAngleMinor = 5.0
threshold1Display.PolarAxes.PolarAxisMajorTickSize = 0.0
threshold1Display.PolarAxes.PolarAxisTickRatioSize = 0.3
threshold1Display.PolarAxes.PolarAxisMajorTickThickness = 1.0
threshold1Display.PolarAxes.PolarAxisTickRatioThickness = 0.5
threshold1Display.PolarAxes.LastRadialAxisMajorTickSize = 0.0
threshold1Display.PolarAxes.LastRadialAxisTickRatioSize = 0.3
threshold1Display.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
threshold1Display.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
threshold1Display.PolarAxes.ArcMajorTickSize = 0.0
threshold1Display.PolarAxes.ArcTickRatioSize = 0.3
threshold1Display.PolarAxes.ArcMajorTickThickness = 1.0
threshold1Display.PolarAxes.ArcTickRatioThickness = 0.5
threshold1Display.PolarAxes.Use2DMode = 0
threshold1Display.PolarAxes.UseLogAxis = 0

# hide data in view
Hide(mainfoam, renderView1)

# show color bar/color legend
threshold1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# reset view to fit data
renderView1.ResetCamera()

# create a new 'Slice'
slice1 = Slice(Input=threshold1)
slice1.SliceType = 'Plane'
slice1.Crinkleslice = 0
slice1.Triangulatetheslice = 1
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [0.0001024999983201269, 0.0003949999954784289, 0.00010124999607796781]
slice1.SliceType.Normal = [1.0, 0.0, 0.0]
slice1.SliceType.Offset = 0.0

# Properties modified on slice1.SliceType
slice1.SliceType.Normal = [0.0, 1.0, 0.0]

# Properties modified on slice1.SliceType
slice1.SliceType.Normal = [0.0, 1.0, 0.0]

# show data in view
slice1Display = Show(slice1, renderView1)

# trace defaults for the display properties.
slice1Display.Representation = 'Surface'
slice1Display.AmbientColor = [1.0, 1.0, 1.0]
slice1Display.ColorArrayName = ['POINTS', 'p']
slice1Display.DiffuseColor = [1.0, 1.0, 1.0]
slice1Display.LookupTable = pLUT
slice1Display.MapScalars = 1
slice1Display.MultiComponentsMapping = 0
slice1Display.InterpolateScalarsBeforeMapping = 1
slice1Display.Opacity = 1.0
slice1Display.PointSize = 2.0
slice1Display.LineWidth = 1.0
slice1Display.RenderLinesAsTubes = 0
slice1Display.RenderPointsAsSpheres = 0
slice1Display.Interpolation = 'Gouraud'
slice1Display.Specular = 0.0
slice1Display.SpecularColor = [1.0, 1.0, 1.0]
slice1Display.SpecularPower = 100.0
slice1Display.Luminosity = 0.0
slice1Display.Ambient = 0.0
slice1Display.Diffuse = 1.0
slice1Display.EdgeColor = [0.0, 0.0, 0.5]
slice1Display.BackfaceRepresentation = 'Follow Frontface'
slice1Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
slice1Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
slice1Display.BackfaceOpacity = 1.0
slice1Display.Position = [0.0, 0.0, 0.0]
slice1Display.Scale = [1.0, 1.0, 1.0]
slice1Display.Orientation = [0.0, 0.0, 0.0]
slice1Display.Origin = [0.0, 0.0, 0.0]
slice1Display.Pickable = 1
slice1Display.Texture = None
slice1Display.Triangulate = 0
slice1Display.UseShaderReplacements = 0
slice1Display.ShaderReplacements = ''
slice1Display.NonlinearSubdivisionLevel = 1
slice1Display.UseDataPartitions = 0
slice1Display.OSPRayUseScaleArray = 0
slice1Display.OSPRayScaleArray = 'p'
slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice1Display.OSPRayMaterial = 'None'
slice1Display.Orient = 0
slice1Display.OrientationMode = 'Direction'
slice1Display.SelectOrientationVectors = 'U'
slice1Display.Scaling = 0
slice1Display.ScaleMode = 'No Data Scaling Off'
slice1Display.ScaleFactor = 5.750000127591193e-06
slice1Display.SelectScaleArray = 'p'
slice1Display.GlyphType = 'Arrow'
slice1Display.UseGlyphTable = 0
slice1Display.GlyphTableIndexArray = 'p'
slice1Display.UseCompositeGlyphTable = 0
slice1Display.UseGlyphCullingAndLOD = 0
slice1Display.LODValues = []
slice1Display.ColorByLODIndex = 0
slice1Display.GaussianRadius = 2.8750000637955967e-07
slice1Display.ShaderPreset = 'Sphere'
slice1Display.CustomTriangleScale = 3
slice1Display.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
slice1Display.Emissive = 0
slice1Display.ScaleByArray = 0
slice1Display.SetScaleArray = ['POINTS', 'p']
slice1Display.ScaleArrayComponent = ''
slice1Display.UseScaleFunction = 1
slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice1Display.OpacityByArray = 0
slice1Display.OpacityArray = ['POINTS', 'p']
slice1Display.OpacityArrayComponent = ''
slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice1Display.DataAxesGrid = 'GridAxesRepresentation'
slice1Display.SelectionCellLabelBold = 0
slice1Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
slice1Display.SelectionCellLabelFontFamily = 'Arial'
slice1Display.SelectionCellLabelFontFile = ''
slice1Display.SelectionCellLabelFontSize = 18
slice1Display.SelectionCellLabelItalic = 0
slice1Display.SelectionCellLabelJustification = 'Left'
slice1Display.SelectionCellLabelOpacity = 1.0
slice1Display.SelectionCellLabelShadow = 0
slice1Display.SelectionPointLabelBold = 0
slice1Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
slice1Display.SelectionPointLabelFontFamily = 'Arial'
slice1Display.SelectionPointLabelFontFile = ''
slice1Display.SelectionPointLabelFontSize = 18
slice1Display.SelectionPointLabelItalic = 0
slice1Display.SelectionPointLabelJustification = 'Left'
slice1Display.SelectionPointLabelOpacity = 1.0
slice1Display.SelectionPointLabelShadow = 0
slice1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
slice1Display.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
slice1Display.GlyphType.TipResolution = 6
slice1Display.GlyphType.TipRadius = 0.1
slice1Display.GlyphType.TipLength = 0.35
slice1Display.GlyphType.ShaftResolution = 6
slice1Display.GlyphType.ShaftRadius = 0.03
slice1Display.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
slice1Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
slice1Display.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
slice1Display.DataAxesGrid.XTitle = 'X Axis'
slice1Display.DataAxesGrid.YTitle = 'Y Axis'
slice1Display.DataAxesGrid.ZTitle = 'Z Axis'
slice1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.XTitleFontFamily = 'Arial'
slice1Display.DataAxesGrid.XTitleFontFile = ''
slice1Display.DataAxesGrid.XTitleBold = 0
slice1Display.DataAxesGrid.XTitleItalic = 0
slice1Display.DataAxesGrid.XTitleFontSize = 12
slice1Display.DataAxesGrid.XTitleShadow = 0
slice1Display.DataAxesGrid.XTitleOpacity = 1.0
slice1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.YTitleFontFamily = 'Arial'
slice1Display.DataAxesGrid.YTitleFontFile = ''
slice1Display.DataAxesGrid.YTitleBold = 0
slice1Display.DataAxesGrid.YTitleItalic = 0
slice1Display.DataAxesGrid.YTitleFontSize = 12
slice1Display.DataAxesGrid.YTitleShadow = 0
slice1Display.DataAxesGrid.YTitleOpacity = 1.0
slice1Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.ZTitleFontFamily = 'Arial'
slice1Display.DataAxesGrid.ZTitleFontFile = ''
slice1Display.DataAxesGrid.ZTitleBold = 0
slice1Display.DataAxesGrid.ZTitleItalic = 0
slice1Display.DataAxesGrid.ZTitleFontSize = 12
slice1Display.DataAxesGrid.ZTitleShadow = 0
slice1Display.DataAxesGrid.ZTitleOpacity = 1.0
slice1Display.DataAxesGrid.FacesToRender = 63
slice1Display.DataAxesGrid.CullBackface = 0
slice1Display.DataAxesGrid.CullFrontface = 1
slice1Display.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
slice1Display.DataAxesGrid.ShowGrid = 0
slice1Display.DataAxesGrid.ShowEdges = 1
slice1Display.DataAxesGrid.ShowTicks = 1
slice1Display.DataAxesGrid.LabelUniqueEdgesOnly = 1
slice1Display.DataAxesGrid.AxesToLabel = 63
slice1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.XLabelFontFamily = 'Arial'
slice1Display.DataAxesGrid.XLabelFontFile = ''
slice1Display.DataAxesGrid.XLabelBold = 0
slice1Display.DataAxesGrid.XLabelItalic = 0
slice1Display.DataAxesGrid.XLabelFontSize = 12
slice1Display.DataAxesGrid.XLabelShadow = 0
slice1Display.DataAxesGrid.XLabelOpacity = 1.0
slice1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.YLabelFontFamily = 'Arial'
slice1Display.DataAxesGrid.YLabelFontFile = ''
slice1Display.DataAxesGrid.YLabelBold = 0
slice1Display.DataAxesGrid.YLabelItalic = 0
slice1Display.DataAxesGrid.YLabelFontSize = 12
slice1Display.DataAxesGrid.YLabelShadow = 0
slice1Display.DataAxesGrid.YLabelOpacity = 1.0
slice1Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
slice1Display.DataAxesGrid.ZLabelFontFamily = 'Arial'
slice1Display.DataAxesGrid.ZLabelFontFile = ''
slice1Display.DataAxesGrid.ZLabelBold = 0
slice1Display.DataAxesGrid.ZLabelItalic = 0
slice1Display.DataAxesGrid.ZLabelFontSize = 12
slice1Display.DataAxesGrid.ZLabelShadow = 0
slice1Display.DataAxesGrid.ZLabelOpacity = 1.0
slice1Display.DataAxesGrid.XAxisNotation = 'Mixed'
slice1Display.DataAxesGrid.XAxisPrecision = 2
slice1Display.DataAxesGrid.XAxisUseCustomLabels = 0
slice1Display.DataAxesGrid.XAxisLabels = []
slice1Display.DataAxesGrid.YAxisNotation = 'Mixed'
slice1Display.DataAxesGrid.YAxisPrecision = 2
slice1Display.DataAxesGrid.YAxisUseCustomLabels = 0
slice1Display.DataAxesGrid.YAxisLabels = []
slice1Display.DataAxesGrid.ZAxisNotation = 'Mixed'
slice1Display.DataAxesGrid.ZAxisPrecision = 2
slice1Display.DataAxesGrid.ZAxisUseCustomLabels = 0
slice1Display.DataAxesGrid.ZAxisLabels = []

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
slice1Display.PolarAxes.Visibility = 0
slice1Display.PolarAxes.Translation = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.Scale = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.EnableCustomBounds = [0, 0, 0]
slice1Display.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
slice1Display.PolarAxes.EnableCustomRange = 0
slice1Display.PolarAxes.CustomRange = [0.0, 1.0]
slice1Display.PolarAxes.PolarAxisVisibility = 1
slice1Display.PolarAxes.RadialAxesVisibility = 1
slice1Display.PolarAxes.DrawRadialGridlines = 1
slice1Display.PolarAxes.PolarArcsVisibility = 1
slice1Display.PolarAxes.DrawPolarArcsGridlines = 1
slice1Display.PolarAxes.NumberOfRadialAxes = 0
slice1Display.PolarAxes.AutoSubdividePolarAxis = 1
slice1Display.PolarAxes.NumberOfPolarAxis = 0
slice1Display.PolarAxes.MinimumRadius = 0.0
slice1Display.PolarAxes.MinimumAngle = 0.0
slice1Display.PolarAxes.MaximumAngle = 90.0
slice1Display.PolarAxes.RadialAxesOriginToPolarAxis = 1
slice1Display.PolarAxes.Ratio = 1.0
slice1Display.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
slice1Display.PolarAxes.PolarAxisTitleVisibility = 1
slice1Display.PolarAxes.PolarAxisTitle = 'Radial Distance'
slice1Display.PolarAxes.PolarAxisTitleLocation = 'Bottom'
slice1Display.PolarAxes.PolarLabelVisibility = 1
slice1Display.PolarAxes.PolarLabelFormat = '%-#6.3g'
slice1Display.PolarAxes.PolarLabelExponentLocation = 'Labels'
slice1Display.PolarAxes.RadialLabelVisibility = 1
slice1Display.PolarAxes.RadialLabelFormat = '%-#3.1f'
slice1Display.PolarAxes.RadialLabelLocation = 'Bottom'
slice1Display.PolarAxes.RadialUnitsVisibility = 1
slice1Display.PolarAxes.ScreenSize = 10.0
slice1Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.PolarAxisTitleOpacity = 1.0
slice1Display.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
slice1Display.PolarAxes.PolarAxisTitleFontFile = ''
slice1Display.PolarAxes.PolarAxisTitleBold = 0
slice1Display.PolarAxes.PolarAxisTitleItalic = 0
slice1Display.PolarAxes.PolarAxisTitleShadow = 0
slice1Display.PolarAxes.PolarAxisTitleFontSize = 12
slice1Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.PolarAxisLabelOpacity = 1.0
slice1Display.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
slice1Display.PolarAxes.PolarAxisLabelFontFile = ''
slice1Display.PolarAxes.PolarAxisLabelBold = 0
slice1Display.PolarAxes.PolarAxisLabelItalic = 0
slice1Display.PolarAxes.PolarAxisLabelShadow = 0
slice1Display.PolarAxes.PolarAxisLabelFontSize = 12
slice1Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.LastRadialAxisTextOpacity = 1.0
slice1Display.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
slice1Display.PolarAxes.LastRadialAxisTextFontFile = ''
slice1Display.PolarAxes.LastRadialAxisTextBold = 0
slice1Display.PolarAxes.LastRadialAxisTextItalic = 0
slice1Display.PolarAxes.LastRadialAxisTextShadow = 0
slice1Display.PolarAxes.LastRadialAxisTextFontSize = 12
slice1Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
slice1Display.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
slice1Display.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
slice1Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''
slice1Display.PolarAxes.SecondaryRadialAxesTextBold = 0
slice1Display.PolarAxes.SecondaryRadialAxesTextItalic = 0
slice1Display.PolarAxes.SecondaryRadialAxesTextShadow = 0
slice1Display.PolarAxes.SecondaryRadialAxesTextFontSize = 12
slice1Display.PolarAxes.EnableDistanceLOD = 1
slice1Display.PolarAxes.DistanceLODThreshold = 0.7
slice1Display.PolarAxes.EnableViewAngleLOD = 1
slice1Display.PolarAxes.ViewAngleLODThreshold = 0.7
slice1Display.PolarAxes.SmallestVisiblePolarAngle = 0.5
slice1Display.PolarAxes.PolarTicksVisibility = 1
slice1Display.PolarAxes.ArcTicksOriginToPolarAxis = 1
slice1Display.PolarAxes.TickLocation = 'Both'
slice1Display.PolarAxes.AxisTickVisibility = 1
slice1Display.PolarAxes.AxisMinorTickVisibility = 0
slice1Display.PolarAxes.ArcTickVisibility = 1
slice1Display.PolarAxes.ArcMinorTickVisibility = 0
slice1Display.PolarAxes.DeltaAngleMajor = 10.0
slice1Display.PolarAxes.DeltaAngleMinor = 5.0
slice1Display.PolarAxes.PolarAxisMajorTickSize = 0.0
slice1Display.PolarAxes.PolarAxisTickRatioSize = 0.3
slice1Display.PolarAxes.PolarAxisMajorTickThickness = 1.0
slice1Display.PolarAxes.PolarAxisTickRatioThickness = 0.5
slice1Display.PolarAxes.LastRadialAxisMajorTickSize = 0.0
slice1Display.PolarAxes.LastRadialAxisTickRatioSize = 0.3
slice1Display.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
slice1Display.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
slice1Display.PolarAxes.ArcMajorTickSize = 0.0
slice1Display.PolarAxes.ArcTickRatioSize = 0.3
slice1Display.PolarAxes.ArcMajorTickThickness = 1.0
slice1Display.PolarAxes.ArcTickRatioThickness = 0.5
slice1Display.PolarAxes.Use2DMode = 0
slice1Display.PolarAxes.UseLogAxis = 0

# hide data in view
Hide(threshold1, renderView1)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(slice1Display, ('POINTS', 'solidificationTime'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
slice1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'solidificationTime'
solidificationTimeLUT = GetColorTransferFunction('solidificationTime')
solidificationTimeLUT.AutomaticRescaleRangeMode = "Grow and update on 'Apply'"
solidificationTimeLUT.InterpretValuesAsCategories = 0
solidificationTimeLUT.AnnotationsInitialized = 0
solidificationTimeLUT.ShowCategoricalColorsinDataRangeOnly = 0
solidificationTimeLUT.RescaleOnVisibilityChange = 0
solidificationTimeLUT.EnableOpacityMapping = 0
solidificationTimeLUT.RGBPoints = [0.0003329360915813595, 0.231373, 0.298039, 0.752941, 0.0004581666871672496, 0.865003, 0.865003, 0.865003, 0.0005833972827531397, 0.705882, 0.0156863, 0.14902]
solidificationTimeLUT.UseLogScale = 0
solidificationTimeLUT.ColorSpace = 'Diverging'
solidificationTimeLUT.UseBelowRangeColor = 0
solidificationTimeLUT.BelowRangeColor = [0.0, 0.0, 0.0]
solidificationTimeLUT.UseAboveRangeColor = 0
solidificationTimeLUT.AboveRangeColor = [0.5, 0.5, 0.5]
solidificationTimeLUT.NanColor = [1.0, 1.0, 0.0]
solidificationTimeLUT.NanOpacity = 1.0
solidificationTimeLUT.Discretize = 1
solidificationTimeLUT.NumberOfTableValues = 256
solidificationTimeLUT.ScalarRangeInitialized = 1.0
solidificationTimeLUT.HSVWrap = 0
solidificationTimeLUT.VectorComponent = 0
solidificationTimeLUT.VectorMode = 'Magnitude'
solidificationTimeLUT.AllowDuplicateScalars = 1
solidificationTimeLUT.Annotations = []
solidificationTimeLUT.ActiveAnnotatedValues = []
solidificationTimeLUT.IndexedColors = []
solidificationTimeLUT.IndexedOpacities = []

# get opacity transfer function/opacity map for 'solidificationTime'
solidificationTimePWF = GetOpacityTransferFunction('solidificationTime')
solidificationTimePWF.Points = [0.0003329360915813595, 0.0, 0.5, 0.0, 0.0005833972827531397, 1.0, 0.5, 0.0]
solidificationTimePWF.AllowDuplicateScalars = 1
solidificationTimePWF.UseLogScale = 0
solidificationTimePWF.ScalarRangeInitialized = 1

# change representation type
slice1Display.SetRepresentationType('Surface With Edges')

# destroy renderView1
Delete(renderView1)
del renderView1

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.UseCache = 0
spreadSheetView1.ViewSize = [400, 400]
spreadSheetView1.CellFontSize = 9
spreadSheetView1.HeaderFontSize = 9
spreadSheetView1.SelectionOnly = 0
spreadSheetView1.GenerateCellConnectivity = 0
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.SelectedComponent = -1
spreadSheetView1.InvertOrder = 0
spreadSheetView1.BlockSize = 1024L
spreadSheetView1.HiddenColumnLabels = []
spreadSheetView1.FieldAssociation = 'Point Data'

# get layout
layout1 = GetLayout()

# place view in the layout
layout1.AssignView(0, spreadSheetView1)

# show data in view
slice1Display = Show(slice1, spreadSheetView1)

# trace defaults for the display properties.
slice1Display.CompositeDataSetIndex = [0]

# export view
ExportView('/home/simon/Documents/PostDocSimon/TestsWithGowthamanSolver/GowthSolverCompiledSonic/TestsOnMeluxina/Test1/meltpool.csv', view=spreadSheetView1)

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).