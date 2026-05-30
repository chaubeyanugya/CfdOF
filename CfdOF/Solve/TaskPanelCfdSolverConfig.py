# CfdOF/Solve/TaskPanelCfdSolverConfig.py

import os
import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets
from CfdOF.Solve.CfdSolverConfig import CfdSolverConfig, makeCfdSolverConfig
from CfdOF import CfdTools

# Correctly point to the top-level Gui/ folder in the CfdOF module
UI_PATH = os.path.join(CfdTools.getModulePath(), "Gui", "TaskPanelCfdSolverConfig.ui")

class TaskPanelCfdSolverConfig:
    def __init__(self, obj):
        self.obj = obj
        self.form = FreeCADGui.PySideUic.loadUi(UI_PATH)
        self._ensure_properties()  # <-- NEW: Make sure properties exist before doing anything else
        self._populateCombos()
        self._loadValues()
        self._connectSignals()

    def _ensure_properties(self):
        """Self-healing function: Injects missing properties into older FreeCAD project files."""
        o = self.obj
        if not hasattr(o, 'RelaxTurb'):
            o.addProperty("App::PropertyFloat", "RelaxTurb", "Solver Settings", "Turbulence relaxation factor").RelaxTurb = 1.0
        if not hasattr(o, 'TurbTolerance'):
            o.addProperty("App::PropertyFloat", "TurbTolerance", "Solver Settings", "Turbulence tolerance").TurbTolerance = 1e-5
        if not hasattr(o, 'NCorrectors'):
            o.addProperty("App::PropertyInteger", "NCorrectors", "Solver Settings", "Number of PIMPLE correctors").NCorrectors = 2
        if not hasattr(o, 'NNonOrthoCorrectors'):
            o.addProperty("App::PropertyInteger", "NNonOrthoCorrectors", "Solver Settings", "Number of non-orthogonal correctors").NNonOrthoCorrectors = 0
        if not hasattr(o, 'MomentumPredictor'):
            o.addProperty("App::PropertyBool", "MomentumPredictor", "Solver Settings", "Enable momentum predictor").MomentumPredictor = True

    def _populateCombos(self):
        cfg = CfdSolverConfig
        self.form.comboDdtScheme.addItems(cfg.DDTSCHEME_NAMES)
        self.form.comboGradScheme.addItems(cfg.GRADSCHEME_NAMES)
        self.form.comboDivScheme.addItems(cfg.DIVSCHEME_NAMES)
        self.form.comboLapScheme.addItems(cfg.LAPSCHEME_NAMES)
        self.form.comboInterpScheme.addItems(cfg.INTERPSCHEME_NAMES)
        
        self.form.comboPSolver.addItems(cfg.PSOLVER_NAMES)
        self.form.comboUSolver.addItems(cfg.USOLVER_NAMES)
        self.form.comboTurbSolver.addItems(cfg.USOLVER_NAMES) # Assuming Turb uses same solvers as U
        self.form.comboAlgorithm.addItems(cfg.ALGORITHM_NAMES)

    def _loadValues(self):
        o = self.obj
        self.form.comboDdtScheme.setCurrentText(getattr(o, 'DdtScheme', 'Euler'))
        self.form.comboGradScheme.setCurrentText(getattr(o, 'GradScheme', 'Gauss linear'))
        self.form.comboDivScheme.setCurrentText(getattr(o, 'DivScheme', 'bounded Gauss linearUpwind grad(U)'))
        self.form.comboLapScheme.setCurrentText(getattr(o, 'LapScheme', 'Gauss linear orthogonal'))
        self.form.comboInterpScheme.setCurrentText(getattr(o, 'InterpScheme', 'linear'))
        
        self.form.comboPSolver.setCurrentText(getattr(o, 'PressureSolver', 'GAMG'))
        self.form.comboUSolver.setCurrentText(getattr(o, 'VelocitySolver', 'smoothSolver'))
        self.form.comboTurbSolver.setCurrentText(getattr(o, 'TurbSolver', 'smoothSolver'))
        self.form.comboAlgorithm.setCurrentText(getattr(o, 'Algorithm', 'SIMPLE'))

        self.form.inputPTol.setText(str(getattr(o, 'PTolerance', 1e-6)))
        self.form.inputUTol.setText(str(getattr(o, 'UTolerance', 1e-5)))
        self.form.inputTurbTol.setText(str(getattr(o, 'TurbTolerance', 1e-5)))
        
        self.form.spinRelaxP.setValue(getattr(o, 'RelaxP', 0.3))
        self.form.spinRelaxU.setValue(getattr(o, 'RelaxU', 0.7))
        self.form.spinRelaxTurb.setValue(getattr(o, 'RelaxTurb', 1.0))
        
        self.form.spinNCorrectors.setValue(getattr(o, 'NCorrectors', 2))
        self.form.spinNNonOrtho.setValue(getattr(o, 'NNonOrthoCorrectors', 0))
        self.form.checkMomentum.setChecked(getattr(o, 'MomentumPredictor', True))

        # Search the FreeCAD document for the Physics Model
        physics_objs = [p for p in FreeCAD.ActiveDocument.Objects 
                        if hasattr(p, 'Proxy') and p.Proxy.__class__.__name__ == 'CfdPhysicsModel']
        
        if physics_objs:
            physics_model = physics_objs[0]
            # Check if the physics model is set to Transient
            is_transient = getattr(physics_model, 'Time', '') == 'Transient' or getattr(physics_model, 'Transient', False)
            
            # Enable the dropdown only if it is a transient simulation
            self.form.comboDdtScheme.setEnabled(is_transient)
            
            # If it is steady state, force the selection to steadyState
            if not is_transient:
                self.form.comboDdtScheme.setCurrentText("steadyState")
                setattr(self.obj, 'DdtScheme', "steadyState")

    def _connectSignals(self):
        # All changes live-update the object immediately
        self.form.comboDdtScheme.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'DdtScheme', v))
        self.form.comboGradScheme.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'GradScheme', v))
        self.form.comboDivScheme.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'DivScheme', v))
        self.form.comboLapScheme.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'LapScheme', v))
        self.form.comboInterpScheme.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'InterpScheme', v))
            
        self.form.comboPSolver.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'PressureSolver', v))
        self.form.comboUSolver.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'VelocitySolver', v))
        self.form.comboTurbSolver.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'TurbSolver', v))
        self.form.comboAlgorithm.currentTextChanged.connect(
            lambda v: setattr(self.obj, 'Algorithm', v))
            
        self.form.spinRelaxP.valueChanged.connect(
            lambda v: setattr(self.obj, 'RelaxP', v))
        self.form.spinRelaxU.valueChanged.connect(
            lambda v: setattr(self.obj, 'RelaxU', v))
        self.form.spinRelaxTurb.valueChanged.connect(
            lambda v: setattr(self.obj, 'RelaxTurb', v))
            
        self.form.spinNCorrectors.valueChanged.connect(
            lambda v: setattr(self.obj, 'NCorrectors', v))
        self.form.spinNNonOrtho.valueChanged.connect(
            lambda v: setattr(self.obj, 'NNonOrthoCorrectors', v))
        self.form.checkMomentum.toggled.connect(
            lambda v: setattr(self.obj, 'MomentumPredictor', v))

    def accept(self):
        # Tolerances read on accept (text fields)
        try:
            self.obj.PTolerance = float(self.form.inputPTol.text())
            self.obj.UTolerance = float(self.form.inputUTol.text())
            self.obj.TurbTolerance = float(self.form.inputTurbTol.text())
        except ValueError:
            pass
            
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()

    def reject(self):
        FreeCADGui.ActiveDocument.resetEdit()