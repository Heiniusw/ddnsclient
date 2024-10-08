$IPAddress = Get-NetIPAddress -AddressFamily IPv6 | Where-Object {
    $_.AddressState -eq 'Preferred' -and
    $_.IPAddress -notmatch '^fe80' -and
    $_.IPAddress -notmatch '::1' -and
    $_.PrefixLength -gt 0
} | Select-Object -First 1

if ($IPAddress) {
    $ipv6Prefix = $IPAddress.IPAddress.Split(':') -join ':' -replace "(?<=::).*", "" -replace "(:0)+$", ":"
    Write-Host $ipv6Prefix
}