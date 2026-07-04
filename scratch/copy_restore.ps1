$sourceWebApp = 'C:\$Recycle.Bin\S-1-5-21-1246261140-2528540334-4027231117-1001\$R1VHN9J'
$destWebApp = "C:\Users\qamba\OneDrive\Desktop\realjarvis\web app"

$sourceFrontend = 'C:\$Recycle.Bin\S-1-5-21-1246261140-2528540334-4027231117-1001\$RDMWD0Y'

$destFrontend = "C:\Users\qamba\OneDrive\Desktop\realjarvis\frontend"

function Copy-ExcludeNodeModules($src, $dest) {
    if (!(Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }
    Get-ChildItem -Path $src -Force | Where-Object { $_.Name -ne "node_modules" -and $_.Name -ne ".next" } | ForEach-Object {
        $target = Join-Path $dest $_.Name
        if ($_.PSIsContainer) {
            Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
        } else {
            Copy-Item -Path $_.FullName -Destination $dest -Force
        }
    }
}

Write-Host "Restoring web app..."
Copy-ExcludeNodeModules -src $sourceWebApp -dest $destWebApp

Write-Host "Restoring frontend..."
Copy-ExcludeNodeModules -src $sourceFrontend -dest $destFrontend

Write-Host "Verification of restored items:"
Get-ChildItem -Path $destWebApp -Force | Select-Object Name
Get-ChildItem -Path $destFrontend -Force | Select-Object Name
