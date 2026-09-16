# Converts thesis/SVDS-Thesis.html into thesis/SVDS-Thesis.docx via Word COM
# automation, forcing all linked images to embed (Word links HTML <img> sources
# by default; without this step the resulting .docx is a few KB with broken
# image references instead of a real, portable document).
#
# Usage: powershell -ExecutionPolicy Bypass -File .\build_docx.ps1

$root = Split-Path $PSScriptRoot -Parent
$htmlPath = Join-Path $root "SVDS-Thesis.html"
$docxPath = Join-Path $root "SVDS-Thesis.docx"

Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Remove-Item $docxPath -ErrorAction SilentlyContinue

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($htmlPath, $false, $false, $false)
    Start-Sleep -Seconds 3

    $count = 0
    foreach ($shape in $doc.InlineShapes) {
        try {
            if ($shape.LinkFormat -ne $null) {
                $shape.LinkFormat.SavePictureWithDocument = $true
                $count++
            }
        } catch {}
    }
    Write-Host "Embedded $count linked images."

    $doc.SaveAs([ref]$docxPath, [ref]12)  # wdFormatXMLDocument = .docx
    $doc.Close()
    Write-Host "Saved $docxPath"
} finally {
    $word.Quit()
}
