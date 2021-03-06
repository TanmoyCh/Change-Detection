# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Change
                                 A QGIS plugin
 Change
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-02-06
        git sha              : $Format:%H$
        copyright            : (C) 2019 by jb
        email                : jb
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QColor
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QAction, QFileDialog
from qgis.analysis import *
from osgeo import gdal, osr
import os
from qgis.PyQt import QtCore, QtGui
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
import processing
import tempfile


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Change_dialog import ChangeDialog
import os.path


class Change:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Change_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = ChangeDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Change')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Change', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Change/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Change'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.oldlib.clicked.connect(self.openRaster)
        self.dlg.newlib.clicked.connect(self.openRaster2)
        self.dlg.load_structures.clicked.connect(self.openVector)
        self.dlg.saveDEM.clicked.connect(self.saveRaster)
        self.loadRasters()
        self.loadRasters2()
        self.loadVectors()

    def loadRasters(self):
        """Load rasters for QGIS table of contents"""
        self.dlg.olddem_list.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        raster_layers = []
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                raster_layers.append(layer.name())
        self.dlg.olddem_list.addItems(raster_layers)

    def loadRasters2(self):
        """Load rasters for QGIS table of contents"""
        self.dlg.newdem_list.clear()
        layers2 = [layer2 for layer2 in QgsProject.instance().mapLayers().values()]
        raster_layers2 = []
        for layer2 in layers2:
            if layer2.type() == QgsMapLayer.RasterLayer:
                raster_layers2.append(layer2.name())
        self.dlg.newdem_list.addItems(raster_layers2)

    def loadVectors(self):
        """Load vectors for QGIS table of contents"""
        self.dlg.structure_list.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        vector_layers = []
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                vector_layers.append(layer.name())
        self.dlg.structure_list.addItems(vector_layers)

    def openRaster(self):
        """Open raster from file dialog"""
        inFile = str(QFileDialog.getOpenFileName(caption="Open raster", filter="GeoTiff (*.tif)")[0])
        if inFile is not None:
            self.iface.addRasterLayer(inFile, str.split(os.path.basename(inFile), ".")[0])
            self.loadRasters()

    def openRaster2(self):
        """Open raster from file dialog"""
        inFile = str(QFileDialog.getOpenFileName(caption="Open raster", filter="GeoTiff (*.tif)")[0])
        if inFile is not None:
            self.iface.addRasterLayer(inFile, str.split(os.path.basename(inFile), ".")[0])
            self.loadRasters2()

    def openVector(self):
        """Open vector from file dialog"""
        inFile = str(QFileDialog.getOpenFileName(caption="Open shapefile", filter="Shapefiles (*.shp)")[0])
        if inFile is not None:
            self.iface.addVectorLayer(inFile, str.split(os.path.basename(inFile), ".")[0], "ogr")
            self.loadVectors()

    def saveRaster(self):
        """Get the save file name for the change DEM"""
        outFile = str(QFileDialog.getSaveFileName(caption="Save change raster as",
                                                  filter="GeoTiff (*.tif)")[0])
        self.setRasterLine(outFile)

    def setRasterLine(self, text):
        """Set the GUI text for the output(change) raster file name"""
        self.dlg.outDEM.setText(text)

    def getRasterLayer(self):
        """Gets raster layer specified in first combo box"""
        layer = None
        layername = self.dlg.olddem_list.currentText()
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
                break
        return layer

    def getRasterLayer2(self):
        """Gets raster layer specified in second combo box"""
        layer = None
        layername = self.dlg.newdem_list.currentText()
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
                break
        return layer

    def getVectorLayer(self):
        """Gets vector layer specified in combo box"""
        layer = None
        layername = self.dlg.structure_list.currentText()
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
                break
        return layer

    def setVariable(self):
        """Get and set all variables from UI"""
        self.olddem = self.getRasterLayer()
        self.newdem = self.getRasterLayer2()
        self.outRaster = self.dlg.outDEM.text()
        self.thrs = self.dlg.min_thrs.value()
        self.inVector = self.getVectorLayer()

    def clip_oldDEM(self):

        old_input = self.olddem

        mask_layer = self.inVector

        #old_clip = r'C:\OSGeo4W64\apps\qgis\python\plugins\change\old_clip.tif'
        old_clip = QgsProcessingUtils.generateTempFilename('old_clip.tif')

        proc = processing.run("gdal:cliprasterbymasklayer",
                       {'INPUT': old_input,
                        'MASK': mask_layer,
                        'NODATA': -9999,
                        'ALPHA_BAND': False,
                        'CROP_TO_CUTLINE': False,
                        'KEEP_RESOLUTION': False,
                        'OUTPUT': old_clip}
                       )
        #output = QgsRasterLayer(proc['OUTPUT'])
        output = QgsRasterLayer(old_clip)
        #ouput = QgsProject.instance().addMapLayer("memory:old_clip")[0]

        return output

    def clip_newDEM(self):

        old_input = self.newdem

        mask_layer = self.inVector

        #new_clip = r'C:\OSGeo4W64\apps\qgis\python\plugins\change\new_clip.tif'
        new_clip = QgsProcessingUtils.generateTempFilename('new_clip.tif')

        proc = processing.run("gdal:cliprasterbymasklayer",
                       {'INPUT': old_input,
                        'MASK': mask_layer,
                        'NODATA': -9999,
                        'ALPHA_BAND': False,
                        'CROP_TO_CUTLINE': False,
                        'KEEP_RESOLUTION': False,
                        'OUTPUT': new_clip }
                       )
        output = QgsRasterLayer(new_clip, "clippedNewDEM")

        #output = QgsRasterLayer(proc['OUTPUT'])

        QgsProject.instance().addMapLayer(output)

        return output

    def rasterCalculation(self, old_clip, new_clip):

        #before_input = self.olddem
        beforeraster = old_clip
        if not beforeraster.isValid():
            print("Layer failed to load!")

        #after_input = self.newdem
        afterraster = new_clip
        if not afterraster.isValid():
            print("Layer failed to load!")

        beforeentry = QgsRasterCalculatorEntry()
        beforeentry.raster = beforeraster
        beforeentry.bandNumber = 1
        beforeentry.ref = 'Before@1'

        afterentry = QgsRasterCalculatorEntry()
        afterentry.raster = afterraster
        afterentry.bandNumber = 1
        afterentry.ref = 'After@2'

        entries = [afterentry, beforeentry]

        e = beforeraster.extent()
        w = beforeraster.width()
        h = beforeraster.height()

        #output = 'C:/OSGeo4W64/apps/qgis/python/plugins/outputs/test.tif'

        change = QgsRasterCalculator('%s - %s' % (afterentry.ref, beforeentry.ref), self.outRaster, "GTiff", e, w, h,
                                     entries)
        result = change.processCalculation()

        return self.outRaster
        #lyr =(self.output, "Change")
        #QgsMapLayerRegistry.instance().addMapLayer(lyr)

    def addLayers(self):
        """Add change raster to table of contents"""
        self.iface.addRasterLayer(self.outRaster, str.split(os.path.basename(self.outRaster), ".")[0])

    def colorRamp(self):
        """Create default color ramp for change raster"""

        layer = self.iface.activeLayer()

        renderer = layer.renderer()
        provider = layer.dataProvider()
        extent = layer.extent()

        ver = provider.hasStatistics(1, QgsRasterBandStats.All)

        stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)

        # need to fix with if statement if input is greater than min and max
        min = stats.minimumValue * -1
        max = stats.maximumValue


        if self.thrs < min:
            min_color = (min * -1) - 1
            print ('Threshold setting greater than the maximum decrease in change processed')
        else:
            min_color = (min * -1) + .1

        if self.thrs > max:
            max_color = max + 1
            print ('Threshold setting greater than the maximum increase in change processed')
        else:
            max_color = max - .1

        # need to divide defaults by max and min
        defualt = float(0.00)
        if self.thrs == defualt:
            pos_ramp = max/2
            neg_ramp = -1 * (min/2)
        else:
            pos_ramp = self.thrs
            neg_ramp = -1 * self.thrs

        lst = []
        qri = QgsColorRampShader.ColorRampItem
        # i.append(qri(0, QColor(0, 0, 0, 0,), 'NODATA'))
        lst.append(qri(min_color, QColor(176, 24, 4, 255), 'Significant Decrease'))
        lst.append(qri(neg_ramp, QColor(255, 106, 113, 255), 'Minor Decrease'))
        lst.append(qri(0, QColor(247, 247, 247, 0), 'No Change'))
        lst.append(qri(pos_ramp, QColor(147, 156, 215, 255), 'Minor Increase'))
        lst.append(qri(max_color, QColor(7, 4, 215, 255), 'Significant Increase'))

        myRasterShader = QgsRasterShader()
        myColorRamp = QgsColorRampShader()

        myColorRamp.setColorRampItemList(lst)
        myColorRamp.setColorRampType(QgsColorRampShader.Interpolated)
        myRasterShader.setRasterShaderFunction(myColorRamp)

        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), layer.type(), myRasterShader)

        layer.setRenderer(myPseudoRenderer)

        layer.triggerRepaint()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Change'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        self.dlg.show()
        self.loadRasters()
        self.loadRasters2()
        self.loadVectors()
        # show the dialog
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.setVariable()
            self.rasterCalculation(self.clip_oldDEM(), self.clip_newDEM())
            self.addLayers()
            self.colorRamp()