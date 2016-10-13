# nukiproxy
A simple proxy to sit between the Nuki bridge and openHAB (since the openHAB REST API requires `Content-Type=text/plain` but Nuki sends `application/json`)

Copy `nukiproxy.ini.example` -> `nukiproxy.ini` and update with your settings.

Run via `python nukiproxy.py`.

Configure your Nuki bridge callback URL to point to `nukiproxy`.

NOTE: as of v1.3.5 of the Nuki bridge firmware the callback will fail if the `nukiproxy` has an endpoint other than `/`.
