$ppt = New-Object -ComObject PowerPoint.Application
$pptPath = "C:\Users\aryan\Desktop\KRISHI\docs\KRISHI_Intelligence_KCC_Presentation.pptx"
$pdfPath = "C:\Users\aryan\Desktop\KRISHI\docs\KRISHI_Intelligence_KCC_Presentation.pdf"

$pres = $ppt.Presentations.Open($pptPath, -1, 0, 0)
$pres.SaveAs($pdfPath, 32) # 32 = ppSaveAsPDF
$pres.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null

Get-Item $pdfPath
