Option Explicit

Dim fso, folder, bat, sh
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
bat = folder & "\GeoGrid.bat"

Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c """ & bat & """", 0, False
