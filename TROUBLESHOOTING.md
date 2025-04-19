# Troubleshooting Email Sending Issues

This guide will help you diagnose and fix common issues when sending emails with the spoofing tool.

## Testing SMTP Servers

Before attempting to send an email, it's recommended to validate that your SMTP servers are working:

```bash
# Test all servers in your file
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --test-only --show-errors

# Test a specific server
python advanced_email_spoofer.py --server smtp.example.com --port 587 --user user@example.com --password your-password --test-only --show-errors
```

## Validating Full Sending Capability

Testing SMTP login is not enough - some servers may allow login but restrict sending to external addresses or have other limitations. To fully validate sending capability:

```bash
# Test sending to yourself first
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --validate-sending --test-email your-own-email@example.com --test-only
```

## Common Error Messages and Solutions

### Authentication Failed

Error: `Authentication failed`, `535 5.7.8 Authentication credentials invalid`

Solutions:
- Double-check your username and password
- For Gmail, use an App Password instead of your regular password
- Make sure the account hasn't been locked for security reasons
- Try logging into the email account via web browser to confirm it's active

### Sender Address Rejected

Error: `Sender address rejected`, `501 5.1.7 Invalid address`

Solutions:
- Some SMTP servers only allow sending from the authenticated email address
- Try setting the `--from-email` to be the same as the SMTP username
- Check if the account has sending restrictions or is in a probation period

### Relay Denied

Error: `Relay access denied`, `550 5.7.1 Relaying denied`

Solutions:
- Many SMTP providers restrict sending to certain domains or addresses
- The server may only allow sending to recipients in the same domain
- Try sending to a recipient in the same domain as the SMTP server first

### Account Blocked/Suspended

Error: `Account suspended`, `Your email access has been blocked`

Solutions:
- The account may have been blocked due to suspicious activity
- Contact the email provider to reactivate the account
- Use a different SMTP server

## Improving Success Rate

1. **Use Your Own SMTP Accounts**: Using your own legitimate SMTP accounts will provide the highest success rate.

2. **Avoid Free Email Providers**: Gmail, Yahoo, and other major providers have strict anti-spoofing measures. Consider using a paid SMTP service like SendGrid, Mailgun, or Amazon SES.

3. **Increase Max Attempts**: Use the `--max-attempts` option to try more servers:
   ```bash
   python advanced_email_spoofer.py --smtp-file smtp_servers.txt --max-attempts 20 --from-name "Example" --from-email example@example.com --to recipient@example.com --subject "Test" --message "Test"
   ```

4. **Save Working Servers**: Once you find working servers, save them for future use:
   ```bash
   python advanced_email_spoofer.py --smtp-file smtp_servers.txt --test-only --save-working working_servers.txt
   ```

5. **Try Different Recipients**: Some email providers may block emails to certain domains. Try sending to different email providers (Gmail, Yahoo, Outlook, etc.).

## Testing Your Configuration

Always test your configuration with a simple message before sending important emails:

```bash
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --from-name "Test" --from-email test@example.com --to your-own-email@example.com --subject "Test" --message "This is a test message" --show-errors
```

## Advanced Debugging

For detailed debugging information, use the `--debug` option:

```bash
python advanced_email_spoofer.py --smtp-file smtp_servers.txt --from-name "Test" --from-email test@example.com --to recipient@example.com --subject "Test" --message "Test" --debug 2
```

This will show the full SMTP conversation, including all commands and responses. 