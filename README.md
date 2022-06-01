# basic_zoom


## Package Installation

```bash
pip install basic-zoom
```

## Example Package Usage JWT

```
from basic_zoom import ZoomAPIClient

zoomapi = ZoomAPIClient(
    API_KEY=" <Zoom API KEY here> ", API_SECRET=" <Zoom API Secret here>  "
)

result = zoomapi.get(endpoint_url="/phone/call_logs")
```


## Example Package Usage Server-to-Server app

```
from basic_zoom import ZoomAPIClient

zoomapi = ZoomAPIClient(
    ACCOUNT_ID=" <Zoom Account ID here> ",
    S2S_CLIENT_ID=" <Zoom S2S App Client ID here> ",
    S2S_CLIENT_SECRET=" <Zoom S2S App Client Secret here> ",)

result = zoomapi.get(endpoint_url="/phone/call_logs")
```

