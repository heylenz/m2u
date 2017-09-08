"""
the asset-export UI

This window will receive data from the export process,
that data can then be edited (change names and paths of assets)
and finally send the edited data back to the export process which will then
continue with the actual export.

"""

import os

from Qt import QtWidgets, QtCore, QtGui

from m2u import ui
from m2u import core
from . import icons
from .SubfolderBrowseDialog import SubfolderBrowseDialog
from m2u.helper.assethelper import AssetListEntry


class ExportWindow(ui.window_base_class):
    def __init__(self, *args, **kwargs):
        super(ExportWindow, self).__init__(*args, **kwargs)

        self.setWindowFlags(QtCore.Qt.Window)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("Export")
        self.setWindowIcon(icons.m2uIcon32)

        self.italicFont = QtGui.QFont()
        self.italicFont.setItalic(True)
        self.instanceBrush = QtGui.QBrush(QtCore.Qt.darkGray)
        self.discrepancyBrush = QtGui.QBrush(QtCore.Qt.red)
        self.untaggedBrush = QtGui.QBrush(QtCore.Qt.yellow)

        # self.browseDialog = SubfolderBrowseDialog()

        self.buildUI()
        self.connectUI()

    def buildUI(self):
        """create the widgets and layouts"""
        # left stuff
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.setContentsMargins(1, 1, 1, 1)
        leftWidget = QtWidgets.QWidget()  # widget required for QSplitter
        # - asset tree
        self.assetTree = QtWidgets.QTreeWidget()
        self.assetTree.setColumnCount(2)
        self.assetTree.setHeaderLabels(["Assets / Instances", "Subpath"])
        self.assetTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.assetTree.setColumnWidth(0, 160)
        leftLayout.addWidget(self.assetTree)
        # - info labels
        self.discrepancyLbl = QtWidgets.QLabel("Objects with same AssetPath but different geometry detected!")
        p = self.discrepancyLbl.palette()
        p.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, self.discrepancyBrush)
        self.discrepancyLbl.setPalette(p)
        self.untaggedLbl = QtWidgets.QLabel("Untagged objects detected, assigned auto-generated names.")
        p = self.untaggedLbl.palette()
        p.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, self.untaggedBrush)
        self.untaggedLbl.setPalette(p)
        leftLayout.addWidget(self.discrepancyLbl)
        leftLayout.addWidget(self.untaggedLbl)
        # - left buttons
        layout = QtWidgets.QGridLayout()
        self.selectInstancesBtn = QtWidgets.QPushButton("Select Instances")
        self.selectInstancesBtn.setDisabled(True)
        layout.addWidget(self.selectInstancesBtn, 0, 0)
        self.removeBtn = QtWidgets.QPushButton("Remove")
        self.removeBtn.setDisabled(True)
        layout.addWidget(self.removeBtn, 1, 0)
        self.makeNewBtn = QtWidgets.QPushButton("Make New Unique(s)")
        self.makeNewBtn.setDisabled(True)
        layout.addWidget(self.makeNewBtn, 1, 1)

        leftLayout.addItem(layout)
        leftWidget.setLayout(leftLayout)

        # right stuff
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.setContentsMargins(1, 1, 1, 1)
        rightWidget = QtWidgets.QWidget()
        # - editing group box
        editGrp = QtWidgets.QGroupBox("Edit Selected")
        grpLayout = QtWidgets.QVBoxLayout()
        grpLayout.setContentsMargins(1, 1, 1, 1)
        # - - asset path edit
        subpathLayout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel("Set Asset Subpath")
        subpathLayout.addWidget(label, 0, 0)
        self.subpathEdit = QtWidgets.QLineEdit()
        subpathLayout.addWidget(self.subpathEdit, 1, 0)
        self.subpathBrowseBtn = QtWidgets.QToolButton()
        self.subpathBrowseBtn.setIcon(icons.icoBrowse)
        self.subpathBrowseBtn.setToolTip("Browse")
        subpathLayout.addWidget(self.subpathBrowseBtn, 1, 1)
        self.subpathAssignBtn = QtWidgets.QPushButton("Set")
        subpathLayout.addWidget(self.subpathAssignBtn, 1, 2)
        grpLayout.addItem(subpathLayout)
        # - - prefix and suffix
        prefixLayout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel("Set Prefix")
        prefixLayout.addWidget(label, 0, 0)
        self.prefixEdit = QtWidgets.QLineEdit()
        prefixLayout.addWidget(self.prefixEdit, 0, 1)
        self.prefixAssignBtn = QtWidgets.QPushButton("Set")
        prefixLayout.addWidget(self.prefixAssignBtn, 0, 2)
        label = QtWidgets.QLabel("Set Suffix")
        prefixLayout.addWidget(label, 1, 0)
        self.suffixEdit = QtWidgets.QLineEdit()
        prefixLayout.addWidget(self.suffixEdit, 1, 1)
        self.suffixAssignBtn = QtWidgets.QPushButton("Set")
        prefixLayout.addWidget(self.suffixAssignBtn, 1, 2)
        grpLayout.addItem(prefixLayout)

        editGrp.setLayout(grpLayout)
        rightLayout.addWidget(editGrp)

        # - right buttons
        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(0,1)
        self.assignAssetDataBtn = QtWidgets.QPushButton("Assign Edited Data")
        self.assignAssetDataBtn.setToolTip("Only assign the data to the objects in the scene. Don't export.")
        self.assignAssetDataBtn.setIcon(icons.icoDoAssign)
        layout.addWidget(self.assignAssetDataBtn, 0, 1)
        self.exportSelectedBtn = QtWidgets.QPushButton("Export Selected")
        self.exportSelectedBtn.setToolTip("Export only the assets that are selected in the list.")
        self.exportSelectedBtn.setIcon(icons.icoDoExportSel)
        layout.addWidget(self.exportSelectedBtn, 1, 1)
        self.cancelBtn = QtWidgets.QPushButton("Cancel")
        self.cancelBtn.setIcon(icons.icoCancel)
        layout.addWidget(self.cancelBtn, 2, 0)
        self.exportAllBtn = QtWidgets.QPushButton("Export")
        self.exportAllBtn.setIcon(icons.icoDoExport)
        layout.addWidget(self.exportAllBtn, 2, 1)

        rightLayout.addStretch()
        rightLayout.addItem(layout)
        rightWidget.setLayout(rightLayout)

        # add all onto the form (splitted)
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
        leftWidget.resize(350,200)
        # leftWidget.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Preferred)
        # rightWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Preferred)
        # splitter.setStretchFactor(0, 100)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def connectUI(self):
        """connect slots to callbacks"""
        self.cancelBtn.clicked.connect(self.close)
        self.exportAllBtn.clicked.connect(self.exportAllBtnClicked)
        self.assignAssetDataBtn.clicked.connect(self.assignAssetDataBtnClicked)
        self.exportSelectedBtn.clicked.connect(self.exportSelectedBtnClicked)

        self.subpathAssignBtn.clicked.connect(self.subpathAssignBtnClicked)
        self.prefixAssignBtn.clicked.connect(self.prefixAssignBtnClicked)
        self.suffixAssignBtn.clicked.connect(self.suffixAssignBtnClicked)

        self.selectInstancesBtn.clicked.connect(self.selectInstancesBtnClicked)
        self.removeBtn.clicked.connect(self.removeBtnClicked)
        self.makeNewBtn.clicked.connect(self.makeNewBtnClicked)

        self.subpathBrowseBtn.clicked.connect(self.subpathBrowseBtnClicked)

    ################################
    # Actions and Callbacks
    ################################

    def setExportOperationAndShow(self, operation):
        """ Set the temporary data for editing and show the window.
        All follow-up export tasks will be called from within the ui.

        """
        self.operation = operation
        self.assetTree.clear()
        self.assetItemList = []
        self.discrepancyLbl.setVisible(operation.tagged_discrepancy_detected)
        self.untaggedLbl.setVisible(operation.untagged_uniques_detected)

        for entry in operation.asset_list:
            lpath, fext = os.path.splitext(entry.asset_path)
            fpath, fname = os.path.split(lpath)
            if len(fpath) == 0:
                # If there is no subpath, let us display at least a slash.
                fpath = "/"
            asset_item = QtWidgets.QTreeWidgetItem(self.assetTree)
            asset_item.setText(0, fname)
            asset_item.setText(1, fpath)
            asset_item.setFlags(QtCore.Qt.ItemIsEnabled |
                                QtCore.Qt.ItemIsEditable |
                                QtCore.Qt.ItemIsSelectable)

            self.assetItemList.append(asset_item)
            for obj_name, obj_ref in entry.obj_list:
                obj_item = QtWidgets.QTreeWidgetItem(asset_item)
                obj_item.setText(0, obj_name)
                obj_item.setFont(0, self.italicFont)
                # obj_item.setDisabled(True)
                obj_item.setForeground(0, self.instanceBrush)
                obj_item.setIcon(0, icons.icoTransform)
                obj_item.obj_name = obj_name
                obj_item.obj_ref = obj_ref

        self.show()
        self.raise_()

    def _getExportData(self):
        """ Reassemble the - possibly edited - export data from the
        tree-entries.

        """
        assetList = []
        # for i in range(0, self.assetTree.topLevelItemCount() - 1):
        for item in self.assetItemList:
            path = item.text(1)
            if not path.endswith("/") and len(path) > 0:
                path = path+"/"
            path = path + item.text(0)
            entry = AssetListEntry(path)
            for i in range(0, item.childCount()):
                child = item.child(i)
                entry.append(child.obj_name, child.obj_ref)
            assetList.append(entry)
        return assetList

    # ---

    def exportAllBtnClicked(self):
        assetList = self._getExportData()
        self.operation.set_edited_data(assetList)
        self.operation.do_export()
        self.close()

    def exportSelectedBtnClicked(self):
        assetList = []
        # for i in range(0, self.assetTree.topLevelItemCount() - 1):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            path = item.text(1)
            if not path.endswith("/") and len(path) > 0:
                path = path+"/"
            path = path + item.text(0)
            entry = AssetListEntry(path)
            for i in range(0, item.childCount()):
                child = item.child(i)
                entry.append(child.obj_name, child.obj_ref)
            assetList.append(entry)
        self.operation.set_edited_data(assetList)
        self.operation.do_export()
        self.close()

    def assignAssetDataBtnClicked(self):
        assetList = self._getExportData()
        self.operation.set_edited_data(assetList)
        self.operation.do_assign_only()
        self.close()

    # ---

    def subpathAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            item.setText(1, self.subpathEdit.text())

    def prefixAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            text = item.text(0)
            prefix = self.prefixEdit.text()
            if text.startswith(prefix):
                continue
            text = prefix + text
            item.setText(0, text)

    def suffixAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            text = item.text(0)
            suffix = self.suffixEdit.text()
            if text.endswith(suffix):
                continue
            if suffix.startswith("_"):
                # TODO: maybe make user-settings set tuple of valid
                #   suffix delimiters?
                index = text.rfind("_")
                if index > -1:
                    text = text[:index]
            text = text + suffix
            item.setText(0, text)

    def subpathBrowseBtnClicked(self):
        basePath = core.pipeline.get_project_export_dir()
        self.browseDialog.setTopDirectory(basePath)
        fullPath = basePath + "/" + self.subpathEdit.text()
        self.browseDialog.setDirectory(fullPath)
        result = self.browseDialog.exec_()
        if result == 1:
            subpath = self.browseDialog.directory().path()
            subpath = subpath[len(basePath):]
            self.subpathEdit.setText(subpath)

    # ---

    def selectInstancesBtnClicked(self):
        pass

    def removeBtnClicked(self):
        pass

    def makeNewBtnClicked(self):
        pass
