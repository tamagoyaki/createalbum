Sub createalbum()
    Dim lngTop As Long
    Dim objFile As Object
    Dim objFldr As FileSystemObject

    ' select image folder
    Set fd = Application.FileDialog(msoFileDialogFolderPicker)
    With fd
       .AllowMultiSelect = False
       .InitialFileName = ThisWorkbook.Path
       If .Show <> -1 Then Exit Sub
    End With

    ' cell name base
    raw = 2
    icol = 2
    gcol = 9
    hgrid = 11
    himg = hgrid
    wimg = 6
    hblank = 1

    ' dot base
    wc = ActiveSheet.Cells(raw, icol).Width
    hc = ActiveSheet.Cells(raw, icol).Height
    wi = wimg * wc
    hi = himg * hc

    ' set grid cell width
    Columns(gcol).ColumnWidth = 3 * ActiveSheet.Cells(raw, icol).ColumnWidth

    ' dig into
    Set objFldr = CreateObject("Scripting.FileSystemObject")
 
    For Each objFile In objFldr.GetFolder(fd.SelectedItems.Item(1)).Files
       x = ActiveSheet.Cells(raw, icol).Left
       y = ActiveSheet.Cells(raw, icol).Top
       
       ' draw image
        ActiveSheet.Shapes.AddPicture _
                Filename:=objFile, _
                LinkToFile:=False, _
                SaveWithDocument:=True, _
                Left:=x, _
                Top:=y, _
                Width:=wi, _
                Height:=hi

	' draw grid
	' Range(Cells(raw, gcol), Cells(raw + hgrid - 1, gcol)) _
	'      .Borders(xlEdgeTop).LineStyle = xlDash
	Range(Cells(raw, gcol), Cells(raw + hgrid - 1, gcol)) _
	     .Borders(xlInsideHorizontal).LineStyle = xlDash
	Range(Cells(raw, gcol), Cells(raw + hgrid - 1, gcol)) _
	     .Borders(xlEdgeBottom).LineStyle = xlDash

	' next
	raw = raw + himg + hblank
    Next
 
End Sub