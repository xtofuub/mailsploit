"""Dedicated TurboSMTP API-mode handler for Vercel.

API credentials are supplied by the browser for each request. They are not
stored in Vercel environment variables or persisted by this handler. SMTP mode
is delegated to the legacy Flask handler so existing non-API behavior remains
unchanged.
"""

import os
from importlib import import_module

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

TURBOSMTP_ENDPOINTS = {
    "eu": "https://api.eu.turbo-smtp.com/api/v2/mail/send",
    "global": "https://api.turbo-smtp.com/api/v2/mail/send",
    "non-eu": "https://api.turbo-smtp.com/api/v2/mail/send",
}


def _request_payload():
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return request.form.to_dict(flat=True)


def _split_addresses(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _provider_error(response):
    """Return a useful provider error without leaking request credentials."""
    try:
        body = response.json()
    except Exception:
        text = (response.text or "").strip()
        return text[:500] or f"HTTP {response.status_code}"

    if not isinstance(body, dict):
        return str(body)[:500]

    message = str(body.get("message") or body.get("error") or "error")
    errors = body.get("errors")
    if errors:
        if isinstance(errors, list):
            flat = []
            for item in errors:
                if isinstance(item, list):
                    flat.extend(str(v) for v in item)
                else:
                    flat.append(str(item))
            if flat:
                message += ": " + "; ".join(flat)
        elif isinstance(errors, dict):
            message += ": " + str(errors.get("errors") or errors.get("message") or errors)
        else:
            message += ": " + str(errors)

    return message[:500]


def _delegate_legacy_send():
    legacy = import_module("app")
    return legacy.send_email()


def _json_response(payload, status=200):
    response = jsonify(payload)
    # Avoid caches retaining request-correlated API responses.
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response, status


@app.route("/send_email", methods=["POST"])
def send_email():
    payload = _request_payload()
    send_mode = str(payload.get("send_mode") or "smtp").strip().lower()

    # Preserve the existing SMTP handler. This file only replaces API mode.
    if send_mode != "api":
        return _delegate_legacy_send()

    # Each browser supplies its own TurboSMTP credentials. Nothing is read from
    # shared Vercel secrets, so one public deployment can serve multiple users.
    consumer_key = str(payload.get("consumer_key") or "").strip()
    consumer_secret = str(payload.get("consumer_secret") or "").strip()
    region = str(payload.get("api_region") or "eu").strip().lower()

    if not consumer_key or not consumer_secret:
        return _json_response({
            "success": False,
            "error": "Enter your TurboSMTP Consumer Key and Consumer Secret in API Mode.",
        }, 400)

    if region not in TURBOSMTP_ENDPOINTS:
        return _json_response({
            "success": False,
            "error": "API region must be 'eu' or 'global'.",
        }, 400)

    from_email = str(payload.get("from_email") or "").strip()
    if not from_email or "@" not in from_email:
        return _json_response({
            "success": False,
            "error": "Enter a valid From Email for the TurboSMTP account.",
        }, 400)

    # Keep the dedicated API path intentionally simple. Attachments remain on
    # the legacy SMTP path until they can be handled without retaining secrets
    # or uploaded data beyond the current request.
    if request.files:
        return _json_response({
            "success": False,
            "error": "Attachments are not supported in API Mode yet.",
        }, 400)

    to_list = _split_addresses(payload.get("to_email"))
    cc_list = _split_addresses(payload.get("cc"))
    bcc_list = _split_addresses(payload.get("bcc"))
    recipients = to_list + cc_list + bcc_list

    if not to_list:
        return _json_response({"success": False, "error": "At least one recipient is required."}, 400)

    # Optional deployment-owner safety policy. If set, it still works exactly
    # as before; if omitted, the user's own TurboSMTP account controls sending.
    allowed_raw = os.environ.get("TURBOSMTP_ALLOWED_RECIPIENTS", "").strip()
    if allowed_raw:
        allowed = {addr.casefold() for addr in _split_addresses(allowed_raw)}
        blocked = [addr for addr in recipients if addr.casefold() not in allowed]
        if blocked:
            return _json_response({
                "success": False,
                "error": "Recipient is not allowed by this deployment.",
            }, 403)

    subject = str(payload.get("subject") or "")
    content = str(payload.get("message") or "")
    html = str(payload.get("html") or "").strip().lower() in {"1", "true", "yes", "on"}
    reply_to = str(payload.get("reply_to") or "").strip()

    # TurboSMTP V2 expects a plain email address in `from`, not
    # "Display Name <address>".
    api_payload = {
        "from": from_email,
        "to": ",".join(to_list),
        "subject": subject,
        "content": content,
    }
    if html:
        api_payload["html_content"] = content
    if cc_list:
        api_payload["cc"] = ",".join(cc_list)
    if bcc_list:
        api_payload["bcc"] = ",".join(bcc_list)
    if reply_to:
        # V2 expects custom_headers as an object/map.
        api_payload["custom_headers"] = {"Reply-To": reply_to}

    headers = {
        "Accept": "application/json",
        "consumerKey": consumer_key,
        "consumerSecret": consumer_secret,
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        response = requests.post(
            TURBOSMTP_ENDPOINTS[region],
            json=api_payload,
            headers=headers,
            timeout=20,
        )
    except requests.RequestException as exc:
        return _json_response({
            "success": False,
            "error": f"TurboSMTP connection failed: {exc}",
        }, 502)

    if response.status_code in {200, 201, 202}:
        try:
            data = response.json()
        except Exception:
            data = {}
        return _json_response({
            "success": True,
            "message": "Email accepted by TurboSMTP",
            "mid": data.get("mid") if isinstance(data, dict) else None,
        })

    return _json_response({
        "success": False,
        "error": f"TurboSMTP API error {response.status_code}: {_provider_error(response)}",
        "provider_status": response.status_code,
    }, 502)
