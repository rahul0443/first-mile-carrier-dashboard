' Auto-Refresh Macro for Pivot Pack
' Purpose: Refreshes all pivot tables and saves the workbook.
' Usage: Import this .bas file into the Excel VBA editor (Alt+F11 > File > Import)
'        then run RefreshAllPivots from the Macros menu (Alt+F8).
'
' Note: This macro assumes the pivot_pack.xlsx workbook is open.
' It iterates all worksheets and refreshes any PivotTable objects found.

Sub RefreshAllPivots()
    Dim ws As Worksheet
    Dim pt As PivotTable
    Dim ptCount As Integer
    
    ptCount = 0
    
    ' Iterate all worksheets in the active workbook
    For Each ws In ThisWorkbook.Worksheets
        For Each pt In ws.PivotTables
            pt.RefreshTable
            ptCount = ptCount + 1
        Next pt
    Next ws
    
    ' Save after refresh
    ThisWorkbook.Save
    
    MsgBox "Refreshed " & ptCount & " pivot table(s) and saved.", vbInformation, "Pivot Refresh Complete"
End Sub

Sub AutoRefreshOnOpen()
    ' Call this from Workbook_Open event to auto-refresh on file open.
    ' To set up: In VBA editor, double-click "ThisWorkbook" in the Project Explorer,
    ' then add:
    '   Private Sub Workbook_Open()
    '       Call RefreshAllPivots
    '   End Sub
    Call RefreshAllPivots
End Sub
