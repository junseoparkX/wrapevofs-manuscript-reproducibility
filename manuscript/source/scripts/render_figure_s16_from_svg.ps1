$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot 'figure_s16_render_wrapper.html')).Path
$output = Join-Path $root 'figures\figure_s16.pdf'
$pngStem = Join-Path $root 'figures\figure_s16'
$chrome = (Get-Command chrome.exe -ErrorAction SilentlyContinue).Source
if (-not $chrome) {
    $chrome = Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'
}
$pdftoppm = (Get-Command pdftoppm -ErrorAction Stop).Source

foreach ($path in @($chrome, $pdftoppm)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required renderer not found: $path"
    }
}
if (-not $output.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside the manuscript source directory: $output"
}

$uri = ([Uri]$wrapper).AbsoluteUri
$arguments = @(
    '--headless=new',
    '--disable-gpu',
    '--no-pdf-header-footer',
    "--print-to-pdf=$output",
    $uri
)
$process = Start-Process -FilePath $chrome -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0) {
    throw "Chrome SVG-to-PDF rendering failed with exit code $($process.ExitCode)"
}

& $pdftoppm -singlefile -png -r 300 $output $pngStem
if ($LASTEXITCODE -ne 0) {
    throw "PDF-to-PNG rendering failed with exit code $LASTEXITCODE"
}

Get-FileHash -LiteralPath $output, (Join-Path $root 'figures\figure_s16.png') -Algorithm SHA256
