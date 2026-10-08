# Binary request replay

Use this reference when a real API or CLI request reads a local binary or image, constructs a request through shell tools, sends it, and displays the response.

Derive commands from the real API contract and project files, then execute the complete pipeline one prompt cycle at a time. A typical planning structure is:

```sh
IMAGE_PATH=/real/path/to/image.png
IMAGE_DATA=$(base64 < "$IMAGE_PATH" | tr -d '\n')
jq --arg image_url "data:image/png;base64,$IMAGE_DATA" \
  '<verified filter for the real request schema>' request.json > request.with-image.json
curl <verified options and endpoint> --data-binary @request.with-image.json > response.json
jq . response.json
```

Resolve every placeholder, MIME type, request field, option, and endpoint before execution. Only commands successfully tested against the real source files and API may enter the evidence manifest or replay.

Preserve variable assignments, redirection, quoting, pipes, expansion, tool errors, and prompt returns. Display the response inside the terminal as the actual text or `jq`-formatted JSON. A card, dashboard, table UI, image layout, or other designed interpretation belongs to a subsequent non-terminal scene sourced from `response.json` or the corresponding captured evidence.
