cmake_minimum_required(VERSION 2.8.9)

project(WindowLevelEffect)

#-----------------------------------------------------------------------------
set(EXTENSION_NAME WindowLevelEffect)
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/WindowLevelEffect")
set(EXTENSION_CATEGORY "Editor Effects")
set(EXTENSION_CONTRIBUTORS "Andrey Fedorov (SPL), Steve Pieper (Isomics Inc)")
set(EXTENSION_DESCRIPTION "This is a utility effect to control window/level from Editor module. Unlike the standard Slicer functionality, this extension allows to change window/level for both background and/or foreground volumes. An ROI tool allows to interactively set window/level based on the intensity range of a user-defined rectangular area.")
set(EXTENSION_ICON_URL "http://www.slicer.org/slicerWiki/images/3/39/WindowLevelEffectLogo.png")
set(EXTENSION_SCREENSHOT_URL "http://www.slicer.org/slicerWiki/images/c/c1/WindowLevelEffectScreenShot.png")
set(EXTENSION_DEPENDS "Editor")

set(EXTENSION_MAJOR_VERSION "1" )
set(EXTENSION_MINOR_VERSION "0" )
set(EXTENSION_PATCH_VERSION "" )
set(EXTENSION_STATUS "Experimental")

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

add_subdirectory(WindowLevelEffect)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
