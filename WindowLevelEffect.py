import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import LabelEffect

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# WindowLevelEffectOptions - see EditOptions and Effect for superclasses
#

class WindowLevelEffectOptions(LabelEffect.LabelEffectOptions):
  """ WindowLevelEffect-specfic gui
  """
  def __init__(self, parent=0):
    super(WindowLevelEffectOptions,self).__init__(parent)

  def __del__(self):
    super(WindowLevelEffectOptions,self).__del__()

  def create(self):
    super(WindowLevelEffectOptions,self).create()


    self.thresholdPaint.hide()
    self.paintOver.hide()
    self.threshold.hide()
    self.thresholdLabel.hide()

    # add the selection whether it should work as regular w/l control,
    # or as a rectangle
    self.normalMode = qt.QRadioButton('Normal mode')
    self.rectangleMode = qt.QRadioButton('Rectangle mode')
    self.normalMode.setChecked(1)

    label = qt.QLabel('Mode of operation:')
    self.frame.layout().addWidget(label)
    self.viewGroup = qt.QButtonGroup()
    self.viewGroup.addButton(self.normalMode,1)
    self.viewGroup.addButton(self.rectangleMode,2)
    self.frame.layout().addWidget(self.normalMode)
    self.frame.layout().addWidget(self.rectangleMode)
    self.viewGroup.connect('buttonClicked(int)',self.updateMRMLFromGUI)

    label = qt.QLabel('Layers affected:')
    self.bgSelector = qt.QCheckBox('Background')
    self.fgSelector = qt.QCheckBox('Foreground')
    self.bgSelector.checked = 0
    self.fgSelector.checked = 1
    self.frame.layout().addWidget(label)
    self.frame.layout().addWidget(self.bgSelector)
    self.frame.layout().addWidget(self.fgSelector)
    self.bgSelector.connect('stateChanged(int)',self.updateMRMLFromGUI)
    self.fgSelector.connect('stateChanged(int)',self.updateMRMLFromGUI)

    EditorLib.HelpButton(self.frame, "Use this tool to change window/level of background/foreground volumes based on the intensity range of the selected rectangle.\n\nLeft Click and Drag: sweep out an outline that will draw when the button is released. The outline will define the rectangle for calculating the new window/level settings.")
    # step4Layout.addRow(self.normalMode, rectangleMode)

    # Add vertical spacer
    self.frame.layout().addStretch(1)

    # set effect-specific parameters
    self.parameterNode.SetParameter('WindowLevelEffect,wlmode', 'Normal')
    self.parameterNode.SetParameter('WindowLevelEffect,changeBg','1')
    self.parameterNode.SetParameter('WindowLevelEffect,changeFg','1')
    self.parameterNode.SetParameter('Effect,scope','')

  def destroy(self):
    super(WindowLevelEffectOptions,self).destroy()

  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  def updateParameterNode(self, caller, event):
    node = self.editUtil.getParameterNode()
    if node != self.parameterNode:
      if self.parameterNode:
        node.RemoveObserver(self.parameterNodeTag)
      self.parameterNode = node
      self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    return
    super(WindowLevelEffectOptions,self).setMRMLDefaults()

  def updateGUIFromMRML(self,caller,event):
    return
    super(WindowLevelEffectOptions,self).updateGUIFromMRML(caller,event)

  def updateMRMLFromGUI(self):
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(WindowLevelEffectOptions,self).updateMRMLFromGUI()

    if self.normalMode.checked:
      self.parameterNode.SetParameter('WindowLevelEffect,wlmode','Normal')
    if self.rectangleMode.checked:
      self.parameterNode.SetParameter('WindowLevelEffect,wlmode','Rectangle')
    if self.bgSelector.checked:
      self.parameterNode.SetParameter('WindowLevelEffect,changeBg','1')
    else:
      self.parameterNode.SetParameter('WindowLevelEffect,changeBg','0')
    if self.fgSelector.checked:
      self.parameterNode.SetParameter('WindowLevelEffect,changeFg','1')
    else:
      self.parameterNode.SetParameter('WindowLevelEffect,changeFg','0')

    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()

#
# WindowLevelEffectTool
#

class WindowLevelEffectTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(WindowLevelEffectTool,self).__init__(sliceWidget)

    # create a logic instance to do the non-gui work
    self.logic = WindowLevelEffectLogic(self.sliceWidget.sliceLogic())
    self.options = WindowLevelEffectOptions()

    # interaction state variables
    self.actionState = None
    self.startXYPosition = None
    self.currentXYPosition = None

    # configuration
    self.parameterNode = self.editUtil.getParameterNode()
    self.mode = self.parameterNode.GetParameter('WindowLevelEffect,wlmode')
    self.changeBg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeBg')))
    self.changeFg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeFg')))

    # initialization
    self.createGlyph()

    self.mapper = vtk.vtkPolyDataMapper2D()
    self.actor = vtk.vtkActor2D()
    self.mapper.SetInput(self.polyData)
    self.actor.SetMapper(self.mapper)
    property_ = self.actor.GetProperty()
    property_.SetColor(1,1,0)
    property_.SetLineWidth(1)
    self.renderer.AddActor2D( self.actor )
    self.actors.append( self.actor )

    # will keep w/l on left mouse button down
    self.bgStartWindowLevel = [0,0]
    self.fgStartWindowLevel = [0,0]

  def cleanup(self):
    """
    call superclass to clean up actor
    """
    super(WindowLevelEffectTool,self).cleanup()


  def createGlyph(self):
    self.polyData = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    self.polyData.SetPoints( points )
    self.polyData.SetLines( lines )
    prevPoint = None
    firstPoint = None

    for x,y in ((0,0),)*4:
      p = points.InsertNextPoint( x, y, 0 )
      if prevPoint != None:
        idList = vtk.vtkIdList()
        idList.InsertNextId( prevPoint )
        idList.InsertNextId( p )
        self.polyData.InsertNextCell( vtk.VTK_LINE, idList )
      prevPoint = p
      if firstPoint == None:
        firstPoint = p

    # make the last line in the polydata
    idList = vtk.vtkIdList()
    idList.InsertNextId( p )
    idList.InsertNextId( firstPoint )
    self.polyData.InsertNextCell( vtk.VTK_LINE, idList )

  def updateGlyph(self):
    if not self.startXYPosition or not self.currentXYPosition:
      return

    points = self.polyData.GetPoints()
    xlo,ylo = self.startXYPosition
    xhi,yhi = self.currentXYPosition

    points.SetPoint( 0, xlo, ylo, 0 )
    points.SetPoint( 1, xlo, yhi, 0 )
    points.SetPoint( 2, xhi, yhi, 0 )
    points.SetPoint( 3, xhi, ylo, 0 )

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """

    if super(WindowLevelEffectTool,self).processEvent(caller,event):
      return

    try:
      self.mode = self.parameterNode.GetParameter('WindowLevelEffect,wlmode')
    except:
      return

    self.changeBg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeBg')))
    self.changeFg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeFg')))

    bgLayer = self.sliceLogic.GetBackgroundLayer()
    fgLayer = self.sliceLogic.GetForegroundLayer()

    bgNode = bgLayer.GetVolumeNode()
    fgNode = fgLayer.GetVolumeNode()

    if event == "LeftButtonPressEvent":
      self.actionState = "dragging"

      self.cursorOff()
      xy = self.interactor.GetEventPosition()
      self.startXYPosition = xy
      self.currentXYPosition = xy

      if self.mode == 'Normal':
        # remember W/L and range!
        if bgNode:
          bgDisplay = bgNode.GetDisplayNode()
          self.bgStartWindowLevel = [bgDisplay.GetWindow(), bgDisplay.GetLevel()]
        if fgNode:
          fgDisplay = fgNode.GetDisplayNode()
          self.fgStartWindowLevel = [fgDisplay.GetWindow(), fgDisplay.GetLevel()]
      else: # Rectangle mode
        self.updateGlyph()
      self.abortEvent(event)

    elif event == "MouseMoveEvent":
      if self.actionState == "dragging":
        if self.mode == 'Normal':
          if bgNode and self.changeBg:
            self.updateNodeWL(bgNode, self.bgStartWindowLevel, self.startXYPosition)
          if fgNode and self.changeFg:
            self.updateNodeWL(fgNode, self.fgStartWindowLevel, self.startXYPosition)
        else:
          self.currentXYPosition = self.interactor.GetEventPosition()
          self.updateGlyph()
          self.sliceView.scheduleRender()
        self.abortEvent(event)

    elif event == "LeftButtonReleaseEvent":
      self.actionState = ""
      self.cursorOn()
      if self.mode == 'Rectangle':
        self.apply()
        self.startXYPosition = (0,0)
        self.currentXYPosition = (0,0)
        self.updateGlyph()
      self.abortEvent(event)

  def apply(self):

    self.mode = self.parameterNode.GetParameter('WindowLevelEffect,wlmode')
    self.changeBg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeBg')))
    self.changeFg = not (0 == int(self.parameterNode.GetParameter('WindowLevelEffect,changeFg')))

    # see vtkSliceViewInteractorStyle:321
    lines = self.polyData.GetLines()
    if lines.GetNumberOfCells() == 0: return
    bgLayer = self.sliceLogic.GetBackgroundLayer()
    fgLayer = self.sliceLogic.GetForegroundLayer()
    bgNode = bgLayer.GetVolumeNode()
    fgNode = fgLayer.GetVolumeNode()
    if bgNode and self.changeBg:
      self.updateWindowLevelRectangle(bgLayer, self.polyData.GetBounds())
    if fgNode and self.changeFg:
      self.updateWindowLevelRectangle(fgLayer, self.polyData.GetBounds())
    self.polyData.GetPoints().Modified()

  def updateNodeWL(self, node, startWindowLevel, startXY):

    currentXY = self.interactor.GetEventPosition()

    vDisplay = node.GetDisplayNode()
    vImage = node.GetImageData()
    vRange = vImage.GetScalarRange()

    # see vtkSliceViewInteractorStyle.cxx:330
    deltaX = currentXY[0]-startXY[0]
    deltaY = currentXY[1]-startXY[1]
    gain = (vRange[1]-vRange[0])/500.
    newWindow = startWindowLevel[0]+(gain*deltaX)
    newLevel = startWindowLevel[1]+(gain*deltaY)

    vDisplay.SetAutoWindowLevel(0)
    vDisplay.SetWindowLevel(newWindow, newLevel)
    vDisplay.Modified()

  def updateWindowLevelRectangle(self, sliceLayer, xyBounds):
    # conversion as done in LabelEffect.py:applyImageMask
    xlo, xhi, ylo, yhi, zlo, zhi = xyBounds
    sliceNode = sliceLayer.GetVolumeNode()
    sliceImage = sliceNode.GetImageData()
    if not sliceImage:
      return [0,0,0,0]
    xyToIJK = sliceLayer.GetXYToIJKTransform().GetMatrix()
    tlIJK = xyToIJK.MultiplyPoint( (xlo, yhi, 0, 1) )[:3]
    trIJK = xyToIJK.MultiplyPoint( (xhi, yhi, 0, 1) )[:3]
    blIJK = xyToIJK.MultiplyPoint( (xlo, ylo, 0, 1) )[:3]
    brIJK = xyToIJK.MultiplyPoint( (xhi, ylo, 0, 1) )[:3]

    #
    # get the mask bounding box in ijk coordinates
    # - get the xy bounds
    # - transform to ijk
    # - clamp the bounds to the dimensions of the label image
    #

    # do the clamping of the four corners
    dims = sliceImage.GetDimensions()
    tl = [0,] * 3
    tr = [0,] * 3
    bl = [0,] * 3
    br = [0,] * 3
    corners = ((tlIJK, tl),(trIJK, tr),(blIJK, bl),(brIJK, br))
    for corner,clampedCorner in corners:
      for d in xrange(3):
        clamped = int(round(corner[d]))
        if clamped < 0: clamped = 0
        if clamped >= dims[d]: clamped = dims[d]-1
        clampedCorner[d] = clamped

    # calculate the statistics for the selected region
    clip = vtk.vtkImageClip()
    extentMin = [min(tl[0],min(tr[0],min(bl[0],br[0]))),min(tl[1],min(tr[1],min(bl[1],br[1]))),min(tl[2],min(tr[2],min(bl[2],br[2])))]
    extentMax = [max(tl[0],max(tr[0],max(bl[0],br[0]))),max(tl[1],max(tr[1],max(bl[1],br[1]))),max(tl[2],max(tr[2],max(bl[2],br[2])))]
    clip.SetOutputWholeExtent(extentMin[0],extentMax[0],extentMin[1],extentMax[1],extentMin[2],extentMax[2])
    clip.SetInput(sliceNode.GetImageData())
    clip.ClipDataOn()
    clip.Update()

    stats = vtk.vtkImageHistogramStatistics()
    stats.SetInput(clip.GetOutput())
    stats.Update()

    minIntensity = stats.GetMinimum()
    maxIntensity = stats.GetMaximum()

    sliceNode.GetDisplayNode().SetAutoWindowLevel(False)
    sliceNode.GetDisplayNode().SetAutoWindowLevel(0)
    sliceNode.GetDisplayNode().SetWindowLevel(maxIntensity-minIntensity, (maxIntensity-minIntensity)/2.+minIntensity)
    sliceNode.GetDisplayNode().Modified()

#
# WindowLevelEffectLogic
#

class WindowLevelEffectLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an WindowLevelEffectTool
  or WindowLevelEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the WindowLevelEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    super(WindowLevelEffectLogic,self).__init__(sliceLogic)


#
# The WindowLevelEffectExtension class definition
#

class WindowLevelEffectExtension(LabelEffect.LabelEffect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. WindowLevelEffect.png)
    self.name = "WindowLevelEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "WindowLevelEffect - change w/l for Bg/Fg using different tools"

    self.options = WindowLevelEffectOptions
    self.tool = WindowLevelEffectTool
    self.logic = WindowLevelEffectLogic


#
# WindowLevelEffect
#

class WindowLevelEffect():
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "Editor WindowLevel Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Andrey Fedorov (BWH)"]
    parent.hidden = True
    parent.helpText = """
    WindowLevel effect
    """
    parent.acknowledgementText = """
    This editor extension was developed by
    Andrey Fedorov, BWH supported by NIH grants CA151261, RR019703 and
    CA111288
    based on work by:
    Steve Pieper, Isomics, Inc.
    based on work by:
    Jean-Christophe Fillion-Robin, Kitware Inc.
    and was partially funded by NIH grant 3P41RR013218.
    """


    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['WindowLevelEffect'] = WindowLevelEffectExtension
