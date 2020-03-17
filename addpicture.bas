Sub ‰æ‘œ“\‚è•t‚¯()
Dim lngTop As Long
Dim objFile As Object
Dim objFldr As FileSystemObject
 
    Set objFldr = CreateObject("Scripting.FileSystemObject")
 
    lngTop = 20
    
    For Each objFile In objFldr.GetFolder(ThisWorkbook.Path & "\images").Files
        ActiveSheet.Shapes.AddPicture _
                Filename:=objFile, _
                LinkToFile:=False, _
                SaveWithDocument:=True, _
                Left:=20, _
                Top:=lngTop, _
                Width:=300, _
                Height:=200
        
        lngTop = lngTop + 200 + 20
    
    Next
 
End Sub