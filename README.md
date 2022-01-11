# basic_zoom


## Package Installation

```bash
pip install basic-zoom
```

## Example Package Usage

```
from basic_zoom import ZoomAPIClient

zoomapi = ZoomAPIClient(
    API_KEY=" <Zoom API KEY here> ", API_SECRET=" <Zoom API Secret here>  "
)

result = zoomapi.get(endpoint_url="/phone/call_logs")
```