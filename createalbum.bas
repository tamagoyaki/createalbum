Const CHUNK As Integer = 3
Const ITOP As Integer = 2
Const ILEFT As integer = 2
Const IWIDTH As Integer  = 6
Const IHEIGHT As Integer = 11
Const GTOP As Integer = 2
Const GLEFT As Integer = 8
Const GWIDTH As Integer  = 3
Const GHEIGHT As Integer = 11
Const INTERMEDIATE As Integer  = 1

Private Sub deleteallimages()
   For Each img in ActiveSheet.Pictures
      img.Delete
   Next img
End Sub

Private Sub deleteallcontents()
   ActiveSheet.Cells.Clear
End Sub

'
' dig: 0, 90, 180, and 270 are available
'
Sub drawimage(cx, cy, cw, ch, file, dig)
   x = ActiveSheet.Cells(cy, cx).Left
   y = ActiveSheet.Cells(cy, cx).Top
   w = ActiveSheet.Cells(cy, cx).Width
   h = ActiveSheet.Cells(cy, cx).Height
   
   Set shp = ActiveSheet.Shapes.AddPicture(Filename := file, _
					   LinkToFile := False, _
					   SaveWithDocument := True, _
					   Left := x, Top := y, _
					   Width := 0, Height := 0)

   ' keep aspect ratio but height
   With shp
      .LockAspectRatio = msoTrue
      .ScaleHeight 1, msoTrue
      .ScaleWidth 1, msoTrue

      Select Case dig
	 Case 90, 270
	    .Width = ch * h
	    .Top = .Top + (h * 1.4)
	    .Left = .Left - (w * 0.46)
	 Case Is = 180
	    .Height = ch * h
	 Case Else
	    .Height = ch * h
	    dig = 0
      End Select
      
      .rotation = dig
   End With
End Sub

Sub drawgrid(cx, cy, cw, ch)
	' Range(Cells(raw, gcol), Cells(raw + hgrid - 1, gcol)) _
	'      .Borders(xlEdgeTop).LineStyle = xlDash
	Range(Cells(cy, cx), Cells(cy + ch -1, cx)) _
	     .Borders(xlInsideHorizontal).LineStyle = xlDash
	Range(Cells(cy, cx), Cells(cy + ch -1, cx)) _
	     .Borders(xlEdgeBottom).LineStyle = xlDash
End Sub

Sub drawtext(cx, cy, text)
   Range(Cells(cy, cx), Cells(cy, cx)).value = text
End Sub

Sub textformat(cx, cy, indlv, align)
   Range(Cells(cy, cx), Cells(cy, cx)).IndentLevel = indlv
   Range(Cells(cy, cx), Cells(cy, cx)).HorizontalAlignment = align
End Sub

Sub createalbum()
   ' position (cell base)
   top = ITOP

   ' print range
   index = 1
   Dim prange As Range
   Dim topleft As Range
   Set topleft = Cells(top, ILEFT)
   
   ' set grid cell width
   Columns(GLEFT).ColumnWidth = 3 * ActiveSheet.Cells(top, ILEFT).ColumnWidth
   deleteallimages
   deleteallcontents

   ' select file list
   Set fd = Application.FileDialog(msoFileDialogOpen)
   With fd
      .AllowMultiSelect = False
      .InitialFileName = "C:"
      .Filters.Add "photo list", "*.createalbum", 1
      If .Show <> -1 Then Exit Sub
   End With
    
   ' read selected file as CSV
   fnum = FreeFile
   Open fd.SelectedItems.Item(1) For Input As #fnum

   Do Until EOF(fnum)
      Line Input #fnum, record
      arry = split(record, ",")

      ' parse csv
      For i = 0 To UBound(arry)
	 s = Trim(arry(i))
	  
	 Select Case i
	    Case Is = 0
	       res = "src: " + s
	       filename = s
	       drawgrid GLEFT, top, GWIDTH, GHEIGHT
	    Case Is =1
	       res = "dig: " + s
       	       drawimage ILEFT, top, IWIDTH, IHEIGHT, filename, CInt(s)
	    Case else
	       res = "cmt: " + s
	       drawtext GLEFT, top + i - 2, s
	       textformat GLEFT, top + i - 2, 1, xlLeft
	 End Select

	 Debug.Print(res)
      Next

      ' print area
      If 0 = index Mod CHUNK Then
	 Dim r As Range
	 Set r = Range(topleft, Cells(top + IHEIGHT - 1, GLEFT))
	 
	 If CHUNK = index Then
	    Set prange = r
	 Else
	    Set prange = Union(prange, r)
	 End If
	 
	 Set topleft = Cells(top + IHEIGHT + INTERMEDIATE, ILEFT)
      End If

      ' next
      index = index + 1
      top = top + IHEIGHT + INTERMEDIATE
   Loop


   ' remaining ?
   If Not 0 = (index - 1) Mod CHUNK Then
      Set r = Range(topleft, Cells(top + IHEIGHT - 1, GLEFT))

      If CHUNK => index Then
	    Set prange = r
      Else
	    Set prange = Union(prange, r)
      End If
   End If

   prange.Name = "PrintArea"
   ActiveSheet.PageSetup.PrintArea = "PrintArea"
End Sub    
