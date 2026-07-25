REM Lancer ReventePro V4 en arrière-plan sans terminal
REM Ce script lance le batch Flask et ouvre le navigateur automatiquement

Dim objShell, strBatchPath, objFSO, intWaitTime

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

REM Chemin du batch (adapter si nécessaire)
strBatchPath = "C:\Users\nqair\OneDrive\Bureau\ReventePro_V4\launch_reventepro.bat"

REM Vérifier si le batch existe
If Not objFSO.FileExists(strBatchPath) Then
    MsgBox "Erreur : launch_reventepro.bat introuvable !" & vbCrLf & "Chemin : " & strBatchPath, vbCritical, "ReventePro - Erreur"
    WScript.Quit 1
End If

REM Lancer le batch en arrière-plan (mode caché : 0)
On Error Resume Next
objShell.Run strBatchPath, 0, False
On Error GoTo 0

REM Attendre 3 secondes pour que Flask démarre
WScript.Sleep 3000

REM Ouvrir le navigateur automatiquement
objShell.Run "cmd /c start http://127.0.0.1:5000", 0, False

REM Message de confirmation
MsgBox "✅ ReventePro V4 est en cours de lancement..." & vbCrLf & vbCrLf & "Votre navigateur va s'ouvrir automatiquement." & vbCrLf & "URL : http://127.0.0.1:5000", vbInformation, "ReventePro V4"
