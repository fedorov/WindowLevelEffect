set(MODULE_NAME WindowLevelEffect)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
    WindowLevelEffect.py
  )

set(MODULE_PYTHON_RESOURCES
    WindowLevelEffect.png
  )

ctkMacroCompilePythonScript(
  TARGET_NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

