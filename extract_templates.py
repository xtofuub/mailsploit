import os
import re

# Mapping of PhishMailer function names to our internal template keys
# Internal key: (Source File, Function Name in PhishMailer)
mapping = {
    "instagram": ("eletter.py", "Instagram"),
    "facebook": ("eletter.py", "Facebook"),
    "gmail": ("eletter.py", "Gmail"),
    "gmail_simple": ("eletter.py", "GmailActivity"),
    "twitter": ("eletter.py", "Twitter"),
    "snapchat": ("ipmenu.py", "Snapchat"),
    "snapchat_simple": ("eletter.py", "SnapchatSimple"),
    "steam": ("eletter.py", "Steam"),
    "dropbox": ("devicemenu.py", "Dropbox"),
    "linkedin": ("devicemenu.py", "Linkedin"),
    "playstation": ("eletter.py", "Playstation"),
    "paypal": ("ipmenu.py", "Paypal1"),
    "discord": ("ipmenu.py", "Discord"),
    "spotify": ("eletter.py", "Spotify"),
    "blockchain": ("eletter.py", "Blockchain"),
    "riotgames": ("eletter.py", "RiotGames"),
    "rockstar": ("eletter.py", "Rockstar"),
    "askfm": ("eletter.py", "AskFM"),
    "000webhost": ("eletter.py", "Webhost000"),
    "dreamteam": ("eletter.py", "Dreamteam"),
    "gamehag": ("eletter.py", "Gamehag"),
    "mega": ("eletter.py", "Mega"),
}

core_path = r"C:\Users\Edwinn\Desktop\PhishMailer-master\Core"
output_file = r"C:\Users\Edwinn\Desktop\mailsploit-main\phish_templates.py"

templates = {}

for internal_key, (filename, func_name) in mapping.items():
    fpath = os.path.join(core_path, filename)
    if not os.path.exists(fpath):
        print(f"Warning: {filename} not found.")
        continue
        
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Search for the function definition and its docstring/string literal
    # Pattern: def FuncName(): ... """content""" or '''content'''
    pattern = rf'def\s+{func_name}\s*\(\)\s*:.*?["\']{{3}}(.*?)["\']{{3}}'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        templates[internal_key] = match.group(1).strip()
    else:
        print(f"Warning: Could not extract template for {func_name} in {filename}")

with open(output_file, "w", encoding="utf-8") as out:
    out.write('"""\nPhishing Templates Extracted from PhishMailer\n"""\n\n')
    out.write("PHISH_TEMPLATES = {\n")
    for k, v in templates.items():
        # Clean up the template: replace placeholders if necessary
        # Most PhishMailer templates use {} for values
        out.write(f'    "{k}": r\'\'\'{v}\'\'\',\n')
    out.write("}\n")

print(f"Successfully extracted {len(templates)} templates to {output_file}")
