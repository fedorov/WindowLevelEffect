cmake_minimum_required(VERSION 2.8.7)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  set(EXTENSION_NAME WindowLevelEffect)
  set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/WindowLevelEffect")
  set(EXTENSION_CATEGORY "Editor Effects")
  set(EXTENSION_CONTRIBUTORS "Andrey Fedorov (SPL)")
  set(EXTENSION_DESCRIPTION "This is a utility effect to control window/level from Editor module. Unlike the standard Slicer functionality, this extension allows to change window/level for both background and/or foreground volumes. An ROI tool allows to interactively set window/level based on the intensity range of a user-defined rectangular area.")
endif()

#-----------------------------------------------------------------------------
set(MODULE_NAME WindowLevelEffect)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
    WindowLevelEffect.py
  )

set(MODULE_PYTHON_RESOURCES
    WindowLevelEffect.png
  )

# add_subdirectory(Logic)

#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
    TARGET_NAME ${EXTENSION_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()
