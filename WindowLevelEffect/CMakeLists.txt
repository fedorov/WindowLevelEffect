set(MODULE_NAME WindowLevelEffect)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
    WindowLevelEffect.py
  )

set(MODULE_PYTHON_RESOURCES
    WindowLevelEffect.png
  )

slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
)
