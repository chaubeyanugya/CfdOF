# CfdOF/Solve/CfdTurbulenceCalculator.py

import FreeCAD
import math
import os

TURBULENCE_CALC_DEFAULTS = {
    "ReferenceVelocity": 1.0,
    "CharacteristicLength": 1.0,
    "TurbulenceIntensity": 0.05,
    "Cmu": 0.09,
    "TurbulentKineticEnergy": 0.0,
    "TurbulentDissipationRate": 0.0,
    "SpecificDissipationRate": 0.0,
}

def makeCfdTurbulenceCalculator(name="TurbulenceCalculator"):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    CfdTurbulenceCalculator(obj)
    if FreeCAD.GuiUp:
        from CfdOF.Solve.TaskPanelCfdTurbulenceCalculator import ViewProviderCfdTurbulenceCalculator
        ViewProviderCfdTurbulenceCalculator(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class CfdTurbulenceCalculator:
    def __init__(self, obj):
        obj.Proxy = self
        self.initProperties(obj)

    def initProperties(self, obj):
        addObjectProperty = obj.addProperty
        addObjectProperty("App::PropertyFloat", "ReferenceVelocity", "TurbulenceInputs", "Reference flow velocity (m/s)")
        addObjectProperty("App::PropertyFloat", "CharacteristicLength", "TurbulenceInputs", "Characteristic geometry length (m)")
        addObjectProperty("App::PropertyFloat", "TurbulenceIntensity", "TurbulenceInputs", "Turbulence intensity (fraction, e.g. 0.05 = 5%)")
        addObjectProperty("App::PropertyFloat", "Cmu", "TurbulenceInputs", "Turbulence model constant Cmu (default 0.09)")
        addObjectProperty("App::PropertyFloat", "TurbulentKineticEnergy", "TurbulenceOutputs", "Computed k (m2/s2)")
        addObjectProperty("App::PropertyFloat", "TurbulentDissipationRate", "TurbulenceOutputs", "Computed epsilon (m2/s3)")
        addObjectProperty("App::PropertyFloat", "SpecificDissipationRate", "TurbulenceOutputs", "Computed omega (1/s)")

        for key, val in TURBULENCE_CALC_DEFAULTS.items():
            if hasattr(obj, key):
                setattr(obj, key, val)

    def compute(self, obj):
        U = obj.ReferenceVelocity
        L = obj.CharacteristicLength
        I = obj.TurbulenceIntensity
        Cmu = obj.Cmu

        k = 1.5 * (U * I) ** 2
        epsilon = (Cmu ** 0.75) * (k ** 1.5) / L
        omega = (k ** 0.5) / ((Cmu ** 0.25) * L)

        obj.TurbulentKineticEnergy = k
        obj.TurbulentDissipationRate = epsilon
        obj.SpecificDissipationRate = omega
        return k, epsilon, omega

    def execute(self, obj):
        self.compute(obj)


class CommandCfdTurbulenceCalculator:
    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), "..", "..", "Gui", "Icons", "cfd.svg"),
            'MenuText': "Turbulence Parameter Calculator",
            'ToolTip': "Calculate k, epsilon, omega from flow velocity and geometry"
        }

    def IsActive(self):
        from CfdOF import CfdTools
        return CfdTools.getActiveAnalysis() is not None

    def Activated(self):
        from CfdOF import CfdTools
        FreeCAD.ActiveDocument.openTransaction("Create TurbulenceCalculator")
        analysis = CfdTools.getActiveAnalysis()
        obj = makeCfdTurbulenceCalculator()
        analysis.addObject(obj)
        FreeCAD.ActiveDocument.recompute()
        if FreeCAD.GuiUp:
            import FreeCADGui
            FreeCADGui.ActiveDocument.setEdit(obj.Name)