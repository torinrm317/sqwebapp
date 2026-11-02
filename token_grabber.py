
import json
from pathlib import Path
from urllib.parse import urlsplit

from mitmproxy import http, ctx

URL_PREFIX = SQUID_API_URL

# Output file: one matching response per line.
OUTPUT_FILE = Path.home() / "sqwebapp" / "mitm_get_results.jsonl"

class GetFilter:
    def response(self, flow: http.HTTPFlow):
        req = flow.request

        # Only capture GET requests.
        if req.method != "GET":
            return

        # Match the URL exactly, ignoring query parameters.
        request_base = req.pretty_url.split("?", 1)[0]

        if request_base != URL_PREFIX:
            return

        if flow.response is None:
            return

        # Extract the bearer token from the request header.
        auth_header = req.headers.get("Authorization", "")
        bearer_token = None

        if auth_header.startswith("Bearer "):
            bearer_token = auth_header[len("Bearer "):]


        response = flow.response

        result = {
            "method": req.method,
            "url": request_base,
            "status": response.status_code,
            "content_type": response.headers.get(
                "content-type", ""
            ),
            "bearer_token": bearer_token,
        }

        try:
            body = json.loads(response.get_content() or b"null")
            result["response_json"] = body
        except (ValueError, UnicodeDecodeError, TypeError):
            result["response_json"] = None

        try:
            with OUTPUT_FILE.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(result, ensure_ascii=False) + "\n"
                )

            ctx.log.info(
                f"Saved matching GET response: {request_base}"
            )

        except OSError as exc:
            ctx.log.error(f"Could not write output file: {exc}")


addons = [GetFilter()]
