"""Dedicated TurboSMTP API-mode handler for Vercel.

This route keeps API credentials server-side and only sends from/to addresses
explicitly configured by the deployment owner. SMTP mode is delegated to the
legacy Flask handler so existing non-API behavior is unchanged.
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


@app.route("/send_email", methods=["POST"])
def send_email():
    payload = _request_payload()
    send_mode = str(payload.get("send_mode") or "smtp").strip().lower()

    # Preserve the existing SMTP handler. This file only replaces API mode.
    if send_mode != "api":
        return _delegate_legacy_send()

    consumer_key = os.environ.get("TURBOSMTP_CONSUMER_KEY", "").strip()
    consumer_secret = os.environ.get("TURBOSMTP_CONSUMER_SECRET", "").strip()
    configured_from = os.environ.get("TURBOSMTP_FROM_EMAIL", "").strip()
    region = os.environ.get("TURBOSMTP_REGION", "eu").strip().lower()
    allowed_raw = os.environ.get("TURBOSMTP_ALLOWED_RECIPIENTS", "").strip()

    if not consumer_key or not consumer_secret:
        return jsonify({
            "success": False,
            "error": "TurboSMTP credentials are not configured on the server. Set TURBOSMTP_CONSUMER_KEY and TURBOSMTP_CONSUMER_SECRET.",
        }), 503

    if not configured_from:
        return jsonify({
            "success": False,
            "error": "Set TURBOSMTP_FROM_EMAIL to a sender address you control and have configured for sending.",
        }), 503

    if region not in TURBOSMTP_ENDPOINTS:
        return jsonify({
            "success": False,
            "error": "TURBOSMTP_REGION must be 'eu' or 'global'.",
        }), 503

    # This dedicated route is intentionally a controlled test sender. It does
    # not accept arbitrary sender identities from the browser.
    requested_from = str(payload.get("from_email") or "").strip()
    if requested_from and requested_from.casefold() != configured_from.casefold():
        return jsonify({
            "success": False,
            "error": f"API mode is configured to send only from {configured_from}.",
        }), 400

    if request.files:
        return jsonify({
            "success": False,
            "error": "Attachments are disabled in the controlled API sender.",
        }), 400

    to_list = _split_addresses(payload.get("to_email"))
    cc_list = _split_addresses(payload.get("cc"))
    bcc_list = _split_addresses(payload.get("bcc"))
    recipients = to_list + cc_list + bcc_list

    if not to_list:
        return jsonify({"success": False, "error": "At least one recipient is required."}), 400

    if not allowed_raw:
        return jsonify({
            "success": False,
            "error": "Set TURBOSMTP_ALLOWED_RECIPIENTS to the comma-separated test inboxes this deployment may send to.",
        }), 503

    allowed = {addr.casefold() for addr in _split_addresses(allowed_raw)}
    blocked = [addr for addr in recipients if addr.casefold() not in allowed]
    if blocked:
        return jsonify({
            "success": False,
            "error": "Recipient is not in TURBOSMTP_ALLOWED_RECIPIENTS.",
        }), 403

    subject = str(payload.get("subject") or "")
    content = str(payload.get("message") or "")
    html = str(payload.get("html") or "").strip().lower() in {"1", "true", "yes", "on"}
    reply_to = str(payload.get("reply_to") or "").strip()

    # TurboSMTP V2 documents `from` as a valid email address. Do not send a
    # display-name form such as "Name <address>" here.
    api_payload = {
        "from": configured_from,
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
        # V2 expects custom_headers as an object/map, not a list of header/value objects.
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
        return jsonify({
            "success": False,
            "error": f"TurboSMTP connection failed: {exc}",
        }), 502

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception:
            data = {}
        return jsonify({
            "success": True,
            "message": "Email accepted by TurboSMTP",
            "mid": data.get("mid") if isinstance(data, dict) else None,
        })

    # Translate provider failures into a gateway error while preserving the
    # provider status/message for debugging. A TurboSMTP HTTP 500 is therefore
    # no longer shown as an unexplained application 500.
    return jsonify({
        "success": False,
        "error": f"TurboSMTP API error {response.status_code}: {_provider_error(response)}",
        "provider_status": response.status_code,
    }), 502
