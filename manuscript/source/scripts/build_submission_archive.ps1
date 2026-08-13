param(
    [string]$SourceRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputZip = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'WrapEvoFS_manuscript_submission.zip')
)

$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$output = [System.IO.Path]::GetFullPath($OutputZip)
$expectedParent = (Resolve-Path -LiteralPath (Split-Path -Parent $source)).Path
if (-not $output.StartsWith($expectedParent + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside the manuscript directory: $output"
}

$excludedDirectories = @('.tex-cache', '.tmp', 'tmp', '__pycache__', 'qa_postfreeze')
$excludedSuffixes = @(
    '.aux', '.bbl', '.blg', '.fdb_latexmk', '.fls', '.log', '.out',
    '.synctex.gz', '.pyc'
)
$fixedTimestamp = [System.DateTimeOffset]::Parse('2026-08-10T00:00:00-07:00')
$temporary = $output + '.building'

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

if ([System.IO.File]::Exists($temporary)) {
    [System.IO.File]::Delete($temporary)
}

$files = Get-ChildItem -LiteralPath $source -File -Recurse -Force | Where-Object {
    $relative = $_.FullName.Substring($source.Length).TrimStart([char[]]@('\', '/')).Replace('\', '/')
    $segments = $relative.Split('/')
    $directoryExcluded = @($segments | Where-Object { $excludedDirectories -contains $_ }).Count -gt 0
    $suffixExcluded = $false
    foreach ($suffix in $excludedSuffixes) {
        if ($relative.EndsWith($suffix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $suffixExcluded = $true
            break
        }
    }
    $buildLogExcluded = $_.Name -like 'build-*.log'
    -not ($directoryExcluded -or $suffixExcluded -or $buildLogExcluded)
} | Sort-Object FullName

$stream = [System.IO.File]::Open($temporary, [System.IO.FileMode]::CreateNew)
try {
    $archive = [System.IO.Compression.ZipArchive]::new(
        $stream,
        [System.IO.Compression.ZipArchiveMode]::Create,
        $false
    )
    try {
        foreach ($file in $files) {
            $relative = $file.FullName.Substring($source.Length).TrimStart([char[]]@('\', '/')).Replace('\', '/')
            $entry = $archive.CreateEntry($relative, [System.IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = $fixedTimestamp
            $entryStream = $entry.Open()
            $inputStream = [System.IO.File]::OpenRead($file.FullName)
            try {
                $inputStream.CopyTo($entryStream)
            }
            finally {
                $inputStream.Dispose()
                $entryStream.Dispose()
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}
finally {
    $stream.Dispose()
}

if ([System.IO.File]::Exists($output)) {
    [System.IO.File]::Delete($output)
}
[System.IO.File]::Move($temporary, $output)

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $output).Hash.ToLowerInvariant()
[pscustomobject]@{
    Output = $output
    Files = $files.Count
    Bytes = (Get-Item -LiteralPath $output).Length
    SHA256 = $hash
}
