Attribute VB_Name = "TrainerMacros"
' BAV Excel Trainer — one-click Check, Hint, and Reveal Answer
' Import via Developer > Visual Basic > File > Import File
' Assign buttons on the Trainer tab to CheckActive, HintActive, RevealActive

Option Explicit

Private Const META_SHEET As String = "_TrainerMeta"
Private Const REF_SHEET As String = "_RefFormulas"

Public Sub CheckActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab.", vbExclamation
        Exit Sub
    End If
    RunTrainerCommand "check", compId
End Sub

Public Sub HintActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab.", vbExclamation
        Exit Sub
    End If
    RunTrainerCommand "hint", compId
End Sub

Public Sub RevealActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab.", vbExclamation
        Exit Sub
    End If
    If MsgBox("Reveal the reference formula for " & compId & "?", vbYesNo + vbQuestion) = vbNo Then Exit Sub
    RevealFormula compId
End Sub

Private Function GetSelectedComponentId() As String
    Dim ws As Worksheet
    Dim r As Long
    On Error GoTo Fail
    Set ws = ThisWorkbook.Worksheets("Trainer")
    r = ActiveCell.Row
    If r < 5 Then GoTo Fail
    GetSelectedComponentId = LookupComponentId(r)
    Exit Function
Fail:
    GetSelectedComponentId = ""
End Function

Private Function LookupComponentId(rowNum As Long) As String
    Dim ws As Worksheet
    Dim meta As Worksheet
    Dim title As String
    Dim r As Long
    Set ws = ThisWorkbook.Worksheets("Trainer")
    title = ws.Cells(rowNum, 1).Value
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 5).Value = title Then
            LookupComponentId = meta.Cells(r, 1).Value
            Exit Function
        End If
    Next r
    LookupComponentId = ""
End Function

Private Sub RevealFormula(compId As String)
    Dim refWs As Worksheet
    Dim tabName As String
    Dim cellAddr As String
    Dim formula As String
    Dim r As Long
    Set refWs = ThisWorkbook.Worksheets(REF_SHEET)
    For r = 2 To refWs.Cells(refWs.Rows.Count, 1).End(xlUp).Row
        If refWs.Cells(r, 1).Value = compId Then
            tabName = refWs.Cells(r, 2).Value
            cellAddr = refWs.Cells(r, 3).Value
            formula = refWs.Cells(r, 4).Value
            ThisWorkbook.Worksheets(tabName).Range(cellAddr).Formula = formula
            UpdateStatus compId, "revealed"
            MsgBox "Formula inserted into " & tabName & "!" & cellAddr, vbInformation
            Exit Sub
        End If
    Next r
    MsgBox "Reference formula not found for " & compId, vbExclamation
End Sub

Private Sub UpdateStatus(compId As String, status As String)
    Dim meta As Worksheet
    Dim r As Long
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 1).Value = compId Then
            meta.Cells(r, 9).Value = status
            Exit Sub
        End If
    Next r
End Sub

Private Sub RunTrainerCommand(cmd As String, compId As String)
    Dim wbPath As String
    Dim pyCmd As String
    wbPath = ThisWorkbook.FullName
    pyCmd = "python3 -m core " & cmd & " --workbook """ & wbPath & """ --component " & compId
    MsgBox "Run from terminal:" & vbCrLf & pyCmd, vbInformation, "BAV Trainer CLI"
End Sub

Public Sub CheckFormulaLocal(compId As String)
    ' Pure-VBA value check: compare practice cell to reference workbook (if cached)
    Dim refWs As Worksheet
    Dim tabName As String
    Dim cellAddr As String
    Dim userVal As Variant
    Dim r As Long
    Application.CalculateFullRebuild
    Set refWs = ThisWorkbook.Worksheets(REF_SHEET)
    For r = 2 To refWs.Cells(refWs.Rows.Count, 1).End(xlUp).Row
        If refWs.Cells(r, 1).Value = compId Then
            tabName = refWs.Cells(r, 2).Value
            cellAddr = refWs.Cells(r, 3).Value
            userVal = ThisWorkbook.Worksheets(tabName).Range(cellAddr).Value
            If IsEmpty(userVal) Or userVal = "" Then
                MsgBox "Enter a formula first.", vbExclamation
            Else
                MsgBox "Current value: " & userVal & vbCrLf & _
                       "Open the _reference workbook in Excel and re-save to enable full value validation.", _
                       vbInformation, "Check (local)"
            End If
            Exit Sub
        End If
    Next r
End Sub
