# trace generated using paraview version 5.7.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active source.
#casefoam = GetActiveSource()
casefoam = OpenFOAMReader(FileName='main.foam')

# Properties modified on casefoam
casefoam.SkipZeroTime = 0
casefoam.MeshRegions = ['back', 'bottomWall', 'front', 'internalMesh', 'leftWall', 'rightWall', 'topWall']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [802, 907]

# show data in view
casefoamDisplay = Show(casefoam, renderView1)

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')
pLUT.AutomaticRescaleRangeMode = "Grow and update on 'Apply'"
pLUT.InterpretValuesAsCategories = 0
pLUT.AnnotationsInitialized = 0
pLUT.ShowCategoricalColorsinDataRangeOnly = 0
pLUT.RescaleOnVisibilityChange = 0
pLUT.EnableOpacityMapping = 0
pLUT.RGBPoints = [10434.0, 0.231373, 0.298039, 0.752941, 431020.5, 0.865003, 0.865003, 0.865003, 851607.0, 0.705882, 0.0156863, 0.14902]
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
casefoamDisplay.Representation = 'Surface'
casefoamDisplay.AmbientColor = [1.0, 1.0, 1.0]
casefoamDisplay.ColorArrayName = ['POINTS', 'p']
casefoamDisplay.DiffuseColor = [1.0, 1.0, 1.0]
casefoamDisplay.LookupTable = pLUT
casefoamDisplay.MapScalars = 1
casefoamDisplay.MultiComponentsMapping = 0
casefoamDisplay.InterpolateScalarsBeforeMapping = 1
casefoamDisplay.Opacity = 1.0
casefoamDisplay.PointSize = 2.0
casefoamDisplay.LineWidth = 1.0
casefoamDisplay.RenderLinesAsTubes = 0
casefoamDisplay.RenderPointsAsSpheres = 0
casefoamDisplay.Interpolation = 'Gouraud'
casefoamDisplay.Specular = 0.0
casefoamDisplay.SpecularColor = [1.0, 1.0, 1.0]
casefoamDisplay.SpecularPower = 100.0
casefoamDisplay.Luminosity = 0.0
casefoamDisplay.Ambient = 0.0
casefoamDisplay.Diffuse = 1.0
casefoamDisplay.EdgeColor = [0.0, 0.0, 0.5]
casefoamDisplay.BackfaceRepresentation = 'Follow Frontface'
casefoamDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
casefoamDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
casefoamDisplay.BackfaceOpacity = 1.0
casefoamDisplay.Position = [0.0, 0.0, 0.0]
casefoamDisplay.Scale = [1.0, 1.0, 1.0]
casefoamDisplay.Orientation = [0.0, 0.0, 0.0]
casefoamDisplay.Origin = [0.0, 0.0, 0.0]
casefoamDisplay.Pickable = 1
casefoamDisplay.Texture = None
casefoamDisplay.Triangulate = 0
casefoamDisplay.UseShaderReplacements = 0
casefoamDisplay.ShaderReplacements = ''
casefoamDisplay.NonlinearSubdivisionLevel = 1
casefoamDisplay.UseDataPartitions = 0
casefoamDisplay.OSPRayUseScaleArray = 0
casefoamDisplay.OSPRayScaleArray = 'p'
casefoamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
casefoamDisplay.OSPRayMaterial = 'None'
casefoamDisplay.Orient = 0
casefoamDisplay.OrientationMode = 'Direction'
casefoamDisplay.SelectOrientationVectors = 'U'
casefoamDisplay.Scaling = 0
casefoamDisplay.ScaleMode = 'No Data Scaling Off'
casefoamDisplay.ScaleFactor = 7.999999797903001e-05
casefoamDisplay.SelectScaleArray = 'p'
casefoamDisplay.GlyphType = 'Arrow'
casefoamDisplay.UseGlyphTable = 0
casefoamDisplay.GlyphTableIndexArray = 'p'
casefoamDisplay.UseCompositeGlyphTable = 0
casefoamDisplay.UseGlyphCullingAndLOD = 0
casefoamDisplay.LODValues = []
casefoamDisplay.ColorByLODIndex = 0
casefoamDisplay.GaussianRadius = 3.999999898951501e-06
casefoamDisplay.ShaderPreset = 'Sphere'
casefoamDisplay.CustomTriangleScale = 3
casefoamDisplay.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
casefoamDisplay.Emissive = 0
casefoamDisplay.ScaleByArray = 0
casefoamDisplay.SetScaleArray = ['POINTS', 'p']
casefoamDisplay.ScaleArrayComponent = ''
casefoamDisplay.UseScaleFunction = 1
casefoamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
casefoamDisplay.OpacityByArray = 0
casefoamDisplay.OpacityArray = ['POINTS', 'p']
casefoamDisplay.OpacityArrayComponent = ''
casefoamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
casefoamDisplay.DataAxesGrid = 'GridAxesRepresentation'
casefoamDisplay.SelectionCellLabelBold = 0
casefoamDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
casefoamDisplay.SelectionCellLabelFontFamily = 'Arial'
casefoamDisplay.SelectionCellLabelFontFile = ''
casefoamDisplay.SelectionCellLabelFontSize = 18
casefoamDisplay.SelectionCellLabelItalic = 0
casefoamDisplay.SelectionCellLabelJustification = 'Left'
casefoamDisplay.SelectionCellLabelOpacity = 1.0
casefoamDisplay.SelectionCellLabelShadow = 0
casefoamDisplay.SelectionPointLabelBold = 0
casefoamDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
casefoamDisplay.SelectionPointLabelFontFamily = 'Arial'
casefoamDisplay.SelectionPointLabelFontFile = ''
casefoamDisplay.SelectionPointLabelFontSize = 18
casefoamDisplay.SelectionPointLabelItalic = 0
casefoamDisplay.SelectionPointLabelJustification = 'Left'
casefoamDisplay.SelectionPointLabelOpacity = 1.0
casefoamDisplay.SelectionPointLabelShadow = 0
casefoamDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
casefoamDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
casefoamDisplay.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
casefoamDisplay.GlyphType.TipResolution = 6
casefoamDisplay.GlyphType.TipRadius = 0.1
casefoamDisplay.GlyphType.TipLength = 0.35
casefoamDisplay.GlyphType.ShaftResolution = 6
casefoamDisplay.GlyphType.ShaftRadius = 0.03
casefoamDisplay.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
casefoamDisplay.ScaleTransferFunction.Points = [10434.0, 0.0, 0.5, 0.0, 851607.0, 1.0, 0.5, 0.0]
casefoamDisplay.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
casefoamDisplay.OpacityTransferFunction.Points = [10434.0, 0.0, 0.5, 0.0, 851607.0, 1.0, 0.5, 0.0]
casefoamDisplay.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
casefoamDisplay.DataAxesGrid.XTitle = 'X Axis'
casefoamDisplay.DataAxesGrid.YTitle = 'Y Axis'
casefoamDisplay.DataAxesGrid.ZTitle = 'Z Axis'
casefoamDisplay.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.XTitleFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.XTitleFontFile = ''
casefoamDisplay.DataAxesGrid.XTitleBold = 0
casefoamDisplay.DataAxesGrid.XTitleItalic = 0
casefoamDisplay.DataAxesGrid.XTitleFontSize = 12
casefoamDisplay.DataAxesGrid.XTitleShadow = 0
casefoamDisplay.DataAxesGrid.XTitleOpacity = 1.0
casefoamDisplay.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.YTitleFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.YTitleFontFile = ''
casefoamDisplay.DataAxesGrid.YTitleBold = 0
casefoamDisplay.DataAxesGrid.YTitleItalic = 0
casefoamDisplay.DataAxesGrid.YTitleFontSize = 12
casefoamDisplay.DataAxesGrid.YTitleShadow = 0
casefoamDisplay.DataAxesGrid.YTitleOpacity = 1.0
casefoamDisplay.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.ZTitleFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.ZTitleFontFile = ''
casefoamDisplay.DataAxesGrid.ZTitleBold = 0
casefoamDisplay.DataAxesGrid.ZTitleItalic = 0
casefoamDisplay.DataAxesGrid.ZTitleFontSize = 12
casefoamDisplay.DataAxesGrid.ZTitleShadow = 0
casefoamDisplay.DataAxesGrid.ZTitleOpacity = 1.0
casefoamDisplay.DataAxesGrid.FacesToRender = 63
casefoamDisplay.DataAxesGrid.CullBackface = 0
casefoamDisplay.DataAxesGrid.CullFrontface = 1
casefoamDisplay.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
casefoamDisplay.DataAxesGrid.ShowGrid = 0
casefoamDisplay.DataAxesGrid.ShowEdges = 1
casefoamDisplay.DataAxesGrid.ShowTicks = 1
casefoamDisplay.DataAxesGrid.LabelUniqueEdgesOnly = 1
casefoamDisplay.DataAxesGrid.AxesToLabel = 63
casefoamDisplay.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.XLabelFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.XLabelFontFile = ''
casefoamDisplay.DataAxesGrid.XLabelBold = 0
casefoamDisplay.DataAxesGrid.XLabelItalic = 0
casefoamDisplay.DataAxesGrid.XLabelFontSize = 12
casefoamDisplay.DataAxesGrid.XLabelShadow = 0
casefoamDisplay.DataAxesGrid.XLabelOpacity = 1.0
casefoamDisplay.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.YLabelFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.YLabelFontFile = ''
casefoamDisplay.DataAxesGrid.YLabelBold = 0
casefoamDisplay.DataAxesGrid.YLabelItalic = 0
casefoamDisplay.DataAxesGrid.YLabelFontSize = 12
casefoamDisplay.DataAxesGrid.YLabelShadow = 0
casefoamDisplay.DataAxesGrid.YLabelOpacity = 1.0
casefoamDisplay.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
casefoamDisplay.DataAxesGrid.ZLabelFontFamily = 'Arial'
casefoamDisplay.DataAxesGrid.ZLabelFontFile = ''
casefoamDisplay.DataAxesGrid.ZLabelBold = 0
casefoamDisplay.DataAxesGrid.ZLabelItalic = 0
casefoamDisplay.DataAxesGrid.ZLabelFontSize = 12
casefoamDisplay.DataAxesGrid.ZLabelShadow = 0
casefoamDisplay.DataAxesGrid.ZLabelOpacity = 1.0
casefoamDisplay.DataAxesGrid.XAxisNotation = 'Mixed'
casefoamDisplay.DataAxesGrid.XAxisPrecision = 2
casefoamDisplay.DataAxesGrid.XAxisUseCustomLabels = 0
casefoamDisplay.DataAxesGrid.XAxisLabels = []
casefoamDisplay.DataAxesGrid.YAxisNotation = 'Mixed'
casefoamDisplay.DataAxesGrid.YAxisPrecision = 2
casefoamDisplay.DataAxesGrid.YAxisUseCustomLabels = 0
casefoamDisplay.DataAxesGrid.YAxisLabels = []
casefoamDisplay.DataAxesGrid.ZAxisNotation = 'Mixed'
casefoamDisplay.DataAxesGrid.ZAxisPrecision = 2
casefoamDisplay.DataAxesGrid.ZAxisUseCustomLabels = 0
casefoamDisplay.DataAxesGrid.ZAxisLabels = []
casefoamDisplay.DataAxesGrid.UseCustomBounds = 0
casefoamDisplay.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
casefoamDisplay.PolarAxes.Visibility = 0
casefoamDisplay.PolarAxes.Translation = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.Scale = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.Orientation = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.EnableCustomBounds = [0, 0, 0]
casefoamDisplay.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
casefoamDisplay.PolarAxes.EnableCustomRange = 0
casefoamDisplay.PolarAxes.CustomRange = [0.0, 1.0]
casefoamDisplay.PolarAxes.PolarAxisVisibility = 1
casefoamDisplay.PolarAxes.RadialAxesVisibility = 1
casefoamDisplay.PolarAxes.DrawRadialGridlines = 1
casefoamDisplay.PolarAxes.PolarArcsVisibility = 1
casefoamDisplay.PolarAxes.DrawPolarArcsGridlines = 1
casefoamDisplay.PolarAxes.NumberOfRadialAxes = 0
casefoamDisplay.PolarAxes.AutoSubdividePolarAxis = 1
casefoamDisplay.PolarAxes.NumberOfPolarAxis = 0
casefoamDisplay.PolarAxes.MinimumRadius = 0.0
casefoamDisplay.PolarAxes.MinimumAngle = 0.0
casefoamDisplay.PolarAxes.MaximumAngle = 90.0
casefoamDisplay.PolarAxes.RadialAxesOriginToPolarAxis = 1
casefoamDisplay.PolarAxes.Ratio = 1.0
casefoamDisplay.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
casefoamDisplay.PolarAxes.PolarAxisTitleVisibility = 1
casefoamDisplay.PolarAxes.PolarAxisTitle = 'Radial Distance'
casefoamDisplay.PolarAxes.PolarAxisTitleLocation = 'Bottom'
casefoamDisplay.PolarAxes.PolarLabelVisibility = 1
casefoamDisplay.PolarAxes.PolarLabelFormat = '%-#6.3g'
casefoamDisplay.PolarAxes.PolarLabelExponentLocation = 'Labels'
casefoamDisplay.PolarAxes.RadialLabelVisibility = 1
casefoamDisplay.PolarAxes.RadialLabelFormat = '%-#3.1f'
casefoamDisplay.PolarAxes.RadialLabelLocation = 'Bottom'
casefoamDisplay.PolarAxes.RadialUnitsVisibility = 1
casefoamDisplay.PolarAxes.ScreenSize = 10.0
casefoamDisplay.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.PolarAxisTitleOpacity = 1.0
casefoamDisplay.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
casefoamDisplay.PolarAxes.PolarAxisTitleFontFile = ''
casefoamDisplay.PolarAxes.PolarAxisTitleBold = 0
casefoamDisplay.PolarAxes.PolarAxisTitleItalic = 0
casefoamDisplay.PolarAxes.PolarAxisTitleShadow = 0
casefoamDisplay.PolarAxes.PolarAxisTitleFontSize = 12
casefoamDisplay.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.PolarAxisLabelOpacity = 1.0
casefoamDisplay.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
casefoamDisplay.PolarAxes.PolarAxisLabelFontFile = ''
casefoamDisplay.PolarAxes.PolarAxisLabelBold = 0
casefoamDisplay.PolarAxes.PolarAxisLabelItalic = 0
casefoamDisplay.PolarAxes.PolarAxisLabelShadow = 0
casefoamDisplay.PolarAxes.PolarAxisLabelFontSize = 12
casefoamDisplay.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.LastRadialAxisTextOpacity = 1.0
casefoamDisplay.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
casefoamDisplay.PolarAxes.LastRadialAxisTextFontFile = ''
casefoamDisplay.PolarAxes.LastRadialAxisTextBold = 0
casefoamDisplay.PolarAxes.LastRadialAxisTextItalic = 0
casefoamDisplay.PolarAxes.LastRadialAxisTextShadow = 0
casefoamDisplay.PolarAxes.LastRadialAxisTextFontSize = 12
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextFontFile = ''
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextBold = 0
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextItalic = 0
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextShadow = 0
casefoamDisplay.PolarAxes.SecondaryRadialAxesTextFontSize = 12
casefoamDisplay.PolarAxes.EnableDistanceLOD = 1
casefoamDisplay.PolarAxes.DistanceLODThreshold = 0.7
casefoamDisplay.PolarAxes.EnableViewAngleLOD = 1
casefoamDisplay.PolarAxes.ViewAngleLODThreshold = 0.7
casefoamDisplay.PolarAxes.SmallestVisiblePolarAngle = 0.5
casefoamDisplay.PolarAxes.PolarTicksVisibility = 1
casefoamDisplay.PolarAxes.ArcTicksOriginToPolarAxis = 1
casefoamDisplay.PolarAxes.TickLocation = 'Both'
casefoamDisplay.PolarAxes.AxisTickVisibility = 1
casefoamDisplay.PolarAxes.AxisMinorTickVisibility = 0
casefoamDisplay.PolarAxes.ArcTickVisibility = 1
casefoamDisplay.PolarAxes.ArcMinorTickVisibility = 0
casefoamDisplay.PolarAxes.DeltaAngleMajor = 10.0
casefoamDisplay.PolarAxes.DeltaAngleMinor = 5.0
casefoamDisplay.PolarAxes.PolarAxisMajorTickSize = 0.0
casefoamDisplay.PolarAxes.PolarAxisTickRatioSize = 0.3
casefoamDisplay.PolarAxes.PolarAxisMajorTickThickness = 1.0
casefoamDisplay.PolarAxes.PolarAxisTickRatioThickness = 0.5
casefoamDisplay.PolarAxes.LastRadialAxisMajorTickSize = 0.0
casefoamDisplay.PolarAxes.LastRadialAxisTickRatioSize = 0.3
casefoamDisplay.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
casefoamDisplay.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
casefoamDisplay.PolarAxes.ArcMajorTickSize = 0.0
casefoamDisplay.PolarAxes.ArcTickRatioSize = 0.3
casefoamDisplay.PolarAxes.ArcMajorTickThickness = 1.0
casefoamDisplay.PolarAxes.ArcTickRatioThickness = 0.5
casefoamDisplay.PolarAxes.Use2DMode = 0
casefoamDisplay.PolarAxes.UseLogAxis = 0

# reset view to fit data
renderView1.ResetCamera()

# show color bar/color legend
casefoamDisplay.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')
pPWF.Points = [10434.0, 0.0, 0.5, 0.0, 851607.0, 1.0, 0.5, 0.0]
pPWF.AllowDuplicateScalars = 1
pPWF.UseLogScale = 0
pPWF.ScalarRangeInitialized = 1

# create a new 'Clip'
clip1 = Clip(Input=casefoam)
clip1.ClipType = 'Plane'
clip1.Scalars = ['POINTS', 'p']
clip1.Value = 431020.5
clip1.Invert = 1
clip1.Crinkleclip = 0
clip1.Exact = 0

# init the 'Plane' selected for 'ClipType'
clip1.ClipType.Origin = [9.999999747378752e-05, 0.00039999998989515007, 9.999999747378752e-05]
clip1.ClipType.Normal = [1.0, 0.0, 0.0]
clip1.ClipType.Offset = 0.0

# Properties modified on clip1
clip1.ClipType = 'Scalar'
clip1.Scalars = ['POINTS', 'alpha.material']
clip1.Value = 0.5
clip1.Invert = 0

# show data in view
clip1Display = Show(clip1, renderView1)

# trace defaults for the display properties.
clip1Display.Representation = 'Surface'
clip1Display.AmbientColor = [1.0, 1.0, 1.0]
clip1Display.ColorArrayName = ['POINTS', 'p']
clip1Display.DiffuseColor = [1.0, 1.0, 1.0]
clip1Display.LookupTable = pLUT
clip1Display.MapScalars = 1
clip1Display.MultiComponentsMapping = 0
clip1Display.InterpolateScalarsBeforeMapping = 1
clip1Display.Opacity = 1.0
clip1Display.PointSize = 2.0
clip1Display.LineWidth = 1.0
clip1Display.RenderLinesAsTubes = 0
clip1Display.RenderPointsAsSpheres = 0
clip1Display.Interpolation = 'Gouraud'
clip1Display.Specular = 0.0
clip1Display.SpecularColor = [1.0, 1.0, 1.0]
clip1Display.SpecularPower = 100.0
clip1Display.Luminosity = 0.0
clip1Display.Ambient = 0.0
clip1Display.Diffuse = 1.0
clip1Display.EdgeColor = [0.0, 0.0, 0.5]
clip1Display.BackfaceRepresentation = 'Follow Frontface'
clip1Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
clip1Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
clip1Display.BackfaceOpacity = 1.0
clip1Display.Position = [0.0, 0.0, 0.0]
clip1Display.Scale = [1.0, 1.0, 1.0]
clip1Display.Orientation = [0.0, 0.0, 0.0]
clip1Display.Origin = [0.0, 0.0, 0.0]
clip1Display.Pickable = 1
clip1Display.Texture = None
clip1Display.Triangulate = 0
clip1Display.UseShaderReplacements = 0
clip1Display.ShaderReplacements = ''
clip1Display.NonlinearSubdivisionLevel = 1
clip1Display.UseDataPartitions = 0
clip1Display.OSPRayUseScaleArray = 0
clip1Display.OSPRayScaleArray = 'p'
clip1Display.OSPRayScaleFunction = 'PiecewiseFunction'
clip1Display.OSPRayMaterial = 'None'
clip1Display.Orient = 0
clip1Display.OrientationMode = 'Direction'
clip1Display.SelectOrientationVectors = 'U'
clip1Display.Scaling = 0
clip1Display.ScaleMode = 'No Data Scaling Off'
clip1Display.ScaleFactor = 7.999999797903001e-05
clip1Display.SelectScaleArray = 'p'
clip1Display.GlyphType = 'Arrow'
clip1Display.UseGlyphTable = 0
clip1Display.GlyphTableIndexArray = 'p'
clip1Display.UseCompositeGlyphTable = 0
clip1Display.UseGlyphCullingAndLOD = 0
clip1Display.LODValues = []
clip1Display.ColorByLODIndex = 0
clip1Display.GaussianRadius = 3.999999898951501e-06
clip1Display.ShaderPreset = 'Sphere'
clip1Display.CustomTriangleScale = 3
clip1Display.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
clip1Display.Emissive = 0
clip1Display.ScaleByArray = 0
clip1Display.SetScaleArray = ['POINTS', 'p']
clip1Display.ScaleArrayComponent = ''
clip1Display.UseScaleFunction = 1
clip1Display.ScaleTransferFunction = 'PiecewiseFunction'
clip1Display.OpacityByArray = 0
clip1Display.OpacityArray = ['POINTS', 'p']
clip1Display.OpacityArrayComponent = ''
clip1Display.OpacityTransferFunction = 'PiecewiseFunction'
clip1Display.DataAxesGrid = 'GridAxesRepresentation'
clip1Display.SelectionCellLabelBold = 0
clip1Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
clip1Display.SelectionCellLabelFontFamily = 'Arial'
clip1Display.SelectionCellLabelFontFile = ''
clip1Display.SelectionCellLabelFontSize = 18
clip1Display.SelectionCellLabelItalic = 0
clip1Display.SelectionCellLabelJustification = 'Left'
clip1Display.SelectionCellLabelOpacity = 1.0
clip1Display.SelectionCellLabelShadow = 0
clip1Display.SelectionPointLabelBold = 0
clip1Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
clip1Display.SelectionPointLabelFontFamily = 'Arial'
clip1Display.SelectionPointLabelFontFile = ''
clip1Display.SelectionPointLabelFontSize = 18
clip1Display.SelectionPointLabelItalic = 0
clip1Display.SelectionPointLabelJustification = 'Left'
clip1Display.SelectionPointLabelOpacity = 1.0
clip1Display.SelectionPointLabelShadow = 0
clip1Display.PolarAxes = 'PolarAxesRepresentation'
clip1Display.ScalarOpacityFunction = pPWF
clip1Display.ScalarOpacityUnitDistance = 1.0307660144600464e-05
clip1Display.ExtractedBlockIndex = 1
clip1Display.SelectMapper = 'Projected tetra'
clip1Display.SamplingDimensions = [128, 128, 128]
clip1Display.UseFloatingPointFrameBuffer = 1

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
clip1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
clip1Display.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
clip1Display.GlyphType.TipResolution = 6
clip1Display.GlyphType.TipRadius = 0.1
clip1Display.GlyphType.TipLength = 0.35
clip1Display.GlyphType.ShaftResolution = 6
clip1Display.GlyphType.ShaftRadius = 0.03
clip1Display.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
clip1Display.ScaleTransferFunction.Points = [10434.0, 0.0, 0.5, 0.0, 851607.0, 1.0, 0.5, 0.0]
clip1Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
clip1Display.OpacityTransferFunction.Points = [10434.0, 0.0, 0.5, 0.0, 851607.0, 1.0, 0.5, 0.0]
clip1Display.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
clip1Display.DataAxesGrid.XTitle = 'X Axis'
clip1Display.DataAxesGrid.YTitle = 'Y Axis'
clip1Display.DataAxesGrid.ZTitle = 'Z Axis'
clip1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.XTitleFontFamily = 'Arial'
clip1Display.DataAxesGrid.XTitleFontFile = ''
clip1Display.DataAxesGrid.XTitleBold = 0
clip1Display.DataAxesGrid.XTitleItalic = 0
clip1Display.DataAxesGrid.XTitleFontSize = 12
clip1Display.DataAxesGrid.XTitleShadow = 0
clip1Display.DataAxesGrid.XTitleOpacity = 1.0
clip1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.YTitleFontFamily = 'Arial'
clip1Display.DataAxesGrid.YTitleFontFile = ''
clip1Display.DataAxesGrid.YTitleBold = 0
clip1Display.DataAxesGrid.YTitleItalic = 0
clip1Display.DataAxesGrid.YTitleFontSize = 12
clip1Display.DataAxesGrid.YTitleShadow = 0
clip1Display.DataAxesGrid.YTitleOpacity = 1.0
clip1Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.ZTitleFontFamily = 'Arial'
clip1Display.DataAxesGrid.ZTitleFontFile = ''
clip1Display.DataAxesGrid.ZTitleBold = 0
clip1Display.DataAxesGrid.ZTitleItalic = 0
clip1Display.DataAxesGrid.ZTitleFontSize = 12
clip1Display.DataAxesGrid.ZTitleShadow = 0
clip1Display.DataAxesGrid.ZTitleOpacity = 1.0
clip1Display.DataAxesGrid.FacesToRender = 63
clip1Display.DataAxesGrid.CullBackface = 0
clip1Display.DataAxesGrid.CullFrontface = 1
clip1Display.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
clip1Display.DataAxesGrid.ShowGrid = 0
clip1Display.DataAxesGrid.ShowEdges = 1
clip1Display.DataAxesGrid.ShowTicks = 1
clip1Display.DataAxesGrid.LabelUniqueEdgesOnly = 1
clip1Display.DataAxesGrid.AxesToLabel = 63
clip1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.XLabelFontFamily = 'Arial'
clip1Display.DataAxesGrid.XLabelFontFile = ''
clip1Display.DataAxesGrid.XLabelBold = 0
clip1Display.DataAxesGrid.XLabelItalic = 0
clip1Display.DataAxesGrid.XLabelFontSize = 12
clip1Display.DataAxesGrid.XLabelShadow = 0
clip1Display.DataAxesGrid.XLabelOpacity = 1.0
clip1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.YLabelFontFamily = 'Arial'
clip1Display.DataAxesGrid.YLabelFontFile = ''
clip1Display.DataAxesGrid.YLabelBold = 0
clip1Display.DataAxesGrid.YLabelItalic = 0
clip1Display.DataAxesGrid.YLabelFontSize = 12
clip1Display.DataAxesGrid.YLabelShadow = 0
clip1Display.DataAxesGrid.YLabelOpacity = 1.0
clip1Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
clip1Display.DataAxesGrid.ZLabelFontFamily = 'Arial'
clip1Display.DataAxesGrid.ZLabelFontFile = ''
clip1Display.DataAxesGrid.ZLabelBold = 0
clip1Display.DataAxesGrid.ZLabelItalic = 0
clip1Display.DataAxesGrid.ZLabelFontSize = 12
clip1Display.DataAxesGrid.ZLabelShadow = 0
clip1Display.DataAxesGrid.ZLabelOpacity = 1.0
clip1Display.DataAxesGrid.XAxisNotation = 'Mixed'
clip1Display.DataAxesGrid.XAxisPrecision = 2
clip1Display.DataAxesGrid.XAxisUseCustomLabels = 0
clip1Display.DataAxesGrid.XAxisLabels = []
clip1Display.DataAxesGrid.YAxisNotation = 'Mixed'
clip1Display.DataAxesGrid.YAxisPrecision = 2
clip1Display.DataAxesGrid.YAxisUseCustomLabels = 0
clip1Display.DataAxesGrid.YAxisLabels = []
clip1Display.DataAxesGrid.ZAxisNotation = 'Mixed'
clip1Display.DataAxesGrid.ZAxisPrecision = 2
clip1Display.DataAxesGrid.ZAxisUseCustomLabels = 0
clip1Display.DataAxesGrid.ZAxisLabels = []
clip1Display.DataAxesGrid.UseCustomBounds = 0
clip1Display.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
clip1Display.PolarAxes.Visibility = 0
clip1Display.PolarAxes.Translation = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.Scale = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.EnableCustomBounds = [0, 0, 0]
clip1Display.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
clip1Display.PolarAxes.EnableCustomRange = 0
clip1Display.PolarAxes.CustomRange = [0.0, 1.0]
clip1Display.PolarAxes.PolarAxisVisibility = 1
clip1Display.PolarAxes.RadialAxesVisibility = 1
clip1Display.PolarAxes.DrawRadialGridlines = 1
clip1Display.PolarAxes.PolarArcsVisibility = 1
clip1Display.PolarAxes.DrawPolarArcsGridlines = 1
clip1Display.PolarAxes.NumberOfRadialAxes = 0
clip1Display.PolarAxes.AutoSubdividePolarAxis = 1
clip1Display.PolarAxes.NumberOfPolarAxis = 0
clip1Display.PolarAxes.MinimumRadius = 0.0
clip1Display.PolarAxes.MinimumAngle = 0.0
clip1Display.PolarAxes.MaximumAngle = 90.0
clip1Display.PolarAxes.RadialAxesOriginToPolarAxis = 1
clip1Display.PolarAxes.Ratio = 1.0
clip1Display.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
clip1Display.PolarAxes.PolarAxisTitleVisibility = 1
clip1Display.PolarAxes.PolarAxisTitle = 'Radial Distance'
clip1Display.PolarAxes.PolarAxisTitleLocation = 'Bottom'
clip1Display.PolarAxes.PolarLabelVisibility = 1
clip1Display.PolarAxes.PolarLabelFormat = '%-#6.3g'
clip1Display.PolarAxes.PolarLabelExponentLocation = 'Labels'
clip1Display.PolarAxes.RadialLabelVisibility = 1
clip1Display.PolarAxes.RadialLabelFormat = '%-#3.1f'
clip1Display.PolarAxes.RadialLabelLocation = 'Bottom'
clip1Display.PolarAxes.RadialUnitsVisibility = 1
clip1Display.PolarAxes.ScreenSize = 10.0
clip1Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.PolarAxisTitleOpacity = 1.0
clip1Display.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
clip1Display.PolarAxes.PolarAxisTitleFontFile = ''
clip1Display.PolarAxes.PolarAxisTitleBold = 0
clip1Display.PolarAxes.PolarAxisTitleItalic = 0
clip1Display.PolarAxes.PolarAxisTitleShadow = 0
clip1Display.PolarAxes.PolarAxisTitleFontSize = 12
clip1Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.PolarAxisLabelOpacity = 1.0
clip1Display.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
clip1Display.PolarAxes.PolarAxisLabelFontFile = ''
clip1Display.PolarAxes.PolarAxisLabelBold = 0
clip1Display.PolarAxes.PolarAxisLabelItalic = 0
clip1Display.PolarAxes.PolarAxisLabelShadow = 0
clip1Display.PolarAxes.PolarAxisLabelFontSize = 12
clip1Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.LastRadialAxisTextOpacity = 1.0
clip1Display.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
clip1Display.PolarAxes.LastRadialAxisTextFontFile = ''
clip1Display.PolarAxes.LastRadialAxisTextBold = 0
clip1Display.PolarAxes.LastRadialAxisTextItalic = 0
clip1Display.PolarAxes.LastRadialAxisTextShadow = 0
clip1Display.PolarAxes.LastRadialAxisTextFontSize = 12
clip1Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
clip1Display.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
clip1Display.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
clip1Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''
clip1Display.PolarAxes.SecondaryRadialAxesTextBold = 0
clip1Display.PolarAxes.SecondaryRadialAxesTextItalic = 0
clip1Display.PolarAxes.SecondaryRadialAxesTextShadow = 0
clip1Display.PolarAxes.SecondaryRadialAxesTextFontSize = 12
clip1Display.PolarAxes.EnableDistanceLOD = 1
clip1Display.PolarAxes.DistanceLODThreshold = 0.7
clip1Display.PolarAxes.EnableViewAngleLOD = 1
clip1Display.PolarAxes.ViewAngleLODThreshold = 0.7
clip1Display.PolarAxes.SmallestVisiblePolarAngle = 0.5
clip1Display.PolarAxes.PolarTicksVisibility = 1
clip1Display.PolarAxes.ArcTicksOriginToPolarAxis = 1
clip1Display.PolarAxes.TickLocation = 'Both'
clip1Display.PolarAxes.AxisTickVisibility = 1
clip1Display.PolarAxes.AxisMinorTickVisibility = 0
clip1Display.PolarAxes.ArcTickVisibility = 1
clip1Display.PolarAxes.ArcMinorTickVisibility = 0
clip1Display.PolarAxes.DeltaAngleMajor = 10.0
clip1Display.PolarAxes.DeltaAngleMinor = 5.0
clip1Display.PolarAxes.PolarAxisMajorTickSize = 0.0
clip1Display.PolarAxes.PolarAxisTickRatioSize = 0.3
clip1Display.PolarAxes.PolarAxisMajorTickThickness = 1.0
clip1Display.PolarAxes.PolarAxisTickRatioThickness = 0.5
clip1Display.PolarAxes.LastRadialAxisMajorTickSize = 0.0
clip1Display.PolarAxes.LastRadialAxisTickRatioSize = 0.3
clip1Display.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
clip1Display.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
clip1Display.PolarAxes.ArcMajorTickSize = 0.0
clip1Display.PolarAxes.ArcTickRatioSize = 0.3
clip1Display.PolarAxes.ArcMajorTickThickness = 1.0
clip1Display.PolarAxes.ArcTickRatioThickness = 0.5
clip1Display.PolarAxes.Use2DMode = 0
clip1Display.PolarAxes.UseLogAxis = 0

# hide data in view
Hide(casefoam, renderView1)

# show color bar/color legend
clip1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

animationScene1.GoToLast()

# set scalar coloring
ColorBy(clip1Display, ('POINTS', 'T'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
clip1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
clip1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'T'
tLUT = GetColorTransferFunction('T')
tLUT.AutomaticRescaleRangeMode = "Grow and update on 'Apply'"
tLUT.InterpretValuesAsCategories = 0
tLUT.AnnotationsInitialized = 0
tLUT.ShowCategoricalColorsinDataRangeOnly = 0
tLUT.RescaleOnVisibilityChange = 0
tLUT.EnableOpacityMapping = 0
tLUT.RGBPoints = [298.0140075683594, 0.231373, 0.298039, 0.752941, 949.8824310302734, 0.865003, 0.865003, 0.865003, 1601.7508544921875, 0.705882, 0.0156863, 0.14902]
tLUT.UseLogScale = 0
tLUT.ColorSpace = 'Diverging'
tLUT.UseBelowRangeColor = 0
tLUT.BelowRangeColor = [0.0, 0.0, 0.0]
tLUT.UseAboveRangeColor = 0
tLUT.AboveRangeColor = [0.5, 0.5, 0.5]
tLUT.NanColor = [1.0, 1.0, 0.0]
tLUT.NanOpacity = 1.0
tLUT.Discretize = 1
tLUT.NumberOfTableValues = 256
tLUT.ScalarRangeInitialized = 1.0
tLUT.HSVWrap = 0
tLUT.VectorComponent = 0
tLUT.VectorMode = 'Magnitude'
tLUT.AllowDuplicateScalars = 1
tLUT.Annotations = []
tLUT.ActiveAnnotatedValues = []
tLUT.IndexedColors = []
tLUT.IndexedOpacities = []

# get opacity transfer function/opacity map for 'T'
tPWF = GetOpacityTransferFunction('T')
tPWF.Points = [298.0140075683594, 0.0, 0.5, 0.0, 1601.7508544921875, 1.0, 0.5, 0.0]
tPWF.AllowDuplicateScalars = 1
tPWF.UseLogScale = 0
tPWF.ScalarRangeInitialized = 1

# create a new 'Clip'
clip2 = Clip(Input=clip1)
clip2.ClipType = 'Plane'
clip2.Scalars = ['POINTS', 'p']
clip2.Value = 412585.6689453125
clip2.Invert = 1
clip2.Crinkleclip = 0
clip2.Exact = 0

# init the 'Plane' selected for 'ClipType'
clip2.ClipType.Origin = [9.999999747378752e-05, 0.00039999998989515007, 7.400000322377309e-05]
clip2.ClipType.Normal = [1.0, 0.0, 0.0]
clip2.ClipType.Offset = 0.0

# Properties modified on clip2
clip2.ClipType = 'Scalar'
clip2.Scalars = ['POINTS', 'solidificationTime']
clip2.Value = 0.0
clip2.Invert = 0

# show data in view
clip2Display = Show(clip2, renderView1)

# trace defaults for the display properties.
clip2Display.Representation = 'Surface'
clip2Display.AmbientColor = [1.0, 1.0, 1.0]
clip2Display.ColorArrayName = ['POINTS', 'p']
clip2Display.DiffuseColor = [1.0, 1.0, 1.0]
clip2Display.LookupTable = pLUT
clip2Display.MapScalars = 1
clip2Display.MultiComponentsMapping = 0
clip2Display.InterpolateScalarsBeforeMapping = 1
clip2Display.Opacity = 1.0
clip2Display.PointSize = 2.0
clip2Display.LineWidth = 1.0
clip2Display.RenderLinesAsTubes = 0
clip2Display.RenderPointsAsSpheres = 0
clip2Display.Interpolation = 'Gouraud'
clip2Display.Specular = 0.0
clip2Display.SpecularColor = [1.0, 1.0, 1.0]
clip2Display.SpecularPower = 100.0
clip2Display.Luminosity = 0.0
clip2Display.Ambient = 0.0
clip2Display.Diffuse = 1.0
clip2Display.EdgeColor = [0.0, 0.0, 0.5]
clip2Display.BackfaceRepresentation = 'Follow Frontface'
clip2Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
clip2Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
clip2Display.BackfaceOpacity = 1.0
clip2Display.Position = [0.0, 0.0, 0.0]
clip2Display.Scale = [1.0, 1.0, 1.0]
clip2Display.Orientation = [0.0, 0.0, 0.0]
clip2Display.Origin = [0.0, 0.0, 0.0]
clip2Display.Pickable = 1
clip2Display.Texture = None
clip2Display.Triangulate = 0
clip2Display.UseShaderReplacements = 0
clip2Display.ShaderReplacements = ''
clip2Display.NonlinearSubdivisionLevel = 1
clip2Display.UseDataPartitions = 0
clip2Display.OSPRayUseScaleArray = 0
clip2Display.OSPRayScaleArray = 'p'
clip2Display.OSPRayScaleFunction = 'PiecewiseFunction'
clip2Display.OSPRayMaterial = 'None'
clip2Display.Orient = 0
clip2Display.OrientationMode = 'Direction'
clip2Display.SelectOrientationVectors = 'U'
clip2Display.Scaling = 0
clip2Display.ScaleMode = 'No Data Scaling Off'
clip2Display.ScaleFactor = 6.360078987199813e-05
clip2Display.SelectScaleArray = 'p'
clip2Display.GlyphType = 'Arrow'
clip2Display.UseGlyphTable = 0
clip2Display.GlyphTableIndexArray = 'p'
clip2Display.UseCompositeGlyphTable = 0
clip2Display.UseGlyphCullingAndLOD = 0
clip2Display.LODValues = []
clip2Display.ColorByLODIndex = 0
clip2Display.GaussianRadius = 3.1800394935999065e-06
clip2Display.ShaderPreset = 'Sphere'
clip2Display.CustomTriangleScale = 3
clip2Display.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
clip2Display.Emissive = 0
clip2Display.ScaleByArray = 0
clip2Display.SetScaleArray = ['POINTS', 'p']
clip2Display.ScaleArrayComponent = ''
clip2Display.UseScaleFunction = 1
clip2Display.ScaleTransferFunction = 'PiecewiseFunction'
clip2Display.OpacityByArray = 0
clip2Display.OpacityArray = ['POINTS', 'p']
clip2Display.OpacityArrayComponent = ''
clip2Display.OpacityTransferFunction = 'PiecewiseFunction'
clip2Display.DataAxesGrid = 'GridAxesRepresentation'
clip2Display.SelectionCellLabelBold = 0
clip2Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
clip2Display.SelectionCellLabelFontFamily = 'Arial'
clip2Display.SelectionCellLabelFontFile = ''
clip2Display.SelectionCellLabelFontSize = 18
clip2Display.SelectionCellLabelItalic = 0
clip2Display.SelectionCellLabelJustification = 'Left'
clip2Display.SelectionCellLabelOpacity = 1.0
clip2Display.SelectionCellLabelShadow = 0
clip2Display.SelectionPointLabelBold = 0
clip2Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
clip2Display.SelectionPointLabelFontFamily = 'Arial'
clip2Display.SelectionPointLabelFontFile = ''
clip2Display.SelectionPointLabelFontSize = 18
clip2Display.SelectionPointLabelItalic = 0
clip2Display.SelectionPointLabelJustification = 'Left'
clip2Display.SelectionPointLabelOpacity = 1.0
clip2Display.SelectionPointLabelShadow = 0
clip2Display.PolarAxes = 'PolarAxesRepresentation'
clip2Display.ScalarOpacityFunction = pPWF
clip2Display.ScalarOpacityUnitDistance = 1.896498014614263e-05
clip2Display.ExtractedBlockIndex = 1
clip2Display.SelectMapper = 'Projected tetra'
clip2Display.SamplingDimensions = [128, 128, 128]
clip2Display.UseFloatingPointFrameBuffer = 1

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
clip2Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
clip2Display.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
clip2Display.GlyphType.TipResolution = 6
clip2Display.GlyphType.TipRadius = 0.1
clip2Display.GlyphType.TipLength = 0.35
clip2Display.GlyphType.ShaftResolution = 6
clip2Display.GlyphType.ShaftRadius = 0.03
clip2Display.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
clip2Display.ScaleTransferFunction.Points = [-19480.748046875, 0.0, 0.5, 0.0, 272775.75, 1.0, 0.5, 0.0]
clip2Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
clip2Display.OpacityTransferFunction.Points = [-19480.748046875, 0.0, 0.5, 0.0, 272775.75, 1.0, 0.5, 0.0]
clip2Display.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
clip2Display.DataAxesGrid.XTitle = 'X Axis'
clip2Display.DataAxesGrid.YTitle = 'Y Axis'
clip2Display.DataAxesGrid.ZTitle = 'Z Axis'
clip2Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.XTitleFontFamily = 'Arial'
clip2Display.DataAxesGrid.XTitleFontFile = ''
clip2Display.DataAxesGrid.XTitleBold = 0
clip2Display.DataAxesGrid.XTitleItalic = 0
clip2Display.DataAxesGrid.XTitleFontSize = 12
clip2Display.DataAxesGrid.XTitleShadow = 0
clip2Display.DataAxesGrid.XTitleOpacity = 1.0
clip2Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.YTitleFontFamily = 'Arial'
clip2Display.DataAxesGrid.YTitleFontFile = ''
clip2Display.DataAxesGrid.YTitleBold = 0
clip2Display.DataAxesGrid.YTitleItalic = 0
clip2Display.DataAxesGrid.YTitleFontSize = 12
clip2Display.DataAxesGrid.YTitleShadow = 0
clip2Display.DataAxesGrid.YTitleOpacity = 1.0
clip2Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.ZTitleFontFamily = 'Arial'
clip2Display.DataAxesGrid.ZTitleFontFile = ''
clip2Display.DataAxesGrid.ZTitleBold = 0
clip2Display.DataAxesGrid.ZTitleItalic = 0
clip2Display.DataAxesGrid.ZTitleFontSize = 12
clip2Display.DataAxesGrid.ZTitleShadow = 0
clip2Display.DataAxesGrid.ZTitleOpacity = 1.0
clip2Display.DataAxesGrid.FacesToRender = 63
clip2Display.DataAxesGrid.CullBackface = 0
clip2Display.DataAxesGrid.CullFrontface = 1
clip2Display.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
clip2Display.DataAxesGrid.ShowGrid = 0
clip2Display.DataAxesGrid.ShowEdges = 1
clip2Display.DataAxesGrid.ShowTicks = 1
clip2Display.DataAxesGrid.LabelUniqueEdgesOnly = 1
clip2Display.DataAxesGrid.AxesToLabel = 63
clip2Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.XLabelFontFamily = 'Arial'
clip2Display.DataAxesGrid.XLabelFontFile = ''
clip2Display.DataAxesGrid.XLabelBold = 0
clip2Display.DataAxesGrid.XLabelItalic = 0
clip2Display.DataAxesGrid.XLabelFontSize = 12
clip2Display.DataAxesGrid.XLabelShadow = 0
clip2Display.DataAxesGrid.XLabelOpacity = 1.0
clip2Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.YLabelFontFamily = 'Arial'
clip2Display.DataAxesGrid.YLabelFontFile = ''
clip2Display.DataAxesGrid.YLabelBold = 0
clip2Display.DataAxesGrid.YLabelItalic = 0
clip2Display.DataAxesGrid.YLabelFontSize = 12
clip2Display.DataAxesGrid.YLabelShadow = 0
clip2Display.DataAxesGrid.YLabelOpacity = 1.0
clip2Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
clip2Display.DataAxesGrid.ZLabelFontFamily = 'Arial'
clip2Display.DataAxesGrid.ZLabelFontFile = ''
clip2Display.DataAxesGrid.ZLabelBold = 0
clip2Display.DataAxesGrid.ZLabelItalic = 0
clip2Display.DataAxesGrid.ZLabelFontSize = 12
clip2Display.DataAxesGrid.ZLabelShadow = 0
clip2Display.DataAxesGrid.ZLabelOpacity = 1.0
clip2Display.DataAxesGrid.XAxisNotation = 'Mixed'
clip2Display.DataAxesGrid.XAxisPrecision = 2
clip2Display.DataAxesGrid.XAxisUseCustomLabels = 0
clip2Display.DataAxesGrid.XAxisLabels = []
clip2Display.DataAxesGrid.YAxisNotation = 'Mixed'
clip2Display.DataAxesGrid.YAxisPrecision = 2
clip2Display.DataAxesGrid.YAxisUseCustomLabels = 0
clip2Display.DataAxesGrid.YAxisLabels = []
clip2Display.DataAxesGrid.ZAxisNotation = 'Mixed'
clip2Display.DataAxesGrid.ZAxisPrecision = 2
clip2Display.DataAxesGrid.ZAxisUseCustomLabels = 0
clip2Display.DataAxesGrid.ZAxisLabels = []
clip2Display.DataAxesGrid.UseCustomBounds = 0
clip2Display.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
clip2Display.PolarAxes.Visibility = 0
clip2Display.PolarAxes.Translation = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.Scale = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.EnableCustomBounds = [0, 0, 0]
clip2Display.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
clip2Display.PolarAxes.EnableCustomRange = 0
clip2Display.PolarAxes.CustomRange = [0.0, 1.0]
clip2Display.PolarAxes.PolarAxisVisibility = 1
clip2Display.PolarAxes.RadialAxesVisibility = 1
clip2Display.PolarAxes.DrawRadialGridlines = 1
clip2Display.PolarAxes.PolarArcsVisibility = 1
clip2Display.PolarAxes.DrawPolarArcsGridlines = 1
clip2Display.PolarAxes.NumberOfRadialAxes = 0
clip2Display.PolarAxes.AutoSubdividePolarAxis = 1
clip2Display.PolarAxes.NumberOfPolarAxis = 0
clip2Display.PolarAxes.MinimumRadius = 0.0
clip2Display.PolarAxes.MinimumAngle = 0.0
clip2Display.PolarAxes.MaximumAngle = 90.0
clip2Display.PolarAxes.RadialAxesOriginToPolarAxis = 1
clip2Display.PolarAxes.Ratio = 1.0
clip2Display.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
clip2Display.PolarAxes.PolarAxisTitleVisibility = 1
clip2Display.PolarAxes.PolarAxisTitle = 'Radial Distance'
clip2Display.PolarAxes.PolarAxisTitleLocation = 'Bottom'
clip2Display.PolarAxes.PolarLabelVisibility = 1
clip2Display.PolarAxes.PolarLabelFormat = '%-#6.3g'
clip2Display.PolarAxes.PolarLabelExponentLocation = 'Labels'
clip2Display.PolarAxes.RadialLabelVisibility = 1
clip2Display.PolarAxes.RadialLabelFormat = '%-#3.1f'
clip2Display.PolarAxes.RadialLabelLocation = 'Bottom'
clip2Display.PolarAxes.RadialUnitsVisibility = 1
clip2Display.PolarAxes.ScreenSize = 10.0
clip2Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.PolarAxisTitleOpacity = 1.0
clip2Display.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
clip2Display.PolarAxes.PolarAxisTitleFontFile = ''
clip2Display.PolarAxes.PolarAxisTitleBold = 0
clip2Display.PolarAxes.PolarAxisTitleItalic = 0
clip2Display.PolarAxes.PolarAxisTitleShadow = 0
clip2Display.PolarAxes.PolarAxisTitleFontSize = 12
clip2Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.PolarAxisLabelOpacity = 1.0
clip2Display.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
clip2Display.PolarAxes.PolarAxisLabelFontFile = ''
clip2Display.PolarAxes.PolarAxisLabelBold = 0
clip2Display.PolarAxes.PolarAxisLabelItalic = 0
clip2Display.PolarAxes.PolarAxisLabelShadow = 0
clip2Display.PolarAxes.PolarAxisLabelFontSize = 12
clip2Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.LastRadialAxisTextOpacity = 1.0
clip2Display.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
clip2Display.PolarAxes.LastRadialAxisTextFontFile = ''
clip2Display.PolarAxes.LastRadialAxisTextBold = 0
clip2Display.PolarAxes.LastRadialAxisTextItalic = 0
clip2Display.PolarAxes.LastRadialAxisTextShadow = 0
clip2Display.PolarAxes.LastRadialAxisTextFontSize = 12
clip2Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
clip2Display.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
clip2Display.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
clip2Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''
clip2Display.PolarAxes.SecondaryRadialAxesTextBold = 0
clip2Display.PolarAxes.SecondaryRadialAxesTextItalic = 0
clip2Display.PolarAxes.SecondaryRadialAxesTextShadow = 0
clip2Display.PolarAxes.SecondaryRadialAxesTextFontSize = 12
clip2Display.PolarAxes.EnableDistanceLOD = 1
clip2Display.PolarAxes.DistanceLODThreshold = 0.7
clip2Display.PolarAxes.EnableViewAngleLOD = 1
clip2Display.PolarAxes.ViewAngleLODThreshold = 0.7
clip2Display.PolarAxes.SmallestVisiblePolarAngle = 0.5
clip2Display.PolarAxes.PolarTicksVisibility = 1
clip2Display.PolarAxes.ArcTicksOriginToPolarAxis = 1
clip2Display.PolarAxes.TickLocation = 'Both'
clip2Display.PolarAxes.AxisTickVisibility = 1
clip2Display.PolarAxes.AxisMinorTickVisibility = 0
clip2Display.PolarAxes.ArcTickVisibility = 1
clip2Display.PolarAxes.ArcMinorTickVisibility = 0
clip2Display.PolarAxes.DeltaAngleMajor = 10.0
clip2Display.PolarAxes.DeltaAngleMinor = 5.0
clip2Display.PolarAxes.PolarAxisMajorTickSize = 0.0
clip2Display.PolarAxes.PolarAxisTickRatioSize = 0.3
clip2Display.PolarAxes.PolarAxisMajorTickThickness = 1.0
clip2Display.PolarAxes.PolarAxisTickRatioThickness = 0.5
clip2Display.PolarAxes.LastRadialAxisMajorTickSize = 0.0
clip2Display.PolarAxes.LastRadialAxisTickRatioSize = 0.3
clip2Display.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
clip2Display.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
clip2Display.PolarAxes.ArcMajorTickSize = 0.0
clip2Display.PolarAxes.ArcTickRatioSize = 0.3
clip2Display.PolarAxes.ArcMajorTickThickness = 1.0
clip2Display.PolarAxes.ArcTickRatioThickness = 0.5
clip2Display.PolarAxes.Use2DMode = 0
clip2Display.PolarAxes.UseLogAxis = 0

# hide data in view
Hide(clip1, renderView1)

# show color bar/color legend
clip2Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# create a new 'Clip'
clip3 = Clip(Input=clip2)
clip3.ClipType = 'Plane'
clip3.Scalars = ['POINTS', 'p']
clip3.Value = 126647.5009765625
clip3.Invert = 1
clip3.Crinkleclip = 0
clip3.Exact = 0

# init the 'Plane' selected for 'ClipType'
clip3.ClipType.Origin = [9.799966210266575e-05, 0.0003980009787483141, 0.00011000034282915294]
clip3.ClipType.Normal = [1.0, 0.0, 0.0]
clip3.ClipType.Offset = 0.0

# Properties modified on clip3
clip3.ClipType = 'Scalar'
clip3.Scalars = ['POINTS', 'alpha.material']
clip3.Value = 0.9999
clip3.Invert = 0

# show data in view
clip3Display = Show(clip3, renderView1)

# trace defaults for the display properties.
clip3Display.Representation = 'Surface'
clip3Display.AmbientColor = [1.0, 1.0, 1.0]
clip3Display.ColorArrayName = ['POINTS', 'p']
clip3Display.DiffuseColor = [1.0, 1.0, 1.0]
clip3Display.LookupTable = pLUT
clip3Display.MapScalars = 1
clip3Display.MultiComponentsMapping = 0
clip3Display.InterpolateScalarsBeforeMapping = 1
clip3Display.Opacity = 1.0
clip3Display.PointSize = 2.0
clip3Display.LineWidth = 1.0
clip3Display.RenderLinesAsTubes = 0
clip3Display.RenderPointsAsSpheres = 0
clip3Display.Interpolation = 'Gouraud'
clip3Display.Specular = 0.0
clip3Display.SpecularColor = [1.0, 1.0, 1.0]
clip3Display.SpecularPower = 100.0
clip3Display.Luminosity = 0.0
clip3Display.Ambient = 0.0
clip3Display.Diffuse = 1.0
clip3Display.EdgeColor = [0.0, 0.0, 0.5]
clip3Display.BackfaceRepresentation = 'Follow Frontface'
clip3Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
clip3Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
clip3Display.BackfaceOpacity = 1.0
clip3Display.Position = [0.0, 0.0, 0.0]
clip3Display.Scale = [1.0, 1.0, 1.0]
clip3Display.Orientation = [0.0, 0.0, 0.0]
clip3Display.Origin = [0.0, 0.0, 0.0]
clip3Display.Pickable = 1
clip3Display.Texture = None
clip3Display.Triangulate = 0
clip3Display.UseShaderReplacements = 0
clip3Display.ShaderReplacements = ''
clip3Display.NonlinearSubdivisionLevel = 1
clip3Display.UseDataPartitions = 0
clip3Display.OSPRayUseScaleArray = 0
clip3Display.OSPRayScaleArray = 'p'
clip3Display.OSPRayScaleFunction = 'PiecewiseFunction'
clip3Display.OSPRayMaterial = 'None'
clip3Display.Orient = 0
clip3Display.OrientationMode = 'Direction'
clip3Display.SelectOrientationVectors = 'U'
clip3Display.Scaling = 0
clip3Display.ScaleMode = 'No Data Scaling Off'
clip3Display.ScaleFactor = 6.16041972534731e-05
clip3Display.SelectScaleArray = 'p'
clip3Display.GlyphType = 'Arrow'
clip3Display.UseGlyphTable = 0
clip3Display.GlyphTableIndexArray = 'p'
clip3Display.UseCompositeGlyphTable = 0
clip3Display.UseGlyphCullingAndLOD = 0
clip3Display.LODValues = []
clip3Display.ColorByLODIndex = 0
clip3Display.GaussianRadius = 3.080209862673655e-06
clip3Display.ShaderPreset = 'Sphere'
clip3Display.CustomTriangleScale = 3
clip3Display.CustomShader = """ // This custom shader code define a gaussian blur
 // Please take a look into vtkSMPointGaussianRepresentation.cxx
 // for other custom shader examples
 //VTK::Color::Impl
   float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
   float gaussian = exp(-0.5*dist2);
   opacity = opacity*gaussian;
"""
clip3Display.Emissive = 0
clip3Display.ScaleByArray = 0
clip3Display.SetScaleArray = ['POINTS', 'p']
clip3Display.ScaleArrayComponent = ''
clip3Display.UseScaleFunction = 1
clip3Display.ScaleTransferFunction = 'PiecewiseFunction'
clip3Display.OpacityByArray = 0
clip3Display.OpacityArray = ['POINTS', 'p']
clip3Display.OpacityArrayComponent = ''
clip3Display.OpacityTransferFunction = 'PiecewiseFunction'
clip3Display.DataAxesGrid = 'GridAxesRepresentation'
clip3Display.SelectionCellLabelBold = 0
clip3Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
clip3Display.SelectionCellLabelFontFamily = 'Arial'
clip3Display.SelectionCellLabelFontFile = ''
clip3Display.SelectionCellLabelFontSize = 18
clip3Display.SelectionCellLabelItalic = 0
clip3Display.SelectionCellLabelJustification = 'Left'
clip3Display.SelectionCellLabelOpacity = 1.0
clip3Display.SelectionCellLabelShadow = 0
clip3Display.SelectionPointLabelBold = 0
clip3Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
clip3Display.SelectionPointLabelFontFamily = 'Arial'
clip3Display.SelectionPointLabelFontFile = ''
clip3Display.SelectionPointLabelFontSize = 18
clip3Display.SelectionPointLabelItalic = 0
clip3Display.SelectionPointLabelJustification = 'Left'
clip3Display.SelectionPointLabelOpacity = 1.0
clip3Display.SelectionPointLabelShadow = 0
clip3Display.PolarAxes = 'PolarAxesRepresentation'
clip3Display.ScalarOpacityFunction = pPWF
clip3Display.ScalarOpacityUnitDistance = 1.9329480166064554e-05
clip3Display.ExtractedBlockIndex = 1
clip3Display.SelectMapper = 'Projected tetra'
clip3Display.SamplingDimensions = [128, 128, 128]
clip3Display.UseFloatingPointFrameBuffer = 1

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
clip3Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
clip3Display.OSPRayScaleFunction.UseLogScale = 0

# init the 'Arrow' selected for 'GlyphType'
clip3Display.GlyphType.TipResolution = 6
clip3Display.GlyphType.TipRadius = 0.1
clip3Display.GlyphType.TipLength = 0.35
clip3Display.GlyphType.ShaftResolution = 6
clip3Display.GlyphType.ShaftRadius = 0.03
clip3Display.GlyphType.Invert = 0

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
clip3Display.ScaleTransferFunction.Points = [3848.524658203125, 0.0, 0.5, 0.0, 158417.734375, 1.0, 0.5, 0.0]
clip3Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
clip3Display.OpacityTransferFunction.Points = [3848.524658203125, 0.0, 0.5, 0.0, 158417.734375, 1.0, 0.5, 0.0]
clip3Display.OpacityTransferFunction.UseLogScale = 0

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
clip3Display.DataAxesGrid.XTitle = 'X Axis'
clip3Display.DataAxesGrid.YTitle = 'Y Axis'
clip3Display.DataAxesGrid.ZTitle = 'Z Axis'
clip3Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.XTitleFontFamily = 'Arial'
clip3Display.DataAxesGrid.XTitleFontFile = ''
clip3Display.DataAxesGrid.XTitleBold = 0
clip3Display.DataAxesGrid.XTitleItalic = 0
clip3Display.DataAxesGrid.XTitleFontSize = 12
clip3Display.DataAxesGrid.XTitleShadow = 0
clip3Display.DataAxesGrid.XTitleOpacity = 1.0
clip3Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.YTitleFontFamily = 'Arial'
clip3Display.DataAxesGrid.YTitleFontFile = ''
clip3Display.DataAxesGrid.YTitleBold = 0
clip3Display.DataAxesGrid.YTitleItalic = 0
clip3Display.DataAxesGrid.YTitleFontSize = 12
clip3Display.DataAxesGrid.YTitleShadow = 0
clip3Display.DataAxesGrid.YTitleOpacity = 1.0
clip3Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.ZTitleFontFamily = 'Arial'
clip3Display.DataAxesGrid.ZTitleFontFile = ''
clip3Display.DataAxesGrid.ZTitleBold = 0
clip3Display.DataAxesGrid.ZTitleItalic = 0
clip3Display.DataAxesGrid.ZTitleFontSize = 12
clip3Display.DataAxesGrid.ZTitleShadow = 0
clip3Display.DataAxesGrid.ZTitleOpacity = 1.0
clip3Display.DataAxesGrid.FacesToRender = 63
clip3Display.DataAxesGrid.CullBackface = 0
clip3Display.DataAxesGrid.CullFrontface = 1
clip3Display.DataAxesGrid.GridColor = [1.0, 1.0, 1.0]
clip3Display.DataAxesGrid.ShowGrid = 0
clip3Display.DataAxesGrid.ShowEdges = 1
clip3Display.DataAxesGrid.ShowTicks = 1
clip3Display.DataAxesGrid.LabelUniqueEdgesOnly = 1
clip3Display.DataAxesGrid.AxesToLabel = 63
clip3Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.XLabelFontFamily = 'Arial'
clip3Display.DataAxesGrid.XLabelFontFile = ''
clip3Display.DataAxesGrid.XLabelBold = 0
clip3Display.DataAxesGrid.XLabelItalic = 0
clip3Display.DataAxesGrid.XLabelFontSize = 12
clip3Display.DataAxesGrid.XLabelShadow = 0
clip3Display.DataAxesGrid.XLabelOpacity = 1.0
clip3Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.YLabelFontFamily = 'Arial'
clip3Display.DataAxesGrid.YLabelFontFile = ''
clip3Display.DataAxesGrid.YLabelBold = 0
clip3Display.DataAxesGrid.YLabelItalic = 0
clip3Display.DataAxesGrid.YLabelFontSize = 12
clip3Display.DataAxesGrid.YLabelShadow = 0
clip3Display.DataAxesGrid.YLabelOpacity = 1.0
clip3Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
clip3Display.DataAxesGrid.ZLabelFontFamily = 'Arial'
clip3Display.DataAxesGrid.ZLabelFontFile = ''
clip3Display.DataAxesGrid.ZLabelBold = 0
clip3Display.DataAxesGrid.ZLabelItalic = 0
clip3Display.DataAxesGrid.ZLabelFontSize = 12
clip3Display.DataAxesGrid.ZLabelShadow = 0
clip3Display.DataAxesGrid.ZLabelOpacity = 1.0
clip3Display.DataAxesGrid.XAxisNotation = 'Mixed'
clip3Display.DataAxesGrid.XAxisPrecision = 2
clip3Display.DataAxesGrid.XAxisUseCustomLabels = 0
clip3Display.DataAxesGrid.XAxisLabels = []
clip3Display.DataAxesGrid.YAxisNotation = 'Mixed'
clip3Display.DataAxesGrid.YAxisPrecision = 2
clip3Display.DataAxesGrid.YAxisUseCustomLabels = 0
clip3Display.DataAxesGrid.YAxisLabels = []
clip3Display.DataAxesGrid.ZAxisNotation = 'Mixed'
clip3Display.DataAxesGrid.ZAxisPrecision = 2
clip3Display.DataAxesGrid.ZAxisUseCustomLabels = 0
clip3Display.DataAxesGrid.ZAxisLabels = []
clip3Display.DataAxesGrid.UseCustomBounds = 0
clip3Display.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
clip3Display.PolarAxes.Visibility = 0
clip3Display.PolarAxes.Translation = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.Scale = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.EnableCustomBounds = [0, 0, 0]
clip3Display.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
clip3Display.PolarAxes.EnableCustomRange = 0
clip3Display.PolarAxes.CustomRange = [0.0, 1.0]
clip3Display.PolarAxes.PolarAxisVisibility = 1
clip3Display.PolarAxes.RadialAxesVisibility = 1
clip3Display.PolarAxes.DrawRadialGridlines = 1
clip3Display.PolarAxes.PolarArcsVisibility = 1
clip3Display.PolarAxes.DrawPolarArcsGridlines = 1
clip3Display.PolarAxes.NumberOfRadialAxes = 0
clip3Display.PolarAxes.AutoSubdividePolarAxis = 1
clip3Display.PolarAxes.NumberOfPolarAxis = 0
clip3Display.PolarAxes.MinimumRadius = 0.0
clip3Display.PolarAxes.MinimumAngle = 0.0
clip3Display.PolarAxes.MaximumAngle = 90.0
clip3Display.PolarAxes.RadialAxesOriginToPolarAxis = 1
clip3Display.PolarAxes.Ratio = 1.0
clip3Display.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
clip3Display.PolarAxes.PolarAxisTitleVisibility = 1
clip3Display.PolarAxes.PolarAxisTitle = 'Radial Distance'
clip3Display.PolarAxes.PolarAxisTitleLocation = 'Bottom'
clip3Display.PolarAxes.PolarLabelVisibility = 1
clip3Display.PolarAxes.PolarLabelFormat = '%-#6.3g'
clip3Display.PolarAxes.PolarLabelExponentLocation = 'Labels'
clip3Display.PolarAxes.RadialLabelVisibility = 1
clip3Display.PolarAxes.RadialLabelFormat = '%-#3.1f'
clip3Display.PolarAxes.RadialLabelLocation = 'Bottom'
clip3Display.PolarAxes.RadialUnitsVisibility = 1
clip3Display.PolarAxes.ScreenSize = 10.0
clip3Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.PolarAxisTitleOpacity = 1.0
clip3Display.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
clip3Display.PolarAxes.PolarAxisTitleFontFile = ''
clip3Display.PolarAxes.PolarAxisTitleBold = 0
clip3Display.PolarAxes.PolarAxisTitleItalic = 0
clip3Display.PolarAxes.PolarAxisTitleShadow = 0
clip3Display.PolarAxes.PolarAxisTitleFontSize = 12
clip3Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.PolarAxisLabelOpacity = 1.0
clip3Display.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
clip3Display.PolarAxes.PolarAxisLabelFontFile = ''
clip3Display.PolarAxes.PolarAxisLabelBold = 0
clip3Display.PolarAxes.PolarAxisLabelItalic = 0
clip3Display.PolarAxes.PolarAxisLabelShadow = 0
clip3Display.PolarAxes.PolarAxisLabelFontSize = 12
clip3Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.LastRadialAxisTextOpacity = 1.0
clip3Display.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
clip3Display.PolarAxes.LastRadialAxisTextFontFile = ''
clip3Display.PolarAxes.LastRadialAxisTextBold = 0
clip3Display.PolarAxes.LastRadialAxisTextItalic = 0
clip3Display.PolarAxes.LastRadialAxisTextShadow = 0
clip3Display.PolarAxes.LastRadialAxisTextFontSize = 12
clip3Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
clip3Display.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
clip3Display.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
clip3Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''
clip3Display.PolarAxes.SecondaryRadialAxesTextBold = 0
clip3Display.PolarAxes.SecondaryRadialAxesTextItalic = 0
clip3Display.PolarAxes.SecondaryRadialAxesTextShadow = 0
clip3Display.PolarAxes.SecondaryRadialAxesTextFontSize = 12
clip3Display.PolarAxes.EnableDistanceLOD = 1
clip3Display.PolarAxes.DistanceLODThreshold = 0.7
clip3Display.PolarAxes.EnableViewAngleLOD = 1
clip3Display.PolarAxes.ViewAngleLODThreshold = 0.7
clip3Display.PolarAxes.SmallestVisiblePolarAngle = 0.5
clip3Display.PolarAxes.PolarTicksVisibility = 1
clip3Display.PolarAxes.ArcTicksOriginToPolarAxis = 1
clip3Display.PolarAxes.TickLocation = 'Both'
clip3Display.PolarAxes.AxisTickVisibility = 1
clip3Display.PolarAxes.AxisMinorTickVisibility = 0
clip3Display.PolarAxes.ArcTickVisibility = 1
clip3Display.PolarAxes.ArcMinorTickVisibility = 0
clip3Display.PolarAxes.DeltaAngleMajor = 10.0
clip3Display.PolarAxes.DeltaAngleMinor = 5.0
clip3Display.PolarAxes.PolarAxisMajorTickSize = 0.0
clip3Display.PolarAxes.PolarAxisTickRatioSize = 0.3
clip3Display.PolarAxes.PolarAxisMajorTickThickness = 1.0
clip3Display.PolarAxes.PolarAxisTickRatioThickness = 0.5
clip3Display.PolarAxes.LastRadialAxisMajorTickSize = 0.0
clip3Display.PolarAxes.LastRadialAxisTickRatioSize = 0.3
clip3Display.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
clip3Display.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
clip3Display.PolarAxes.ArcMajorTickSize = 0.0
clip3Display.PolarAxes.ArcTickRatioSize = 0.3
clip3Display.PolarAxes.ArcMajorTickThickness = 1.0
clip3Display.PolarAxes.ArcTickRatioThickness = 0.5
clip3Display.PolarAxes.Use2DMode = 0
clip3Display.PolarAxes.UseLogAxis = 0

# hide data in view
Hide(clip2, renderView1)

# show color bar/color legend
clip3Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(clip3Display, ('POINTS', 'T'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
clip3Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
clip3Display.SetScalarBarVisibility(renderView1, True)

animationScene1.GoToLast()

# reset view to fit data
renderView1.ResetCamera()

# create a new 'Slice'
slice1 = Slice(Input=clip3)
slice1.SliceType = 'Plane'
slice1.Crinkleslice = 0
slice1.Triangulatetheslice = 1
slice1.Mergeduplicatedpointsintheslice = 1
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [9.800020961847622e-05, 0.0003880201111314818, 0.00010999884398188442]
slice1.SliceType.Normal = [1.0, 0.0, 0.0]
slice1.SliceType.Offset = 0.0

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
slice1Display.ScaleFactor = 6.060293671907857e-05
slice1Display.SelectScaleArray = 'p'
slice1Display.GlyphType = 'Arrow'
slice1Display.UseGlyphTable = 0
slice1Display.GlyphTableIndexArray = 'p'
slice1Display.UseCompositeGlyphTable = 0
slice1Display.UseGlyphCullingAndLOD = 0
slice1Display.LODValues = []
slice1Display.ColorByLODIndex = 0
slice1Display.GaussianRadius = 3.0301468359539287e-06
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
slice1Display.ScaleTransferFunction.Points = [39722.33203125, 0.0, 0.5, 0.0, 157800.5, 1.0, 0.5, 0.0]
slice1Display.ScaleTransferFunction.UseLogScale = 0

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice1Display.OpacityTransferFunction.Points = [39722.33203125, 0.0, 0.5, 0.0, 157800.5, 1.0, 0.5, 0.0]
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
slice1Display.DataAxesGrid.UseCustomBounds = 0
slice1Display.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

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
Hide(clip3, renderView1)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

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
spreadSheetView1.InvertOrder = 0
spreadSheetView1.BlockSize = 1024
spreadSheetView1.HiddenColumnLabels = []
spreadSheetView1.FieldAssociation = 'Point Data'

# show data in view
slice1Display = Show(slice1, spreadSheetView1)

# trace defaults for the display properties.
slice1Display.CompositeDataSetIndex = [0]

# get layout
layout1 = GetLayoutByName("Layout #1")

# assign view to a particular cell in the layout
AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=0)

# export view
ExportView('./meltpool_forcontinuity.csv', view=spreadSheetView1)