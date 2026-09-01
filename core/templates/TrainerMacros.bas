Attribute VB_Name = "TrainerMacros"
' BAV Excel Trainer — one-click Check, Hint, and Reveal Answer (local, no terminal)
' Import via Developer > Visual Basic > File > Import File
' Assign buttons on the Trainer tab to CheckActive, HintActive, RevealActive

Option Explicit

Private Const META_SHEET As String = "_TrainerMeta"
Private Const REF_SHEET As String = "_RefFormulas"
Private Const REF_VALUES_SHEET As String = "_RefValues"
Private Const TRAINER_SHEET As String = "Trainer"

Public Sub CheckActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab (row 5+).", vbExclamation
        Exit Sub
    End If
    CheckFormulaLocal compId
End Sub

Public Sub HintActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab (row 5+).", vbExclamation
        Exit Sub
    End If
    HintLocal compId
End Sub

Public Sub RevealActive()
    Dim compId As String
    compId = GetSelectedComponentId()
    If compId = "" Then
        MsgBox "Select a component row on the Trainer tab (row 5+).", vbExclamation
        Exit Sub
    End If
    If MsgBox("Reveal the reference formula for " & compId & "?", vbYesNo + vbQuestion) = vbNo Then Exit Sub
    RevealFormula compId
End Sub

Private Function GetSelectedComponentId() As String
    Dim ws As Worksheet
    Dim r As Long
    On Error GoTo Fail
    Set ws = ThisWorkbook.Worksheets(TRAINER_SHEET)
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
    Set ws = ThisWorkbook.Worksheets(TRAINER_SHEET)
    title = ws.Cells(rowNum, 2).Value
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 5).Value = title Then
            LookupComponentId = meta.Cells(r, 1).Value
            Exit Function
        End If
    Next r
    LookupComponentId = ""
End Function

Public Sub CheckFormulaLocal(compId As String)
    Dim meta As Worksheet
    Dim tabName As String
    Dim cellAddr As String
    Dim expected As Variant
    Dim tolerance As Double
    Dim userVal As Variant
    Dim r As Long
    Application.CalculateFullRebuild
    On Error GoTo CheckFail
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 1).Value = compId Then
            tabName = meta.Cells(r, 3).Value
            cellAddr = meta.Cells(r, 4).Value
            expected = meta.Cells(r, 11).Value
            tolerance = meta.Cells(r, 12).Value
            If IsEmpty(tolerance) Or tolerance = 0 Then tolerance = 0.01
            GoTo FoundMeta
        End If
    Next r
    MsgBox "Component not found in " & META_SHEET, vbExclamation
    Exit Sub

FoundMeta:
    If Not ThisWorkbook.Worksheets(tabName).Range(cellAddr).HasFormula Then
        userVal = ThisWorkbook.Worksheets(tabName).Range(cellAddr).Value
        If IsEmpty(userVal) Or userVal = "" Then
            MsgBox "Enter a formula in " & tabName & "!" & cellAddr & " before checking.", vbExclamation
            Exit Sub
        End If
    End If
    userVal = ThisWorkbook.Worksheets(tabName).Range(cellAddr).Value
    If IsEmpty(expected) Or IsNull(expected) Then
        MsgBox "No expected value in map for " & compId, vbExclamation
        Exit Sub
    End If
    If IsNumeric(userVal) And IsNumeric(expected) Then
        Dim u As Double, e As Double
        u = CDbl(userVal)
        e = CDbl(expected)
        If e = 0 Then
            If Abs(u - e) <= tolerance Then
                UpdateStatus compId, "correct"
                MsgBox "Correct! (" & u & ")", vbInformation, "Check"
            Else
                MsgBox "Mismatch: got " & u & ", expected " & e, vbExclamation, "Check"
            End If
        Else
            If Abs(u - e) / Abs(e) <= tolerance Or Abs(u - e) <= tolerance Then
                UpdateStatus compId, "correct"
                MsgBox "Correct! (" & u & ")", vbInformation, "Check"
            Else
                MsgBox "Mismatch: got " & u & ", expected " & e & " (±" & Format(tolerance, "0%") & ")", vbExclamation, "Check"
            End If
        End If
    Else
        If CStr(userVal) = CStr(expected) Then
            UpdateStatus compId, "correct"
            MsgBox "Correct!", vbInformation, "Check"
        Else
            MsgBox "Mismatch: got " & userVal & ", expected " & expected, vbExclamation, "Check"
        End If
    End If
    Exit Sub
CheckFail:
    MsgBox "Check failed: " & Err.Description, vbCritical
End Sub

Public Sub HintLocal(compId As String)
    Dim meta As Worksheet
    Dim tabName As String
    Dim cellAddr As String
    Dim hintsRaw As String
    Dim hintParts() As String
    Dim level As Long
    Dim maxHints As Long
    Dim hintText As String
    Dim r As Long
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 1).Value = compId Then
            tabName = meta.Cells(r, 3).Value
            cellAddr = meta.Cells(r, 4).Value
            level = CLng(meta.Cells(r, 7).Value)
            maxHints = CLng(meta.Cells(r, 8).Value)
            hintsRaw = meta.Cells(r, 14).Value
            If hintsRaw = "" Then
                hintText = meta.Cells(r, 6).Value
            Else
                hintParts = Split(hintsRaw, "|")
                If level >= UBound(hintParts) + 1 Then
                    hintText = meta.Cells(r, 6).Value & " (all hints shown)"
                Else
                    hintText = hintParts(level)
                    level = level + 1
                    meta.Cells(r, 7).Value = level
                End If
            End If
            ThisWorkbook.Worksheets(tabName).Range(cellAddr).Offset(0, 1).Value = _
                "[Hint " & level & "/" & maxHints & "] " & hintText
            MsgBox hintText, vbInformation, "Hint " & compId
            Exit Sub
        End If
    Next r
    MsgBox "Component not found: " & compId, vbExclamation
End Sub

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
            ThisWorkbook.Worksheets(tabName).Range(cellAddr).Interior.Color = RGB(230, 244, 234)
            UpdateStatus compId, "revealed"
            MsgBox "Formula inserted into " & tabName & "!" & cellAddr, vbInformation
            Exit Sub
        End If
    Next r
    MsgBox "Reference formula not found for " & compId, vbExclamation
End Sub

Private Sub UpdateStatus(compId As String, status As String)
    Dim meta As Worksheet
    Dim trainer As Worksheet
    Dim title As String
    Dim r As Long
    Set meta = ThisWorkbook.Worksheets(META_SHEET)
    For r = 2 To meta.Cells(meta.Rows.Count, 1).End(xlUp).Row
        If meta.Cells(r, 1).Value = compId Then
            meta.Cells(r, 9).Value = status
            title = meta.Cells(r, 5).Value
            Set trainer = ThisWorkbook.Worksheets(TRAINER_SHEET)
            For r = 5 To trainer.Cells(trainer.Rows.Count, 1).End(xlUp).Row
                If trainer.Cells(r, 2).Value = title Then
                    trainer.Cells(r, 5).Value = status
                    Exit Sub
                End If
            Next r
            Exit Sub
        End If
    Next r
End Sub
