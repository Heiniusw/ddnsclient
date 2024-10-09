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

try {

    [xml]$response = Invoke-RestMethod -Uri "http://${fritzboxip}:49000/igdupnp/control/WANIPConn1" -Method Post -Headers $headers -Body $body
    $externalIp = $response.Envelope.Body.GetExternalIPAddressResponse.NewExternalIPAddress
    if ($externalIp -match '\b\d{1,3}(.\d{1,3}){3}\b') {
        Write-Output $externalIp  # Output the external IP address
    } else {
        exit 0  # No IP found, exit gracefully
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1  # Return a non-zero exit code to indicate failure
}