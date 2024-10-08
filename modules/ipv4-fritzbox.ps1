$FritzBoxIp = "192.168.188.1"

$headers = @{
    "Content-Type" = "text/xml; charset=utf-8"
    "SoapAction"   = "urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress"
}

$body = @"
<?xml version='1.0' encoding='utf-8'?>
<s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'>
  <s:Body>
    <u:GetExternalIPAddress xmlns:u='urn:schemas-upnp-org:service:WANIPConnection:1' />
  </s:Body>
</s:Envelope>
"@

$response = Invoke-RestMethod -Uri "http://${FritzBoxIp}:49000/igdupnp/control/WANIPConn1" -Method Post -Headers $headers -Body $body

if ($response -match '\b\d{1,3}(\.\d{1,3}){3}\b') {
    Write-Host $matches[0]
}
