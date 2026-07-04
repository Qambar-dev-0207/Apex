$sh = New-Object -ComObject Shell.Application
$bin = $sh.Namespace(0xa)
$bin.Items() | ForEach-Object {
    [PSCustomObject]@{
        Name             = $_.Name
        Path             = $_.Path
        OriginalLocation = $bin.GetDetailsOf($_, 1)
    }
} | Format-List
