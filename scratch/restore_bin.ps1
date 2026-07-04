$sh = New-Object -ComObject Shell.Application
$bin = $sh.Namespace(0xa)
$items = $bin.Items() | Where-Object { $_.Name -eq "web app" -or $_.Name -eq "frontend" }
foreach ($item in $items) {
    Write-Host "Restoring: $($item.Name)"
    $item.InvokeVerb("R&estore")
}
Write-Host "Restore complete."

