# CfdOF/Solve/CfdSolverConfig.py

import FreeCAD

def makeCfdSolverConfig(name="CfdSolverConfig"):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    CfdSolverConfig(obj)
    return obj

class CfdSolverConfig:
    # --- fvSchemes ---
    DDTSCHEME_NAMES    = ["Euler", "backward", "CrankNicolson", "steadyState"]
    GRADSCHEME_NAMES   = ["Gauss linear", "leastSquares", "cellLimited Gauss linear 1"]
    DIVSCHEME_NAMES    = ["Gauss linearUpwind grad(U)", "Gauss upwind", "Gauss linear"]
    LAPSCHEME_NAMES    = ["Gauss linear corrected", "Gauss linear limited corrected 0.5"]
    INTERPSCHEME_NAMES = ["linear", "linearUpwind", "cubic"]

    # --- fvSolution pressure solvers ---
    PSOLVER_NAMES      = ["GAMG", "PCG", "smoothSolver"]
    # --- fvSolution velocity/turbulence solvers ---
    USOLVER_NAMES      = ["smoothSolver", "PBiCGStab", "PBiCG"]
    # --- algorithm ---
    ALGORITHM_NAMES    = ["SIMPLE", "PIMPLE", "PISO"]

    def __init__(self, obj):
        obj.Proxy = self
        self.initProperties(obj)

    def initProperties(self, obj):
        addObjectProperty = obj.addProperty

        # fvSchemes
        addObjectProperty("App::PropertyEnumeration", "DdtScheme",    "fvSchemes", "Time scheme")
        addObjectProperty("App::PropertyEnumeration", "GradScheme",   "fvSchemes", "Gradient scheme")
        addObjectProperty("App::PropertyEnumeration", "DivScheme",    "fvSchemes", "Divergence scheme")
        addObjectProperty("App::PropertyEnumeration", "LapScheme",    "fvSchemes", "Laplacian scheme")
        addObjectProperty("App::PropertyEnumeration", "InterpScheme", "fvSchemes", "Interpolation scheme")

        obj.DdtScheme    = self.DDTSCHEME_NAMES
        obj.GradScheme   = self.GRADSCHEME_NAMES
        obj.DivScheme    = self.DIVSCHEME_NAMES
        obj.LapScheme    = self.LAPSCHEME_NAMES
        obj.InterpScheme = self.INTERPSCHEME_NAMES

        # fvSolution
        addObjectProperty("App::PropertyEnumeration", "PressureSolver",   "fvSolution", "Pressure linear solver")
        addObjectProperty("App::PropertyEnumeration", "VelocitySolver",   "fvSolution", "Velocity linear solver")
        addObjectProperty("App::PropertyEnumeration", "TurbSolver",       "fvSolution", "Turbulence variable solver")
        addObjectProperty("App::PropertyFloat",       "PTolerance",       "fvSolution", "Pressure solver tolerance")
        addObjectProperty("App::PropertyFloat",       "UTolerance",       "fvSolution", "Velocity solver tolerance")
        addObjectProperty("App::PropertyFloat",       "RelaxP",           "fvSolution", "Pressure relaxation factor")
        addObjectProperty("App::PropertyFloat",       "RelaxU",           "fvSolution", "Velocity relaxation factor")
        addObjectProperty("App::PropertyEnumeration", "Algorithm",        "fvSolution", "Pressure-velocity algorithm")
        addObjectProperty("App::PropertyInteger",     "NOuterCorrectors", "fvSolution", "PIMPLE outer correctors")
        addObjectProperty("App::PropertyInteger",     "NCorrectors",      "fvSolution", "PIMPLE/PISO inner correctors")

        obj.PressureSolver   = self.PSOLVER_NAMES
        obj.VelocitySolver   = self.USOLVER_NAMES
        obj.TurbSolver       = self.USOLVER_NAMES
        obj.PTolerance       = 1e-6
        obj.UTolerance       = 1e-5
        obj.RelaxP           = 0.3
        obj.RelaxU           = 0.7
        obj.Algorithm        = self.ALGORITHM_NAMES
        obj.NOuterCorrectors = 50
        obj.NCorrectors      = 2

    def onDocumentRestored(self, obj):
        self.initProperties(obj)