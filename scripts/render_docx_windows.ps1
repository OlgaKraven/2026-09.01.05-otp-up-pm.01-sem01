param([string]$InputFolder='output/playwright',[string]$OutputFolder='output/docx-render',[switch]$SaveUpdatedFields)
$ErrorActionPreference='Stop'
$sourceFolder=(Resolve-Path -LiteralPath $InputFolder).Path
New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
$targetFolder=(Resolve-Path -LiteralPath $OutputFolder).Path
$wordInstance=New-Object -ComObject Word.Application
$wordInstance.Visible=$false
$wordInstance.DisplayAlerts=0
try {
 foreach($file in Get-ChildItem -LiteralPath $sourceFolder -Filter '*.docx') {
  $document=$wordInstance.Documents.Open($file.FullName,$false,(-not $SaveUpdatedFields))
  try {
   $document.Fields.Update() | Out-Null
   foreach($toc in $document.TablesOfContents) {$toc.Update()}
   if($SaveUpdatedFields) {$document.Save()}
   $pdf=Join-Path $targetFolder ($file.BaseName+'.pdf')
   $document.ExportAsFixedFormat($pdf,17)
   Write-Output $pdf
  } finally {$document.Close(0)}
 }
} finally {$wordInstance.Quit();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordInstance)}
