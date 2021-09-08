# -*- coding: utf-8 -*-

# Macro Begin: +++++++++++++++++++++++++++++++++++++++++++++++++
import os
import FreeCAD
import CfdAnalysis
import CfdTools
import CfdPhysicsSelection
import CfdFluidMaterial
import CfdInitialiseFlowField
import CfdSolverFoam
import CfdMesh
import CfdMeshTools
import CfdFluidBoundary
import CfdCaseWriterFoam
from CfdConsoleProcess import CfdConsoleProcess
import CfdMeshRefinement
import csv

with open('SSInputs', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
           line_count += 1

cwd = os.getcwd()
FreeCAD.open(cwd + "/Basic_Membrane.FCStd")
#App.setActiveDocument("Basic_Membrane")
#App.ActiveDocument=App.getDocument("Basic_Membrane")
#Gui.ActiveDocument=Gui.getDocument("Basic_Membrane")

App.ActiveDocument.Spreadsheet.set('B3', row['B3']) #SpacerRadius, mm
App.ActiveDocument.Spreadsheet.set('B4', row['B4']) #channelHeight, mm
App.ActiveDocument.Spreadsheet.set('B5', row['B5']) #channelLength, mm
App.ActiveDocument.Spreadsheet.set('B6', row['B6']) #SpacerOffsetX, mm
App.ActiveDocument.Spreadsheet.set('B7', row['B7']) #channelWidth, mm
App.ActiveDocument.recompute()
#Gui.activateWorkbench("CfdOFWorkbench")

analysis = CfdAnalysis.makeCfdAnalysis('CfdAnalysis')
CfdTools.setActiveAnalysis(analysis)
analysis.addObject(CfdPhysicsSelection.makeCfdPhysicsSelection())
analysis.addObject(CfdFluidMaterial.makeCfdFluidMaterial('FluidProperties'))
analysis.addObject(CfdInitialiseFlowField.makeCfdInitialFlowField())
analysis.addObject(CfdSolverFoam.makeCfdSolverFoam())
FreeCAD.getDocument("Basic_Membrane").getObject("CfdAnalysis").OutputPath = cwd

mesh = CfdMesh.makeCfdMesh('Cut_Mesh')
App.ActiveDocument.ActiveObject.Part = App.ActiveDocument.Cut
CfdTools.getActiveAnalysis().addObject(App.ActiveDocument.ActiveObject)

FreeCAD.ActiveDocument.Cut_Mesh.CharacteristicLengthMax = '0.65 mm'
FreeCAD.ActiveDocument.Cut_Mesh.MeshUtility = 'snappyHexMesh'
FreeCAD.ActiveDocument.Cut_Mesh.ElementDimension = '3D'
FreeCAD.ActiveDocument.Cut_Mesh.CellsBetweenLevels = 3
FreeCAD.ActiveDocument.Cut_Mesh.EdgeRefinement = 1.0
FreeCAD.ActiveDocument.Cut_Mesh.PointInMesh = {'x': '0 mm', 'y': '0 mm', 'z': '0 mm'}

CfdMeshRefinement.makeCfdMeshRefinement(App.ActiveDocument.Cut_Mesh)
referenceList = []
referenceList.append(('Cut','Face8'))
referenceList.append(('Cut','Face7'))
FreeCAD.ActiveDocument.MeshRefinement.References = referenceList

FreeCAD.ActiveDocument.MeshRefinement.RelativeLength = 0.75
FreeCAD.ActiveDocument.MeshRefinement.RefinementThickness = '0 mm'
FreeCAD.ActiveDocument.MeshRefinement.NumberLayers = 1
FreeCAD.ActiveDocument.MeshRefinement.ExpansionRatio = 1.2
FreeCAD.ActiveDocument.MeshRefinement.FirstLayerHeight = '0 mm'
FreeCAD.ActiveDocument.MeshRefinement.RegionEdgeRefinement = 0.7499999999999998
FreeCAD.ActiveDocument.MeshRefinement.Baffle = False
FreeCAD.ActiveDocument.MeshRefinement.Internal = False

FreeCAD.ActiveDocument.Cut_Mesh.Proxy.cart_mesh = CfdMeshTools.CfdMeshTools(FreeCAD.ActiveDocument.Cut_Mesh)
cart_mesh = FreeCAD.ActiveDocument.Cut_Mesh.Proxy.cart_mesh
cart_mesh.processDimension()
cart_mesh.getFilePaths(CfdTools.getOutputPath(FreeCAD.ActiveDocument.CfdAnalysis))
cart_mesh.setupMeshCaseDir()
cart_mesh.processRefinements()
cart_mesh.writeMeshCase()
cart_mesh.writePartFile()
# Macro End: +++++++++++++++++++++++++++++++++++++++++++++++++
cmd0 = CfdTools.makeRunCommand('cp Allmesh2 meshCase', cwd, source_env=False)
env_vars = CfdTools.getRunEnvironment()
print("Executing: " + ' '.join(cmd0) + "\n")
copy_process0 = CfdConsoleProcess()
copy_process0.start(cmd0, env_vars=env_vars)
copy_process0.waitForFinished()
copy_process0.terminate()

cmd = CfdTools.makeRunCommand('./Allmesh2', cart_mesh.meshCaseDir, source_env=False)
print("Executing: " + ' '.join(cmd) + "\n")
mesh_process = CfdConsoleProcess()
mesh_process.start(cmd, env_vars=env_vars)
mesh_process.waitForFinished()
mesh_process.terminate()

#App.getDocument("Basic_Membrane").save()

obj = FreeCAD.ActiveDocument.PhysicsModel
obj.Time = 'Steady'
obj.Phase = 'Single'
obj.Flow = 'Incompressible'
obj.Thermal = 'None'
obj.Turbulence = 'Inviscid'
obj.gx = '0 mm/s^2'
obj.gy = '-9.8e+03 mm/s^2'
obj.gz = '0 mm/s^2'

FreeCAD.ActiveDocument.FluidProperties.Material = {'CardName': 'Seawater', 'AuthorAndLicense': '', 'Name': 'Seawater', 'Description': 'Sea water (30%) at 20 Degrees Celsius and 1 atm', 'Density': '1025 kg/m^3', 'DynamicViscosity': '1.07e-3 kg/m/s'}

CfdTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())

bc = FreeCAD.ActiveDocument.CfdFluidBoundary
bc.BoundaryType = 'wall'
bc.BoundarySubType = 'fixedWall'
bc.ThermalBoundaryType = 'fixedValue'
bc.VelocityIsCartesian = True
bc.Ux = '0 mm/s'
bc.Uy = '0 mm/s'
bc.Uz = '0 mm/s'
bc.VelocityMag = '0 mm/s'
bc.DirectionFace = ''
bc.ReverseNormal = False
bc.MassFlowRate = '0 kg/s'
bc.VolFlowRate = '0 mm^3/s'
bc.Pressure = '0 kg/(mm*s^2)'
bc.SlipRatio = '0 '
bc.Temperature = '290 K'
bc.HeatFlux = '0 kg/s^3'
bc.HeatTransferCoeff = '0 kg/(s^3*K)'
bc.TurbulenceInletSpecification = 'intensityAndLengthScale'
bc.TurbulentKineticEnergy = '10000 mm^2/s^2'
bc.SpecificDissipationRate = '57 deg/s'
bc.TurbulenceIntensity = '0.1 '
bc.TurbulenceLengthScale = '100 mm'
bc.VolumeFractions = {}
bc.PorousBaffleMethod = 'porousCoeff'
bc.PressureDropCoeff = '0 '
bc.ScreenWireDiameter = '0.2 mm'
bc.ScreenSpacing = '2 mm'
FreeCAD.ActiveDocument.CfdFluidBoundary.Label = 'wall'
FreeCAD.ActiveDocument.CfdFluidBoundary.References = []
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face5'))
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face1'))
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face7'))
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face8'))
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face4'))
FreeCAD.ActiveDocument.CfdFluidBoundary.References.append(('Cut', 'Face6'))
FreeCAD.ActiveDocument.recompute()

CfdTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())

bc = FreeCAD.ActiveDocument.CfdFluidBoundary001
bc.BoundaryType = 'inlet'
bc.BoundarySubType = 'uniformVelocityInlet'
bc.ThermalBoundaryType = 'fixedValue'
bc.VelocityIsCartesian = True
bc.Ux = '100 mm/s'
bc.Uy = '0 mm/s'
bc.Uz = '0 mm/s'
bc.VelocityMag = '0 mm/s'
bc.DirectionFace = ''
bc.ReverseNormal = True
bc.MassFlowRate = '0 kg/s'
bc.VolFlowRate = '0 mm^3/s'
bc.Pressure = '0 kg/(mm*s^2)'
bc.SlipRatio = '0 '
bc.Temperature = '290 K'
bc.HeatFlux = '0 kg/s^3'
bc.HeatTransferCoeff = '0 kg/(s^3*K)'
bc.TurbulenceInletSpecification = 'intensityAndLengthScale'
bc.TurbulentKineticEnergy = '10000 mm^2/s^2'
bc.SpecificDissipationRate = '57 deg/s'
bc.TurbulenceIntensity = '0.1 '
bc.TurbulenceLengthScale = '100 mm'
bc.VolumeFractions = {}
bc.PorousBaffleMethod = 'porousCoeff'
bc.PressureDropCoeff = '0 '
bc.ScreenWireDiameter = '0.2 mm'
bc.ScreenSpacing = '2 mm'
FreeCAD.ActiveDocument.CfdFluidBoundary001.Label = 'inlet'
FreeCAD.ActiveDocument.CfdFluidBoundary001.References = []
FreeCAD.ActiveDocument.CfdFluidBoundary001.References.append(('Cut', 'Face2'))
FreeCAD.ActiveDocument.recompute()

CfdTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())

bc = FreeCAD.ActiveDocument.CfdFluidBoundary002
bc.BoundaryType = 'outlet'
bc.BoundarySubType = 'staticPressureOutlet'
bc.ThermalBoundaryType = 'fixedValue'
bc.VelocityIsCartesian = True
bc.Ux = '0 mm/s'
bc.Uy = '0 mm/s'
bc.Uz = '0 mm/s'
bc.VelocityMag = '0 mm/s'
bc.DirectionFace = ''
bc.ReverseNormal = False
bc.MassFlowRate = '0 kg/s'
bc.VolFlowRate = '0 mm^3/s'
bc.Pressure = '0 kg/(mm*s^2)'
bc.SlipRatio = '0 '
bc.Temperature = '290 K'
bc.HeatFlux = '0 kg/s^3'
bc.HeatTransferCoeff = '0 kg/(s^3*K)'
bc.TurbulenceInletSpecification = 'intensityAndLengthScale'
bc.TurbulentKineticEnergy = '10000 mm^2/s^2'
bc.SpecificDissipationRate = '57 deg/s'
bc.TurbulenceIntensity = '0.1 '
bc.TurbulenceLengthScale = '100 mm'
bc.VolumeFractions = {}
bc.PorousBaffleMethod = 'porousCoeff'
bc.PressureDropCoeff = '0 '
bc.ScreenWireDiameter = '0.2 mm'
bc.ScreenSpacing = '2 mm'
FreeCAD.ActiveDocument.CfdFluidBoundary002.Label = 'outlet'
FreeCAD.ActiveDocument.CfdFluidBoundary002.References = []
FreeCAD.ActiveDocument.CfdFluidBoundary002.References.append(('Cut', 'Face3'))
FreeCAD.ActiveDocument.recompute()

init = FreeCAD.ActiveDocument.InitialiseFields
init.PotentialFlow = True
init.UseInletUValues = False
init.Ux = '0 mm/s'
init.Uy = '0 mm/s'
init.Uz = '0 mm/s'
init.UseOutletPValue = True
init.PotentialFlowP = False
init.Pressure = '0 kg/(mm*s^2)'
init.VolumeFractions = {}
init.UseInletTemperatureValue = False
init.Temperature = '290 K'
init.UseInletTurbulenceValues = False
init.omega = '57 deg/s'
init.k = '10000 mm^2/s^2'
init.BoundaryU = FreeCAD.ActiveDocument.CfdFluidBoundary001
init.BoundaryP = FreeCAD.ActiveDocument.CfdFluidBoundary002
init.BoundaryT = FreeCAD.ActiveDocument.CfdFluidBoundary001
init.BoundaryTurb = FreeCAD.ActiveDocument.CfdFluidBoundary001

writer = CfdCaseWriterFoam.CfdCaseWriterFoam(FreeCAD.ActiveDocument.CfdAnalysis)
writer.writeCase()

# Macro End: +++++++++++++++++++++++++++++++++++++++++++++++++
cmd2 = CfdTools.makeRunCommand('cp Allrun2 case', cwd, source_env=False)
print("Executing: " + ' '.join(cmd2) + "\n")
copy_process = CfdConsoleProcess()
copy_process.start(cmd2, env_vars=env_vars)
copy_process.waitForFinished()
copy_process.terminate()

cmd3 = CfdTools.makeRunCommand('./Allrun2', writer.case_folder, source_env=False)
print("Executing: " + ' '.join(cmd3) + "\n")
solve_process = CfdConsoleProcess()
solve_process.start(cmd3, env_vars=env_vars)
solve_process.waitForFinished()
solve_process.terminate()
print("Done")



