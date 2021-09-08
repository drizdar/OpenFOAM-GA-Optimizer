@echo off
rem ! /bin/sh

rem HAVE TO BE IN 'of230' ALIAS:

rem --------------
rem PRE-PROCESSING
rem --------------
rem Incorporate the parameters from DAKOTA into the template, writing ros.in
rem Use the following line if SNL's APREPRO utility is used instead of DPrePro.
rem ../aprepro -c '*' -q --nowarning ros.template ros.in

echo %CD%

"C:\Program Files\FreeCAD 0.18\bin\python.exe" dprepro.py %1% SSInputs.template SSInputs.in

xcopy /s /e /y ..\casebase
copy SSInputs.in SSInputs

"C:\Program Files\FreeCAD 0.18\bin\python.exe" CFD_Macro.py



