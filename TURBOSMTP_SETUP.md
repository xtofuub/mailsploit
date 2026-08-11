# TurboSMTP API mode setup

The API-mode sender uses TurboSMTP V2 and keeps credentials on the server instead of storing them in browser localStorage.

## 1. Rotate exposed credentials

If a Consumer Secret has ever been pasted into chat, a public issue, a commit, a screenshot, or another untrusted location, revoke that Consumer Key / Secret pair in TurboSMTP and create a new pair before deploying.

Do not commit the replacement credentials to this repository.

## 2. Configure Vercel environment variables

Set these variables in the Vercel project for the environment(s) you use:

- `TURBOSMTP_CONSUMER_KEY` — the newly generated Consumer Key.
- `TURBOSMTP_CONSUMER_SECRET` — the newly generated Consumer Secret.
- `TURBOSMTP_FROM_EMAIL` — a sender email address you control and have configured for sending.
- `TURBOSMTP_REGION` — `eu` for EU sending infrastructure or `global` for non-EU/global infrastructure.
- `TURBOSMTP_ALLOWED_RECIPIENTS` — comma-separated test inboxes that this deployment is allowed to send to.

Example values (placeholders only):

```text
TURBOSMTP_CONSUMER_KEY=replace-me
TURBOSMTP_CONSUMER_SECRET=replace-me
TURBOSMTP_FROM_EMAIL=security-test@example.com
TURBOSMTP_REGION=eu
TURBOSMTP_ALLOWED_RECIPIENTS=security-inbox@example.com,qa@example.com
```

Redeploy after changing environment variables.

## 3. API-mode behavior

`POST /send_email` is routed through `api/send_email_safe.py` when the form uses API mode. The handler:

- reads TurboSMTP credentials only from server environment variables;
- sends only from `TURBOSMTP_FROM_EMAIL`;
- sends only to recipients in `TURBOSMTP_ALLOWED_RECIPIENTS`;
- uses the documented TurboSMTP V2 `from` email format;
- sends `custom_headers` as a JSON object;
- supports EU and global TurboSMTP send endpoints;
- returns provider status details without leaking credentials;
- disables attachments in this controlled API path.

SMTP mode continues to use the existing Flask handler.

## Troubleshooting

- `503 TurboSMTP credentials are not configured`: add the Consumer Key and Secret environment variables, then redeploy.
- `503 Set TURBOSMTP_FROM_EMAIL`: configure the sender environment variable.
- `503 Set TURBOSMTP_ALLOWED_RECIPIENTS`: configure at least one controlled test inbox.
- `400 API mode is configured to send only from ...`: make the From field match `TURBOSMTP_FROM_EMAIL`.
- `403 Recipient is not in TURBOSMTP_ALLOWED_RECIPIENTS`: add the controlled test inbox to the environment variable and redeploy.
- `TurboSMTP API error 401`: the key/secret pair is invalid, revoked, or not accepted for that account.
- `TurboSMTP API error 500`: retry using the correct `TURBOSMTP_REGION`; if it persists with a minimal valid payload, check TurboSMTP service/account status.
