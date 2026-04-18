# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the CfdOF addon.

################################################################################
#                                                                              #
#   Copyright (c) 2017-2018 Johan Heyns (CSIR) <jheyns@csir.co.za>             #
#   Copyright (c) 2017-2018 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          #
#   Copyright (c) 2017-2018 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        #
#   Copyright (c) 2019-2022 Oliver Oxtoby <oliveroxtoby@gmail.com>             #
#   Copyright (c) 2022 Jonathan Bergh <bergh.jonathan@gmail.com>               #
#                                                                              #
#   This program is free software; you can redistribute it and/or              #
#   modify it under the terms of the GNU Lesser General Public                 #
#   License as published by the Free Software Foundation; either               #
#   version 3 of the License, or (at your option) any later version.           #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       #
#                                                                              #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public License   #
#   along with this program; if not, write to the Free Software Foundation,    #
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.        #
#                                                                              #
################################################################################
print("week 4 running")
import os
import os.path
import FreeCAD
if FreeCAD.GuiUp:
    import FreeCADGui
from PySide2.QtWidgets import QFormLayout, QDoubleSpinBox
from CfdOF import CfdTools
from CfdOF.CfdTools import getQuantity, setQuantity, storeIfChanged
from CfdOF.Solve.CfdTurbulenceModels import getModelCoefficients, getModelsForCategory


class TaskPanelCfdPhysicsSelection:
    def __init__(self, obj):
        FreeCADGui.Selection.clearSelection()
        self.sel_server = None
        self.obj = obj
        self._coeffSpinBoxes = {}  # holds coeff name -> QDoubleSpinBox

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(CfdTools.getModulePath(), 'Gui', "TaskPanelPhysics.ui"))

        self.form.radioButtonSteady.toggled.connect(self.updateUI)
        self.form.cb_turbulence_model.currentIndexChanged.connect(self.onModelChanged)
        self.form.radioButtonTransient.toggled.connect(self.updateUI)
        self.form.radioButtonSinglePhase.toggled.connect(self.updateUI)
        self.form.radioButtonFreeSurface.toggled.connect(self.updateUI)
        if hasattr(self.form.checkBoxIsothermal, "checkStateChanged"):
            self.form.checkBoxIsothermal.checkStateChanged.connect(self.updateUI)
            self.form.viscousCheckBox.checkStateChanged.connect(self.updateUI)
            self.form.srfCheckBox.checkStateChanged.connect(self.updateUI)
        else:
            self.form.checkBoxIsothermal.stateChanged.connect(self.updateUI)
            self.form.viscousCheckBox.stateChanged.connect(self.updateUI)
            self.form.srfCheckBox.stateChanged.connect(self.updateUI)
        self.form.radioButtonLaminar.toggled.connect(self.updateUI)
        self.form.radioButtonRANS.toggled.connect(self.updateUI)
        self.form.radioButtonDES.toggled.connect(self.updateUI)
        self.form.radioButtonLES.toggled.connect(self.updateUI)

        self.load()

    def load(self):

        # Time
        if self.obj.Time == 'Steady':
            self.form.radioButtonSteady.toggle()
        elif self.obj.Time == 'Transient':
            self.form.radioButtonTransient.toggle()

        # Phase
        if self.obj.Phase == 'Single':
            self.form.radioButtonSinglePhase.toggle()
        elif self.obj.Phase == 'FreeSurface':
            self.form.radioButtonFreeSurface.toggle()

        # Flow
        self.form.checkBoxIsothermal.setChecked(self.obj.Flow == 'Isothermal')
        self.form.checkBoxHighMach.setChecked(self.obj.Flow == 'HighMachCompressible')

        # Turbulence
        if self.obj.Turbulence == 'Inviscid':
            self.form.viscousCheckBox.setChecked(False)
            self.form.radioButtonLaminar.toggle()
        if self.obj.Turbulence == 'Laminar':
            self.form.viscousCheckBox.setChecked(True)
            self.form.radioButtonLaminar.toggle()
        elif self.obj.Turbulence == 'RANS':
            self.form.viscousCheckBox.setChecked(True)
            self.form.radioButtonRANS.toggle()
        elif self.obj.Turbulence == 'DES':
            self.form.viscousCheckBox.setChecked(True)
            self.form.radioButtonDES.toggle()
        elif self.obj.Turbulence == 'LES':
            self.form.viscousCheckBox.setChecked(True)
            self.form.radioButtonLES.toggle()

        # Gravity
        setQuantity(self.form.gx, self.obj.gx)
        setQuantity(self.form.gy, self.obj.gy)
        setQuantity(self.form.gz, self.obj.gz)

        # SRF model
        self.form.srfCheckBox.setChecked(self.obj.SRFModelEnabled)

        setQuantity(self.form.inputSRFCoRx, self.obj.SRFModelCoR.x)
        setQuantity(self.form.inputSRFCoRy, self.obj.SRFModelCoR.y)
        setQuantity(self.form.inputSRFCoRz, self.obj.SRFModelCoR.z)

        setQuantity(self.form.inputSRFAxisx, self.obj.SRFModelAxis.x)
        setQuantity(self.form.inputSRFAxisy, self.obj.SRFModelAxis.y)
        setQuantity(self.form.inputSRFAxisz, self.obj.SRFModelAxis.z)

        setQuantity(self.form.inputSRFRPM, self.obj.SRFModelRPM)

        self.updateUI()

    def updateUI(self):
        self.form.TimeFrame.setVisible(True)
        self.form.FlowFrame.setVisible(True)
        self.form.turbulenceFrame.setVisible(True)

        # Steady / transient
        if self.form.radioButtonSteady.isChecked():
            self.form.radioButtonFreeSurface.setEnabled(False)
            if self.form.radioButtonDES.isChecked() or self.form.radioButtonLES.isChecked():
                self.form.radioButtonRANS.toggle()
            self.form.radioButtonDES.setEnabled(False)
            self.form.radioButtonLES.setEnabled(False)
            if self.form.radioButtonFreeSurface.isChecked():
                self.form.radioButtonSinglePhase.toggle()
        else:
            self.form.radioButtonFreeSurface.setEnabled(True)
            self.form.radioButtonDES.setEnabled(True)
            self.form.radioButtonLES.setEnabled(True)

        # Gravity
        self.form.gravityFrame.setEnabled(
            self.form.radioButtonFreeSurface.isChecked() or
            (not self.form.checkBoxIsothermal.isChecked() and not self.form.checkBoxHighMach.isChecked())
        )

        # SRF model
        srf_capable = (self.form.radioButtonSteady.isChecked() and self.form.checkBoxIsothermal.isChecked())
        srf_should_be_unchecked = (
            (not self.form.checkBoxIsothermal.isChecked()) or
            self.form.radioButtonTransient.isChecked() or
            self.form.radioButtonFreeSurface.isChecked()
        )
        self.form.srfCheckBox.setEnabled(srf_capable)
        if srf_should_be_unchecked:
            self.form.srfCheckBox.setChecked(False)
        self.form.srfFrame.setEnabled(self.form.srfCheckBox.isChecked())

        # Free surface
        if self.form.radioButtonFreeSurface.isChecked():
            self.form.checkBoxIsothermal.setChecked(True)
            self.form.checkBoxIsothermal.setEnabled(False)
        else:
            self.form.checkBoxIsothermal.setEnabled(True)

        # High Mach capability
        self.form.checkBoxHighMach.setEnabled(not self.form.checkBoxIsothermal.isChecked())
        if self.form.checkBoxIsothermal.isChecked():
            self.form.checkBoxHighMach.setChecked(False)

        # =========================
        # DYNAMIC TURBULENCE LOGIC
        # =========================

        if self.form.viscousCheckBox.isChecked():
            self.form.turbulenceFrame.setVisible(True)

            # Choose model list from CfdTurbulenceModels (single source of truth)
            if self.form.radioButtonRANS.isChecked():
                models = getModelsForCategory("RANS")
            elif self.form.radioButtonDES.isChecked():
                models = getModelsForCategory("DES")
            elif self.form.radioButtonLES.isChecked():
                models = getModelsForCategory("LES")
            else:
                models = []
            
            if not models:
                self.form.cb_turbulence_model.clear()
                self.form.gb_turbulence_coeffs.setVisible(False)
                return

            # Populate dropdown without triggering onModelChanged mid-update
            self.form.cb_turbulence_model.blockSignals(True)
            self.form.cb_turbulence_model.clear()
            self.form.cb_turbulence_model.addItems(models)

            # Restore saved model selection if it exists in the new list
            if models:
                ti = CfdTools.indexOrDefault(models, self.obj.TurbulenceModel, 0)
                self.form.cb_turbulence_model.setCurrentIndex(ti)

            self.form.cb_turbulence_model.blockSignals(False)

            # Rebuild coefficient form for whichever model is now selected
            self._rebuildCoefficientForm()

        else:
            self.form.turbulenceFrame.setVisible(False)
            self.form.gb_turbulence_coeffs.setVisible(False)

    def _rebuildCoefficientForm(self):
        """Clear and repopulate the coefficient QFormLayout for the current model."""
        modelName = self.form.cb_turbulence_model.currentText()

        if not modelName:
            self.form.gb_turbulence_coeffs.setVisible(False)
            return

        defaults = getModelCoefficients(modelName) or {}
        if not defaults:
            self.form.gb_turbulence_coeffs.setVisible(False)
            return

        # Retrieve any user-saved overrides from the document object
        saved = {}
        if hasattr(self.obj, 'TurbulenceModelCoeffs') and self.obj.TurbulenceModelCoeffs:
            saved = self.obj.TurbulenceModelCoeffs

        # Get or create the QFormLayout inside widget_coeffs_container
        # NEW - uses layout_coeffs directly from the .ui file
        layout = self.form.layout_coeffs
        while layout.rowCount():
            layout.removeRow(0)
        
        self._coeffSpinBoxes = {}

        for coeff, defaultVal in defaults.items():
            spinBox = QDoubleSpinBox()
            spinBox.setDecimals(6)
            spinBox.setRange(-1e9, 1e9)

            # Use saved override if present, otherwise fall back to default
            try:
                value = float(saved.get(coeff, defaultVal))
            except (TypeError, ValueError):
                value = float(defaultVal)

            spinBox.setValue(value)  # ← THIS WAS THE MISSING LINE
            layout.addRow(coeff, spinBox)
            self._coeffSpinBoxes[coeff] = spinBox

        # Show the group box only when there are coefficients to display
        self.form.gb_turbulence_coeffs.setVisible(bool(defaults))

        # Restore printCoeffs checkbox
        if hasattr(self.obj, 'PrintCoeffs'):
            self.form.check_print_coeffs.setChecked(self.obj.PrintCoeffs)

    def onModelChanged(self):
        """Called when the user picks a different model from the dropdown."""
        # Update the document object immediately so other parts of the UI
        # that read TurbulenceModel stay consistent
        self.obj.TurbulenceModel = self.form.cb_turbulence_model.currentText()
        self._rebuildCoefficientForm()

    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

        if self.form.radioButtonSteady.isChecked():
            storeIfChanged(self.obj, 'Time', 'Steady')
        elif self.form.radioButtonTransient.isChecked():
            storeIfChanged(self.obj, 'Time', 'Transient')

        if self.form.radioButtonSinglePhase.isChecked():
            storeIfChanged(self.obj, 'Phase', 'Single')
        elif self.form.radioButtonFreeSurface.isChecked():
            storeIfChanged(self.obj, 'Phase', 'FreeSurface')

        if self.form.checkBoxIsothermal.isChecked():
            storeIfChanged(self.obj, 'Flow', 'Isothermal')
        elif not self.form.checkBoxIsothermal.isChecked():
            if self.form.checkBoxHighMach.isChecked():
                storeIfChanged(self.obj, 'Flow', 'HighMachCompressible')
            else:
                storeIfChanged(self.obj, 'Flow', 'NonIsothermal')

        if self.form.viscousCheckBox.isChecked():
            if self.form.radioButtonLaminar.isChecked():
                storeIfChanged(self.obj, 'Turbulence', 'Laminar')
            else:
                if self.form.radioButtonRANS.isChecked():
                    storeIfChanged(self.obj, 'Turbulence', 'RANS')
                elif self.form.radioButtonDES.isChecked():
                    storeIfChanged(self.obj, 'Turbulence', 'DES')
                elif self.form.radioButtonLES.isChecked():
                    storeIfChanged(self.obj, 'Turbulence', 'LES')

                # Save selected model name
                storeIfChanged(self.obj, 'TurbulenceModel', self.form.cb_turbulence_model.currentText())

                # Save coefficient overrides (only what the user has actually changed)
                if hasattr(self.obj, 'TurbulenceModelCoeffs'):
                    coeffOverrides = {}
                    modelName = self.form.cb_turbulence_model.currentText()
                    defaults = getModelCoefficients(modelName)
                    for coeff, spinBox in self._coeffSpinBoxes.items():
                        # Only store if the user changed the value from the default
                        if abs(spinBox.value() - float(defaults.get(coeff, 0))) > 1e-10:
                            coeffOverrides[coeff] = str(spinBox.value())
                    storeIfChanged(self.obj, 'TurbulenceModelCoeffs', coeffOverrides)

                # Save printCoeffs flag
                if hasattr(self.obj, 'PrintCoeffs'):
                    storeIfChanged(self.obj, 'PrintCoeffs', self.form.check_print_coeffs.isChecked())

        else:
            storeIfChanged(self.obj, 'Turbulence', 'Inviscid')

        storeIfChanged(self.obj, 'gx', getQuantity(self.form.gx))
        storeIfChanged(self.obj, 'gy', getQuantity(self.form.gy))
        storeIfChanged(self.obj, 'gz', getQuantity(self.form.gz))

        storeIfChanged(self.obj, 'SRFModelEnabled', self.form.srfCheckBox.isChecked())
        if self.form.srfCheckBox.isChecked():
            storeIfChanged(self.obj, 'SRFModelRPM', self.form.inputSRFRPM.text())
            centre_of_rotation = FreeCAD.Vector(
                self.form.inputSRFCoRx.property("quantity").Value,
                self.form.inputSRFCoRy.property("quantity").Value,
                self.form.inputSRFCoRz.property("quantity").Value)
            storeIfChanged(self.obj, 'SRFModelCoR', centre_of_rotation)
            model_axis = FreeCAD.Vector(
                self.form.inputSRFAxisx.property("quantity").Value,
                self.form.inputSRFAxisy.property("quantity").Value,
                self.form.inputSRFAxisz.property("quantity").Value)
            storeIfChanged(self.obj, 'SRFModelAxis', model_axis)

    def reject(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

    def closing(self):
        # We call this from unsetEdit to allow cleanup
        return