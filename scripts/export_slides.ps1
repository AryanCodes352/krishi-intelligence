$ppt = New-Object -ComObject PowerPoint.Application
$pptPath = "C:\Users\aryan\Desktop\KRISHI\docs\KRISHI_Intelligence_KCC_Presentation.pptx"
$outDir = "C:\Users\aryan\Desktop\KRISHI\docs\slides_preview"
if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
$pres = $ppt.Presentations.Open($pptPath, -1, 0, 0)
$pres.SaveAs($outDir, 18) # 18 = ppSaveAsPNG
$pres.Close()
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
Get-ChildItem $outDir
