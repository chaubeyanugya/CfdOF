# CfdOF/Solve/TaskPanelCfdTurbulenceCalculator.py

import FreeCAD
import FreeCADGui
import os
from PySide2 import QtCore, QtWidgets, QtUiTools

UI_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Gui",
                       "TaskPanelCfdTurbulenceCalculator.ui")

class TaskPanelCfdTurbulenceCalculator:
    def __init__(self, obj):
        self.obj = obj
        # Load UI file correctly
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(UI_PATH)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.form = loader.load(ui_file)
        ui_file.close()
        self._connectSignals()
        self._loadFromObject()

    def _connectSignals(self):
        self.form.pb_Calculate.clicked.connect(self.calculate)
        self.form.pb_ApplyToCase.clicked.connect(self.applyToCase)

    def _loadFromObject(self):
        obj = self.obj
        self.form.if_ReferenceVelocity.setValue(obj.ReferenceVelocity)
        self.form.if_CharacteristicLength.setValue(obj.CharacteristicLength)
        self.form.if_TurbulenceIntensity.setValue(obj.TurbulenceIntensity)
        self.form.if_Cmu.setValue(obj.Cmu)

    def calculate(self):
        obj = self.obj
        obj.ReferenceVelocity = self.form.if_ReferenceVelocity.value()
        obj.CharacteristicLength = self.form.if_CharacteristicLength.value()
        obj.TurbulenceIntensity = self.form.if_TurbulenceIntensity.value()
        obj.Cmu = self.form.if_Cmu.value()

        k, epsilon, omega = obj.Proxy.compute(obj)

        self.form.le_k.setText(f"{k:.6e}")
        self.form.le_epsilon.setText(f"{epsilon:.6e}")
        self.form.le_omega.setText(f"{omega:.6e}")

        FreeCAD.ActiveDocument.recompute()

    def applyToCase(self):
        from CfdOF import CfdTools

        init_obj = CfdTools.getInitialConditions(CfdTools.getActiveAnalysis())
        if init_obj is None:
            QtWidgets.QMessageBox.warning(
                None, "No Initialisation Object",
                "Please create an Initialise Flow Field object first.")
            return

        obj = self.obj
        FreeCAD.Console.PrintMessage(
            f"Turbulence values applied: k={obj.TurbulentKineticEnergy:.4e}, "
            f"epsilon={obj.TurbulentDissipationRate:.4e}, "
            f"omega={obj.SpecificDissipationRate:.4e}\n")
        FreeCAD.ActiveDocument.recompute()

    def accept(self):
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def reject(self):
        FreeCADGui.ActiveDocument.resetEdit()
        return True


class ViewProviderCfdTurbulenceCalculator:
    def __init__(self, vobj):
        vobj.Proxy = self

    def setEdit(self, vobj, mode):
        task = TaskPanelCfdTurbulenceCalculator(vobj.Object)
        FreeCADGui.Control.showDialog(task)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return True

    def getIcon(self):
        # Reuse existing cfd.svg to avoid missing icon error
        return os.path.join(os.path.dirname(__file__), "..", "..",
                            "Gui", "Icons", "cfd.svg")