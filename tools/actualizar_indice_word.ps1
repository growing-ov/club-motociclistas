$ErrorActionPreference = "Stop"
$rutas = @(
    "C:\Users\octavio.velazco\Music\python_u\club_motociclistas\docs\Club_de_Motociclistas_Documentacion.docx",
    "C:\Users\octavio.velazco\Music\python_u\club_motociclistas\docs\Club_de_Motociclistas_Tutorial.docx"
)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
foreach ($ruta in $rutas) {
    Write-Output "Procesando: $(Split-Path $ruta -Leaf)"
    $doc = $word.Documents.Open($ruta, $false, $false)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    $doc.Repaginate()
    Write-Output "  paginas: $($doc.ComputeStatistics(2)) | palabras: $($doc.ComputeStatistics(0)) | imagenes: $($doc.InlineShapes.Count)"
    $doc.Save()
    $doc.Close($false)
}
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Output "Listo (solo DOCX, sin PDF)"
