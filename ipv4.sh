#! /bin/bash

wget -qO- "http://fritz.box:49000/igdupnp/control/WANIPConn1" --header "Content-Type: text/xml; charset="utf-8"" --header "SoapAction:urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress" --post-data="<?xml version='1.0' encoding='utf-8'?> <s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'> <s:Body> <u:GetExternalIPAddress xmlns:u='urn:schemas-upnp-org:service:WANIPConnection:1' /> </s:Body> </s:Envelope>"  | grep -Eo '\<[[:digit:]]{1,3}(\.[[:digit:]]{1,3}){3}\>'
