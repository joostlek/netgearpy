"""Constants for NetgearPy."""

ENVELOPE = """<!--?xml version="1.0" encoding= "UTF-8" ?-->
<v:Envelope
xmlns:v="http://schemas.xmlsoap.org/soap/envelope/">
<v:Header>
<SessionID>A7D88AE69687E58D9A00</SessionID>
</v:Header>
<v:Body>
{}
</v:Body>
</v:Envelope>"""


LOGIN_BODY = """<M1:SOAPLogin xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<Username>{}</Username><Password>{}</Password></M1:SOAPLogin>"""

GET_ATTACHED_DEVICES_BODY = (
    """<M1:GetAttachDevice xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceInfo:1" />"""
)
