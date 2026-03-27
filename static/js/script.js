/* Mailsploit — Monochrome UI Logic */

// ── Navigation ────────────────────────────────────────────
function closeMobileMenu() {
    const overlay = document.getElementById('sheet-overlay');
    const content = document.getElementById('sheet-content');
    if (overlay) overlay.classList.remove('show');
    if (content) content.classList.remove('show');
    document.body.style.overflow = '';
}

function goHome() {
    const el = document.getElementById('section-home');
    closeMobileMenu();
    
    if (el) {
        document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
        el.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        window.location.href = '/';
    }
}

function scrollToSection(id) {
    const home = document.getElementById('section-home');
    closeMobileMenu();

    if (home) {
        document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
        home.classList.add('active');
        setTimeout(() => {
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
    } else {
        window.location.href = '/#' + id;
    }
}

function switchSection(id) {
    const el = document.getElementById('section-' + id);
    closeMobileMenu();

    if (el) {
        document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
        el.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Sync SMTP fields if applicable
        if (id === 'test') {
            ['smtp_server', 'smtp_port', 'username', 'password'].forEach(f => {
                const s = document.getElementById(f), t = document.getElementById('test_' + f);
                if (s && t) t.value = s.value;
            });
        }
    } else {
        window.location.href = '/#section-' + id;
    }
}

// ── Shortcuts ─────────────────────────────────────────────
document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.key.toLowerCase() === 's') {
        e.preventDefault();
        switchSection('send');
        toast('Switched to Send Email', 'ok');
    }
});

function pushToEmail(code) {
    const msg = document.getElementById('message');
    if (msg) {
        msg.value = code;
        switchSection('send');
        toast('Pushed to Send Email', 'ok');
    }
}

async function applyForgeToEmail() {
    const t = document.getElementById('modal_phish_target').value;
    let tn = document.getElementById('modal_phish_name').value.trim();
    if (!tn) {
        const toEmail = document.getElementById('to_email')?.value.trim();
        if (toEmail) tn = toEmail.split(',')[0].trim().split('@')[0];
    }
    const lu = document.getElementById('modal_phish_url').value.trim();

    showLoading('Forging template...');
    try {
        const r = await fetch('/forge_phish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: t, target_name: tn, lure_url: lu })
        });
        const data = await r.json();
        hideLoading();
        if (data.success) {
            const msg = document.getElementById('message');
            if (msg) {
                msg.value = data.template;
                toast(`Forged ${t} template`, 'ok');
                closeForge();
            }
        } else {
            toast(data.error, 'fail');
        }
    } catch (err) {
        hideLoading();
        toast('Error: ' + err.message, 'fail');
    }
}

function openForge() {
    const el = document.getElementById('forgeOverlay');
    if (el) el.classList.add('show');
}

function closeForge() {
    const el = document.getElementById('forgeOverlay');
    if (el) el.classList.remove('show');
}

// ── Scroll Reveal ─────────────────────────────────────────
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => {
        observer.observe(el);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    initNavbarScroll();
});

function initNavbarScroll() {
    const navbar = document.querySelector('.navbar-wrap');
    if (!navbar) return;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        // Only show navbar when at the very top (e.g., < 50px)
        if (currentScrollY > 50) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
    }, { passive: true });
}

// ── Config ────────────────────────────────────────────────
window.bgSettings = { speed: 0.4 }; // Global for background access

function openConfig() {
    // Sync UI with current settings
    const color = getComputedStyle(document.documentElement).getPropertyValue('--accent-glow-primary').trim() || '#ffffff';
    const accentInput = document.getElementById('cfgAccent');
    if (accentInput) {
        accentInput.value = color;
        const hexDisp = document.getElementById('accentHex');
        if (hexDisp) hexDisp.textContent = color.toUpperCase();
    }
    const speedInput = document.getElementById('cfgSpeed');
    if (speedInput) {
        speedInput.value = window.bgSettings.speed;
        const speedDisp = document.getElementById('speedVal');
        if (speedDisp) speedDisp.textContent = window.bgSettings.speed + 'x';
    }
    document.getElementById('configOverlay')?.classList.add('show');
}

function closeConfig() { document.getElementById('configOverlay')?.classList.remove('show'); }

function saveConfig() {
    const color = document.getElementById('cfgAccent').value;
    const speed = parseFloat(document.getElementById('cfgSpeed').value);

    // Apply changes
    document.documentElement.style.setProperty('--accent-glow-primary', color);
    window.bgSettings.speed = speed;

    // Update Hex and Slider UI
    const hexDisp = document.getElementById('accentHex');
    if (hexDisp) hexDisp.textContent = color.toUpperCase();
    const speedDisp = document.getElementById('speedVal');
    if (speedDisp) speedDisp.textContent = speed + 'x';

    // Persist
    localStorage.setItem('ms_config', JSON.stringify({ color, speed }));

    closeConfig();
    toast('Settings applied', 'ok');
}

function resetConfig() {
    localStorage.removeItem('ms_config');
    // Restore defaults
    document.documentElement.style.removeProperty('--accent-glow-primary');
    window.bgSettings.speed = 0.4;

    // Update inputs if they exist
    const accent = document.getElementById('cfgAccent');
    if (accent) {
        accent.value = '#ffffff';
        document.getElementById('accentHex').textContent = '#FFFFFF';
    }
    const speed = document.getElementById('cfgSpeed');
    if (speed) {
        speed.value = 0.4;
        document.getElementById('speedVal').textContent = '0.4x';
    }

    toast('Defaults restored', 'ok');
}

function loadConfig() {
    const saved = localStorage.getItem('ms_config');
    if (saved) {
        const config = JSON.parse(saved);
        if (config.color) {
            document.documentElement.style.setProperty('--accent-glow-primary', config.color);
            // Also apply to --pure if needed by Neural Bg
            document.documentElement.style.setProperty('--pure', config.color);
        }
        if (config.speed) window.bgSettings.speed = config.speed;
    }
}

// ── Credential Persistence (obfuscated in localStorage) ──
const SMTP_FIELDS = ['smtp_server', 'smtp_port', 'username', 'password'];
const API_FIELDS  = ['consumer_key', 'consumer_secret'];

function _encode(v) { try { return btoa(unescape(encodeURIComponent(v))); } catch { return ''; } }
function _decode(v) { try { return decodeURIComponent(escape(atob(v))); } catch { return ''; } }

function saveAllCredentials() {
    const creds = { mode: (document.getElementById('send_mode')?.value || 'smtp') };
    [...SMTP_FIELDS, ...API_FIELDS].forEach(f => {
        const el = document.getElementById(f);
        if (el) creds[f] = _encode(el.value);
    });
    localStorage.setItem('ms_creds', JSON.stringify(creds));
}

function loadAllCredentials() {
    const raw = localStorage.getItem('ms_creds');
    if (!raw) return;
    try {
        const creds = JSON.parse(raw);
        [...SMTP_FIELDS, ...API_FIELDS].forEach(f => {
            const el = document.getElementById(f);
            if (el && creds[f]) el.value = _decode(creds[f]);
        });
        // Restore mode toggle
        if (creds.mode === 'api') {
            const tog = document.getElementById('send_mode_toggle');
            if (tog) { tog.checked = true; toggleSendMode(); }
        }
    } catch {}
}

function toggleSendMode() {
    const checked = document.getElementById('send_mode_toggle')?.checked;
    const smtpDiv = document.getElementById('smtp_mode_fields');
    const apiDiv  = document.getElementById('api_mode_fields');
    const modeEl  = document.getElementById('send_mode');
    if (checked) {
        if (smtpDiv) smtpDiv.style.display = 'none';
        if (apiDiv)  apiDiv.style.display  = '';
        if (modeEl)  modeEl.value = 'api';
    } else {
        if (smtpDiv) smtpDiv.style.display = '';
        if (apiDiv)  apiDiv.style.display  = 'none';
        if (modeEl)  modeEl.value = 'smtp';
    }
    saveAllCredentials();
}

// ── Loading ───────────────────────────────────────────────
function showLoading(txt) {
    const el = document.getElementById('loadingOverlay');
    const tx = document.getElementById('loadingText');
    if (tx) tx.textContent = txt || 'Processing...';
    if (el) el.classList.add('show');
}
function hideLoading() { document.getElementById('loadingOverlay')?.classList.remove('show'); }

// ── Toast ─────────────────────────────────────────────────
function toast(msg, type) {
    const stack = document.getElementById('toastStack'); if (!stack) return;
    const icon = type === 'ok' ? 'fa-check-circle' : type === 'fail' ? 'fa-times-circle' : 'fa-info-circle';
    const el = document.createElement('div');
    el.className = 'toast';
    el.innerHTML = `<i class="fas ${icon}"></i> <span>${msg}</span>`;
    stack.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}
function showAlert(m, t) { toast(m, t === 'success' ? 'ok' : t === 'danger' ? 'fail' : 'info'); }

// ── Stats ─────────────────────────────────────────────────
function inc(key) {
    const v = parseInt(localStorage.getItem('sk_' + key) || '0') + 1;
    localStorage.setItem('sk_' + key, v);
    const el = document.getElementById('stat' + key.charAt(0).toUpperCase() + key.slice(1));
    if (el) el.textContent = v;
}
function loadStats() {
    ['Emails', 'Servers', 'Domains', 'Headers'].forEach(k => {
        const el = document.getElementById('stat' + k);
        if (el) el.textContent = localStorage.getItem('sk_' + k.toLowerCase()) || '0';
    });
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadStats();

    const forms = {
        emailForm: sendEmail, testForm: testConnection, serversForm: testServers,
        spoofForm: checkDomain, dkimForm: checkDKIM, headersForm: analyzeHeaders,
        dnsblForm: auditDNSBL, subdomainForm: enumSubdomains,
        breachForm: searchBreach, phishForm: generatePhish, macroForm: generateMacro,
        pixelForm: generatePixel, homoglyphForm: generateHomoglyph, obfuscateForm: obfuscateHtml
    };
    Object.entries(forms).forEach(([id, fn]) => {
        const f = document.getElementById(id);
        if (f) f.addEventListener('submit', e => { e.preventDefault(); fn(); });
    });

    // Auto-fill sender identity fields
    const fe = document.getElementById('from_email');
    const rt = document.getElementById('reply_to');
    const es = document.getElementById('envelope_sender');

    if (fe) {
        fe.addEventListener('input', () => {
            // Only sync if the fields are empty or currently match the old value (simplified: only if not manually touched)
            // For simplicity and user request "always put the same", we'll sync if they haven't been manually changed to something else
            if (es && (!es.value || es.dataset.synced === 'true')) {
                es.value = fe.value;
                es.dataset.synced = 'true';
            }
        });
    }

    // Mark as manually changed to stop auto-sync
    if (es) {
        es.addEventListener('input', () => {
            es.dataset.synced = 'false';
        });
        es.addEventListener('blur', () => {
            if (es.value === fe.value) es.dataset.synced = 'true';
        });
    }

    // Password toggles
    document.querySelectorAll('input[type="password"]').forEach(p => {
        const w = document.createElement('div');
        w.style.cssText = 'position:relative;';
        p.parentNode.insertBefore(w, p); w.appendChild(p);
        const i = document.createElement('i');
        i.className = 'fas fa-eye';
        i.style.cssText = 'position:absolute;right:12px;top:50%;transform:translateY(-50%);cursor:pointer;color:var(--muted);font-size:12px;';
        i.onclick = () => { p.type = p.type === 'password' ? 'text' : 'password'; i.className = p.type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash'; };
        w.appendChild(i);
    });

    // Neural Background Init
    initNeuralBackground('bg-container', '#a3a3a3', 400, 0.4, 0.15);

    // Initial Config & Creds Load
    loadConfig();
    loadAllCredentials();

    // Attach listeners for credential saving (both SMTP and API fields)
    [...SMTP_FIELDS, ...API_FIELDS].forEach(f => {
        const el = document.getElementById(f);
        if (el) el.addEventListener('input', saveAllCredentials);
    });

    // Config Listeners
    const accentInput = document.getElementById('cfgAccent');
    if (accentInput) {
        accentInput.addEventListener('input', (e) => {
            const hexDisp = document.getElementById('accentHex');
            if (hexDisp) hexDisp.textContent = e.target.value.toUpperCase();
        });
    }

    const speedInput = document.getElementById('cfgSpeed');
    if (speedInput) {
        speedInput.addEventListener('input', (e) => {
            const speedDisp = document.getElementById('speedVal');
            if (speedDisp) speedDisp.textContent = e.target.value + 'x';
        });
    }

    // FAQ Accordion Logic
    document.querySelectorAll('.accordion-trigger').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const item = trigger.closest('.accordion-item');
            const content = item.querySelector('.accordion-content');
            const isOpen = item.classList.contains('open');

            // Close all other accordions (optional: remove for multi-open)
            document.querySelectorAll('.accordion-item').forEach(otherItem => {
                otherItem.classList.remove('open');
                otherItem.querySelector('.accordion-content').style.maxHeight = null;
            });

            // Toggle current one
            if (!isOpen) {
                item.classList.add('open');
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });

    // Mobile Nav Toggle (Shadcn Style Sheet)
    const navToggle = document.getElementById('nav-toggle');
    const sheetOverlay = document.getElementById('sheet-overlay');
    const sheetContent = document.getElementById('sheet-content');
    const sheetClose = document.getElementById('sheet-close');

    if (navToggle && sheetOverlay && sheetContent) {
        const openMenu = () => {
            sheetOverlay.classList.add('show');
            sheetContent.classList.add('show');
            document.body.style.overflow = 'hidden'; 
        };

        const closeMenu = () => {
            sheetOverlay.classList.remove('show');
            sheetContent.classList.remove('show');
            document.body.style.overflow = '';
        };

        navToggle.addEventListener('click', openMenu);
        if (sheetClose) sheetClose.addEventListener('click', closeMenu);
        sheetOverlay.addEventListener('click', (e) => {
            if (e.target === sheetOverlay) closeMenu();
        });
    }

    // Handle initial hash for section switching (e.g. from features page)
    const hash = window.location.hash;
    if (hash && hash.startsWith('#section-')) {
        const sectionId = hash.replace('#section-', '');
        switchSection(sectionId);

        // Minor delay to ensure smooth scroll if needed, though switchSection does scrollTo(0,0)
        setTimeout(() => {
            const el = document.getElementById('section-' + sectionId);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
});

// ── API Calls ─────────────────────────────────────────────
async function sendEmail() {
    showLoading('Sending email...');
    try {
        const r = await fetch('/send_email', { method: 'POST', body: new FormData(document.getElementById('emailForm')) });
        const d = await r.json(); hideLoading();
        if (d.success) { toast('Email sent successfully', 'ok'); inc('emails'); }
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function applyHomoglyphFromEmail() {
    const fe = document.getElementById('from_email');
    if (!fe || !fe.value.includes('@')) {
        return toast('Enter a valid sender email first', 'fail');
    }

    const parts = fe.value.split('@');
    const user = parts[0];
    const domain = parts[1];

    showLoading('Spoofing domain...');
    try {
        const r = await fetch('/bypass_homoglyph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain: domain })
        });
        const d = await r.json();
        hideLoading();

        if (d.success && d.homoglyphs && d.homoglyphs.length > 0) {
            // Pick a random homoglyph for variety
            const randomGlyph = d.homoglyphs[Math.floor(Math.random() * d.homoglyphs.length)];
            fe.value = `${user}@${randomGlyph}`;
            
            // Also update envelope sender if synced
            const es = document.getElementById('envelope_sender');
            if (es && es.dataset.synced === 'true') {
                es.value = fe.value;
            }

            toast('Domain spoofed with homoglyph!', 'ok');
        } else {
            toast(d.error || 'No homoglyphs found for this domain', 'fail');
        }
    } catch (e) {
        hideLoading();
        toast('Error: ' + e.message, 'fail');
    }
}

async function testConnection() {
    showLoading('Testing connection...');
    try {
        const r = await fetch('/test_connection', { method: 'POST', body: new FormData(document.getElementById('testForm')) });
        const d = await r.json(); hideLoading();
        if (d.success) toast(d.message, 'ok'); else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function testServers() {
    showLoading('Testing servers...');
    const sl = document.getElementById('serversList'), rd = document.getElementById('serversResults');
    if (sl) sl.innerHTML = '<div style="color:var(--muted);font-size:12px;">Scanning...</div>';
    if (rd) rd.style.display = 'block';
    try {
        const r = await fetch('/test_servers', { method: 'POST', body: new FormData(document.getElementById('serversForm')) });
        const d = await r.json(); hideLoading();
        if (d.success) { toast('Cluster audit complete', 'ok'); inc('servers'); renderNodes(d.working_servers); }
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function checkDomain() {
    let rawInput = document.getElementById('domain_check').value.trim();
    if (!rawInput) return toast('Enter domain(s) or paste text containing domains', 'fail');

    // Re-fang domains (e.g. example[.]com -> example.com)
    rawInput = rawInput.replace(/\[\.\]/g, '.');

    // Auto-extract domains using regex, discarding 'http://', 'https://', and trailing paths
    const domainRegex = /(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)/gi;
    const matches = Array.from(rawInput.matchAll(domainRegex));
    const extractedDomains = [...new Set(matches.map(m => m[1].toLowerCase()))];

    if (extractedDomains.length === 0) return toast('No valid domains found in text', 'fail');

    const scanSubdomains = document.getElementById('scan_subdomains')?.checked || false;

    const ad = document.getElementById('spoofAnalysis'), rd = document.getElementById('spoofResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Analyzing ' + extractedDomains.length + ' domain(s)...</div>';
    if (rd) rd.style.display = 'block';

    showLoading('Running recon...');
    try {
        let d;
        if (extractedDomains.length > 1 || scanSubdomains) {
            const r = await fetch('/check_multiple_domains', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domains: extractedDomains.join(','), scan_subdomains: scanSubdomains }) });
            d = await r.json();
        } else {
            const r = await fetch('/check_spoofing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: extractedDomains[0], scan_subdomains: scanSubdomains }) });
            d = await r.json();
        }
        hideLoading();
        if (d.success) { inc('domains'); (extractedDomains.length > 1 || scanSubdomains) ? renderMultiRecon(d) : renderRecon(d.analysis); }
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function checkDKIM() {
    const dom = document.getElementById('dkim_domain').value.trim();
    if (!dom) return toast('Enter domain', 'fail');
    const ad = document.getElementById('dkimAnalysis'), rd = document.getElementById('dkimResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Auditing...</div>';
    if (rd) rd.style.display = 'block';
    const sel = document.getElementById('dkim_selectors').value.trim();
    const req = { domain: dom }; if (sel) req.selectors = sel.split(',').map(s => s.trim());
    showLoading('Checking DKIM...');
    try {
        const r = await fetch('/check_dkim', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) });
        const d = await r.json(); hideLoading();
        if (d.success) { inc('domains'); renderDKIM(d.analysis); }
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function analyzeHeaders() {
    const h = document.getElementById('email_headers').value.trim();
    if (!h) return toast('Paste headers', 'fail');
    const ad = document.getElementById('headersAnalysis'), rd = document.getElementById('headersResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Parsing...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Analyzing headers...');
    try {
        const r = await fetch('/analyze_headers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ headers: h }) });
        const d = await r.json(); hideLoading();
        if (d.success) { inc('headers'); renderHeaders(d.analysis); }
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function auditDNSBL() {
    const t = document.getElementById('bl_target').value.trim();
    if (!t) return toast('Enter IP or domain', 'fail');
    const ad = document.getElementById('dnsblAnalysis'), rd = document.getElementById('dnsblResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Checking DNSBLs...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Checking blacklist...');
    try {
        const r = await fetch('/audit_dnsbl', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target: t }) });
        const d = await r.json(); hideLoading();
        if (d.success) renderDNSBL(d.results, t);
        else toast(d.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function enumSubdomains() {
    const d = document.getElementById('sub_domain').value.trim();
    if (!d) return toast('Enter domain', 'fail');
    const ad = document.getElementById('subdomainAnalysis'), rd = document.getElementById('subdomainResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Enumerating...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Scanning subdomains...');
    try {
        const r = await fetch('/intel_subdomain', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: d }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderSubdomains(data, d);
        else toast(data.error, 'fail');
    } catch (e) { hideLoading(); toast('Error: ' + e.message, 'fail'); }
}

async function searchBreach() {
    const e = document.getElementById('breach_email').value.trim();
    if (!e) return toast('Enter email', 'fail');
    const ad = document.getElementById('breachAnalysis'), rd = document.getElementById('breachResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Searching dumps...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Searching breaches...');
    try {
        const r = await fetch('/intel_breach', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: e }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderBreach(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

async function generatePhish() {
    const t = document.getElementById('phish_target').value;
    let tn = document.getElementById('phish_target_name')?.value || '';
    if (!tn) {
        const toEmail = document.getElementById('to_email')?.value.trim();
        if (toEmail) tn = toEmail.split(',')[0].trim().split('@')[0];
    }
    const lu = document.getElementById('phish_lure_url')?.value || '';
    const ad = document.getElementById('phishAnalysis'), rd = document.getElementById('phishResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Generating...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Generating template...');
    try {
        const r = await fetch('/forge_phish', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target: t, target_name: tn, lure_url: lu }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderPhish(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

async function generateMacro() {
    const ad = document.getElementById('macroAnalysis'), rd = document.getElementById('macroResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Building VBA...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Building macro...');
    try {
        const r = await fetch('/forge_macro', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: "calc.exe" }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderMacro(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

async function generatePixel() {
    const ad = document.getElementById('pixelAnalysis'), rd = document.getElementById('pixelResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Generating...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Generating pixel...');
    try {
        const r = await fetch('/forge_pixel', { method: 'POST' });
        const data = await r.json(); hideLoading();
        if (data.success) renderPixel(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

async function generateHomoglyph() {
    const d = document.getElementById('homo_domain').value.trim();
    if (!d) return toast('Enter domain', 'fail');
    const ad = document.getElementById('homoglyphAnalysis'), rd = document.getElementById('homoglyphResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Generating...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Generating homoglyphs...');
    try {
        const r = await fetch('/bypass_homoglyph', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: d }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderHomoglyph(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

async function obfuscateHtml() {
    const h = document.getElementById('obf_html').value.trim();
    const m = document.getElementById('obf_mode').value;
    if (!h) return toast('Enter HTML', 'fail');
    const ad = document.getElementById('obfuscateAnalysis'), rd = document.getElementById('obfuscateResults');
    if (ad) ad.innerHTML = '<div style="color:var(--muted);font-size:12px;">Obfuscating...</div>';
    if (rd) rd.style.display = 'block';
    showLoading('Obfuscating HTML...');
    try {
        const r = await fetch('/bypass_html', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ html: h, mode: m }) });
        const data = await r.json(); hideLoading();
        if (data.success) renderObfuscated(data);
        else toast(data.error, 'fail');
    } catch (err) { hideLoading(); toast('Error: ' + err.message, 'fail'); }
}

// ── Renderers ─────────────────────────────────────────────
function renderNodes(nodes) {
    const sl = document.getElementById('serversList');
    if (!nodes || !nodes.length) { sl.innerHTML = '<span class="badge badge-fail">No live nodes</span>'; return; }
    sl.innerHTML = '<table class="data-table"><thead><tr><th>Node</th><th>Status</th></tr></thead><tbody>' +
        nodes.map(n => `<tr><td>${n.server}:${n.port}</td><td><span class="badge badge-ok">LIVE</span></td></tr>`).join('') +
        '</tbody></table>';
}

function renderRecon(a) {
    const ad = document.getElementById('spoofAnalysis');
    const st = a.overall_status === 'secure' ? 'badge-ok' : a.overall_status === 'partially_secure' ? 'badge-warn' : 'badge-fail';
    const stText = a.overall_status.toUpperCase().replace('_', ' ');

    // Build Issues Table rows if vulnerable
    let issuesHtml = '';
    let issueCount = 1;
    if (a.spf.status !== 'present') {
        issuesHtml += `<tr><td>${issueCount++}</td><td>Missing SPF Record</td><td>The domain lacks an SPF record, allowing unauthorized servers to spoof it.</td><td>High</td></tr>`;
    }
    if (a.dmarc.status !== 'present') {
        issuesHtml += `<tr><td>${issueCount++}</td><td>Missing DMARC Record</td><td>The domain lacks a DMARC policy, meaning spoofed emails won't be rejected.</td><td>High</td></tr>`;
    } else if (a.dmarc.policy === 'none') {
        issuesHtml += `<tr><td>${issueCount++}</td><td>Insecure DMARC policy 'p' qualifier</td><td>The DMARC policy 'p' qualifier is set to "none". If the DMARC policy is neither "reject" nor "quarantine", spoofed emails are likely to be accepted.</td><td>High</td></tr>`;
    }
    if (a.dmarc.subdomain_vulnerable) {
        issuesHtml += `<tr><td>${issueCount++}</td><td>Insecure DMARC sub-domain 'sp' qualifier</td><td>The DMARC policy 'sp' qualifier for sub-domains is set to "none" or undefined. If the DMARC policy is neither "reject" nor "quarantine", spoofed emails from sub-domains are likely to be accepted.</td><td>High</td></tr>`;
    }

    const issuesTable = issuesHtml ? `
        <div style="margin-top: 16px; overflow-x: auto; padding-bottom: 8px;">
            <table class="data-table" style="min-width: 600px;">
                <thead><tr><th style="width:60px;">Issue #</th><th style="width:200px;">Issue Title</th><th>Issue Detail</th><th style="width:80px;">Severity</th></tr></thead>
                <tbody>${issuesHtml}</tbody>
            </table>
        </div>
    ` : '<div class="alert-bar ok mt-16" style="font-size:12px;">No spoofing vulnerabilities detected. Domain is secure.</div>';

    ad.innerHTML = `<div class="module">
        <div class="module-head" style="display:flex;justify-content:space-between;align-items:center;">
            <span>${a.domain}</span><span class="badge ${st}">${stText}</span>
        </div>
        <div class="module-body">
            <div style="font-size: 12px; color: var(--soft); margin-bottom: 8px; word-break: break-all;">
                <span style="color: var(--muted); font-weight: bold;">SPF Record:</span> ${a.spf.record || 'Not found'}
            </div>
            <div style="font-size: 12px; color: var(--soft); margin-bottom: 16px; word-break: break-all;">
                <span style="color: var(--muted); font-weight: bold;">DMARC Record:</span> ${a.dmarc.record || 'Not found'}
            </div>
            ${issuesTable}
            ${a.recommendations.length ? '<div style="margin-top:16px;font-size:12px;color:var(--soft);"><strong>Recommendations:</strong><ul style="margin:8px 0 0 16px;">' + a.recommendations.map(r => '<li style="margin-bottom:4px;">' + r + '</li>').join('') + '</ul></div>' : ''}
        </div>
    </div>`;
}

function renderMultiRecon(res) {
    const ad = document.getElementById('spoofAnalysis');

    // Build accordion items instead of a table
    const accordionHtml = res.results.map((d, index) => {
        const bdg = d.overall_status === 'secure' ? 'badge-ok' : d.overall_status === 'partially_secure' ? 'badge-warn' : 'badge-fail';
        const stText = d.overall_status.toUpperCase().replace('_', ' ');
        const spfBdg = d.spf.status === 'present' ? 'badge-ok' : 'badge-fail';
        const dmarcBdg = d.dmarc.vulnerable ? 'badge-fail' : 'badge-ok';

        // Build Issues Table rows if vulnerable
        let issuesHtml = '';
        let issueCount = 1;
        if (d.spf.status !== 'present') {
            issuesHtml += `<tr><td>${issueCount++}</td><td>Missing SPF Record</td><td>The domain lacks an SPF record, allowing unauthorized servers to spoof it.</td><td>High</td></tr>`;
        }
        if (d.dmarc.status !== 'present') {
            issuesHtml += `<tr><td>${issueCount++}</td><td>Missing DMARC Record</td><td>The domain lacks a DMARC policy, meaning spoofed emails won't be rejected.</td><td>High</td></tr>`;
        } else if (d.dmarc.policy === 'none') {
            issuesHtml += `<tr><td>${issueCount++}</td><td>Insecure DMARC policy 'p' qualifier</td><td>The DMARC policy 'p' qualifier is set to "none". If the DMARC policy is neither "reject" nor "quarantine", spoofed emails are likely to be accepted.</td><td>High</td></tr>`;
        }
        if (d.dmarc.subdomain_vulnerable) {
            issuesHtml += `<tr><td>${issueCount++}</td><td>Insecure DMARC sub-domain 'sp' qualifier</td><td>The DMARC policy 'sp' qualifier for sub-domains is set to "none" or undefined. If the DMARC policy is neither "reject" nor "quarantine", spoofed emails from sub-domains are likely to be accepted.</td><td>High</td></tr>`;
        }

        const issuesTable = issuesHtml ? `
            <div style="margin-top: 16px; overflow-x: auto; padding-bottom: 8px;">
                <table class="data-table" style="min-width: 600px;">
                    <thead><tr><th style="width:60px;">Issue #</th><th style="width:200px;">Issue Title</th><th>Issue Detail</th><th style="width:80px;">Severity</th></tr></thead>
                    <tbody>${issuesHtml}</tbody>
                </table>
            </div>
        ` : '<div class="alert-bar ok mt-16" style="font-size:12px;">No spoofing vulnerabilities detected. Domain is secure.</div>';

        return `
        <div class="accordion-item" style="border: 1px solid var(--border); margin-bottom: 8px; border-radius: 4px;">
            <div class="accordion-trigger" style="padding: 12px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; background: rgba(0,0,0,0.2);">
                <div style="font-weight: bold; font-family: monospace;">${d.domain}</div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="badge ${bdg}">${stText}</span>
                    <i class="fas fa-chevron-down" style="color: var(--muted); font-size: 10px; transition: transform 0.3s ease;"></i>
                </div>
            </div>
            <div class="accordion-content" style="max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; background: var(--bg);">
                <div style="padding: 16px;">
                    <div style="font-size: 12px; color: var(--soft); margin-bottom: 8px; word-break: break-all;">
                        <span style="color: var(--muted); font-weight: bold;">SPF Record:</span> ${d.spf.record || 'Not found'}
                    </div>
                    <div style="font-size: 12px; color: var(--soft); margin-bottom: 16px; word-break: break-all;">
                        <span style="color: var(--muted); font-weight: bold;">DMARC Record:</span> ${d.dmarc.record || 'Not found'}
                    </div>
                    ${issuesTable}
                    ${d.recommendations.length ? '<div style="margin-top:16px;font-size:12px;color:var(--soft);"><strong>Recommendations:</strong><ul style="margin:8px 0 0 16px;">' + d.recommendations.map(r => '<li style="margin-bottom:4px;">' + r + '</li>').join('') + '</ul></div>' : ''}
                </div>
            </div>
        </div>`;
    }).join('');

    ad.innerHTML = `<div class="module"><div class="module-head">Bulk Recon — ${res.summary.total_checked} domains</div>
        <div class="module-body">
            <div class="field-row-3 mb-16" style="text-align:center;">
                <div><div class="badge badge-ok">${res.summary.secure_count}</div><div style="font-size:11px;color:var(--muted);margin-top:4px;">Secure</div></div>
                <div><div class="badge badge-warn">${res.summary.partially_secure_count}</div><div style="font-size:11px;color:var(--muted);margin-top:4px;">Partial</div></div>
                <div><div class="badge badge-fail">${res.summary.vulnerable_count}</div><div style="font-size:11px;color:var(--muted);margin-top:4px;">Vulnerable</div></div>
            </div>
            <div class="bulk-recon-list" style="margin-top: 16px;">
                ${accordionHtml}
            </div>
        </div></div>`;

    // Re-bind accordion logic just for these new items
    ad.querySelectorAll('.accordion-trigger').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const item = trigger.closest('.accordion-item');
            const content = item.querySelector('.accordion-content');
            const icon = item.querySelector('.fa-chevron-down');
            const isOpen = item.classList.contains('open');

            // Close all others in this specific module
            ad.querySelectorAll('.accordion-item').forEach(otherItem => {
                otherItem.classList.remove('open');
                otherItem.querySelector('.accordion-content').style.maxHeight = null;
                const otherIcon = otherItem.querySelector('.fa-chevron-down');
                if (otherIcon) otherIcon.style.transform = 'rotate(0deg)';
            });

            if (!isOpen) {
                item.classList.add('open');
                content.style.maxHeight = content.scrollHeight + "px";
                if (icon) icon.style.transform = 'rotate(180deg)';
            }
        });
    });
}

function renderDKIM(a) {
    const ad = document.getElementById('dkimAnalysis');
    const rd = document.getElementById('dkimResults');
    if (rd) rd.style.display = 'block';
    
    let html = `<div class="module">
        <div class="module-head" style="display:flex; justify-content:space-between; align-items:center;">
            <span>DKIM Audit: ${a.domain}</span>
            <span class="badge ${a.valid_keys > 0 ? 'badge-ok' : 'badge-fail'}">
                ${a.valid_keys}/${a.selectors_found.length} Valid
            </span>
        </div>
        <div class="module-body">
            <div style="font-size:12px; color:var(--soft); margin-bottom:12px;">${a.summary}</div>
            
            ${a.selectors_found.length ? `
                <table class="data-table">
                    <thead>
                        <tr><th>Selector</th><th>Record / Key Info</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        ${a.selectors_found.map(s => `
                            <tr>
                                <td style="font-weight:700;">${s.selector}</td>
                                <td>
                                    <div style="font-size:10px; color:var(--muted); max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${s.record}">
                                        ${s.record}
                                    </div>
                                    <div style="font-size:10px; margin-top:4px;">
                                        Type: ${s.key_type || 'RSA'} | Alg: ${s.algorithm || 'sha256'}
                                    </div>
                                </td>
                                <td>
                                    <span class="badge ${s.valid ? 'badge-ok' : 'badge-fail'}">
                                        ${s.valid ? 'PASS' : 'FAIL'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : `
                <div class="alert-bar warn">
                    <i class="fas fa-exclamation-triangle"></i> No DKIM selectors found for this domain. 
                    Try entering a common selector like 'google' or 'default' manually.
                </div>
            `}
            
            ${a.recommendations.length ? `
                <div style="margin-top:16px; padding-top:12px; border-top:1px solid var(--border);">
                    <div style="font-size:11px; font-weight:700; color:var(--muted); margin-bottom:8px; text-transform:uppercase; letter-spacing:0.05em;">Recommendations</div>
                    ${a.recommendations.map(r => `<div style="font-size:12px; color:var(--soft); margin-bottom:4px;">• ${r}</div>`).join('')}
                </div>
            ` : ''}
        </div>
    </div>`;
    ad.innerHTML = html;
}

function renderHeaders(a) {
    const ad = document.getElementById('headersAnalysis');
    const sc = a.security_score >= 80 ? 'badge-ok' : a.security_score >= 60 ? 'badge-warn' : 'badge-fail';
    ad.innerHTML = `<div class="module"><div class="module-head" style="display:flex;justify-content:space-between;align-items:center;">
        <span>Header Analysis</span><span class="badge ${sc}">Score: ${a.security_score}</span></div>
        <div class="module-body">
            <div class="field-row-3 mb-16" style="text-align:center;">
                <div><span class="badge ${a.spf_result === 'pass' ? 'badge-ok' : 'badge-fail'}">${a.spf_result || 'N/A'}</span><div style="font-size:10px;color:var(--muted);margin-top:4px;">SPF</div></div>
                <div><span class="badge ${a.dkim_result === 'pass' ? 'badge-ok' : 'badge-fail'}">${a.dkim_result || 'N/A'}</span><div style="font-size:10px;color:var(--muted);margin-top:4px;">DKIM</div></div>
                <div><span class="badge ${a.dmarc_result === 'pass' ? 'badge-ok' : 'badge-fail'}">${a.dmarc_result || 'N/A'}</span><div style="font-size:10px;color:var(--muted);margin-top:4px;">DMARC</div></div>
            </div>
            <div style="font-size:12px;color:var(--soft);margin-bottom:12px;">${a.summary}</div>
            ${a.suspicious_indicators.length ? '<div class="alert-bar warn" style="font-size:12px;"><i class="fas fa-exclamation-triangle"></i> ' + a.suspicious_indicators.join(', ') + '</div>' : ''}
            ${a.received_chain.length ? '<details style="margin-top:12px;"><summary style="font-size:11px;color:var(--muted);cursor:pointer;">Routing chain (' + a.received_chain.length + ' hops)</summary><div style="font-size:10px;color:var(--muted);padding:8px;background:var(--bg);border-radius:4px;margin-top:8px;max-height:200px;overflow:auto;">' + a.received_chain.map(c => '<div style="margin-bottom:4px;">&gt; ' + c + '</div>').join('') + '</div></details>' : ''}
        </div></div>`;
}
// ── Renderers ─────────────────────────────────────────────

function renderDNSBL(res, target) {
    const ad = document.getElementById('dnsblAnalysis');
    const listed = res.filter(r => r.listed);
    const badge = listed.length > 0 ? 'badge-fail' : 'badge-ok';
    const statusTxt = listed.length > 0 ? `Listed on ${listed.length}` : 'Clean';
    ad.innerHTML = `<div class="module"><div class="module-head" style="display:flex;justify-content:space-between;">
        <span>${target}</span><span class="badge ${badge}">${statusTxt}</span></div>
        <div class="module-body">
            <table class="data-table"><thead><tr><th>DNSBL</th><th>Status</th></tr></thead><tbody>
                ${res.map(r => `<tr><td>${r.provider}</td><td><span class="badge ${r.listed ? 'badge-fail' : 'badge-ok'}">${r.listed ? 'LISTED' : 'OK'}</span></td></tr>`).join('')}
            </tbody></table>
        </div></div>`;
}

function renderSubdomains(data, target) {
    const ad = document.getElementById('subdomainAnalysis');
    const found = data.active_subdomains || [];

    const html = found.map(s => {
        const isProtected = s.security && s.security.protected;
        const records = s.records || {};

        let recordHtml = '';
        if (records.A && records.A.length) {
            recordHtml += `<div class="record-pill"><b>A:</b> ${records.A.join(', ')}</div>`;
        }
        if (records.CNAME && records.CNAME.length) {
            recordHtml += `<div class="record-pill"><b>CNAME:</b> ${records.CNAME.join(', ')}</div>`;
        }
        if (records.SPF) {
            recordHtml += `<div class="record-pill"><b>SPF:</b> ${records.SPF}</div>`;
        }
        if (records.DMARC) {
            recordHtml += `<div class="record-pill"><b>DMARC:</b> ${records.DMARC}</div>`;
        }

        return `
            <div class="subdomain-item">
                <div class="subdomain-header">
                    <div class="subdomain-name">
                        <i class="fas fa-server" style="margin-right:8px; color:var(--soft);"></i>
                        ${s.subdomain}
                        ${isProtected ? '<span class="security-tag protected" style="margin-left:8px;">Protected</span>' : ''}
                    </div>
                    <span class="badge badge-ok" style="font-size:9px; opacity:0.8;">DISCOVERED</span>
                </div>
                <div class="record-pills">
                    ${recordHtml || '<span style="font-size:10px;color:var(--muted); font-style:italic;">No active DNS records detected</span>'}
                </div>
            </div>
        `;
    }).join('');

    ad.innerHTML = `<div class="module">
        <div class="module-head" style="display:flex;justify-content:space-between;align-items:center;">
            <span>Infrastructure Scan: ${target}</span>
            <span class="badge badge-ok">${found.length} Nodes</span>
        </div>
        <div class="module-body" style="background: rgba(0,0,0,0.1); border-radius: 0 0 6px 6px;">
            <div style="font-size:11px; color:var(--muted); margin-bottom:12px; font-style:italic;">
                <i class="fas fa-info-circle"></i> Aggregating crt.sh certificate logs with live DNS probes (A, CNAME, SPF, DMARC).
            </div>
            <div class="subdomain-list">
                ${html || '<div class="alert-bar warn">No subdomains found for this target.</div>'}
            </div>
        </div>
    </div>`;
}

function renderBreach(data) {
    const ad = document.getElementById('breachAnalysis');
    const b = data.breaches;
    const badge = b.length > 0 ? 'badge-fail' : 'badge-ok';
    ad.innerHTML = `<div class="module"><div class="module-head" style="display:flex;justify-content:space-between;">
        <span>${data.email}</span><span class="badge ${badge}">${data.breached ? b.length + ' Breaches' : 'Clean'}</span></div>
        <div class="module-body">
             ${b.length ? `<table class="data-table"><thead><tr><th>Source</th><th>Compromised Data</th></tr></thead><tbody>
                ${b.map(x => `<tr><td>${x.name}</td><td>${x.compromised_data.join(', ')}</td></tr>`).join('')}
            </tbody></table><div class="hint mt-8">Note: This is simulated data for demonstration.</div>` : '<div class="alert-bar ok">No breaches found for this email.</div>'}
        </div></div>`;
}

function renderPhish(data) {
    const ad = document.getElementById('phishAnalysis');
    ad.innerHTML = `<div class="module" style="margin-bottom: 16px;"><div class="module-head">Phishing Template Code</div>
        <div class="module-body">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px;">
                <span class="badge badge-ok">HTML Generated</span>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-white" style="padding:4px 12px;font-size:12px;" onclick="pushToEmail(document.getElementById('phish_code').textContent)"><i class="fas fa-paper-plane"></i> Push to Send</button>
                    <button class="btn btn-ghost" style="padding:4px 8px;font-size:12px;" onclick="navigator.clipboard.writeText(document.getElementById('phish_code').textContent);toast('Copied!','ok')"><i class="fas fa-copy"></i> Copy</button>
                </div>
            </div>
            <pre style="background:var(--bg);padding:12px;border-radius:4px;overflow-y:auto;font-size:11px;color:var(--soft); max-height: 400px; white-space: pre-wrap; word-break: break-all;"><code id="phish_code">${data.template.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div></div>
        <div class="module"><div class="module-head"><i class="fas fa-eye"></i> Visual Preview</div>
        <div class="module-body" style="padding:0; overflow:hidden; border-radius: 0 0 var(--radius) var(--radius);">
            <iframe id="phish_preview" style="width:100%; height:500px; border:none; background:white;"></iframe>
        </div></div>`;

    setTimeout(() => {
        const iframe = document.getElementById('phish_preview');
        if (iframe) iframe.srcdoc = data.template;
    }, 50);
}

function renderMacro(data) {
    const ad = document.getElementById('macroAnalysis');
    ad.innerHTML = `<div class="module"><div class="module-head">VBA Payload</div>
        <div class="module-body">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span class="badge badge-warn">Executes: calc.exe</span>
                <button class="btn btn-ghost" style="padding:4px 8px;font-size:12px;" onclick="navigator.clipboard.writeText(document.getElementById('macro_code').textContent);toast('Copied!','ok')"><i class="fas fa-copy"></i> Copy</button>
            </div>
            <pre style="background:var(--bg);padding:12px;border-radius:4px;overflow-x:auto;font-size:11px;color:var(--soft);max-height:250px;"><code id="macro_code">${data.macro}</code></pre>
            <div class="hint mt-8">Instructions: Open Word/Excel > Alt+F11 > Insert Module > Paste code. Save as macro-enabled document (.docm/.xlsm).</div>
        </div></div>`;
}

function renderPixel(data) {
    const ad = document.getElementById('pixelAnalysis');
    ad.innerHTML = `<div class="module"><div class="module-head">Tracking Pixel Generated</div>
        <div class="module-body">
            <div class="field"><label>HTML Image Tag</label>
                <div style="display:flex;gap:8px;">
                    <input type="text" value='${data.pixel_tag.replace(/'/g, "&apos;")}' readonly id="px_tag" style="background:var(--bg);">
                    <button class="btn btn-ghost" onclick="navigator.clipboard.writeText(document.getElementById('px_tag').value);toast('Copied!','ok')"><i class="fas fa-copy"></i></button>
                </div>
            </div>
            <div class="field mt-8"><label>Tracking Server Script (PHP)</label>
                <div style="display:flex;gap:8px;position:relative;">
                    <textarea readonly id="px_php" style="background:var(--bg);min-height:100px;font-family:monospace;font-size:11px;color:var(--soft);">${data.listener_code}</textarea>
                    <button class="btn btn-ghost" style="position:absolute;top:8px;right:8px;padding:4px 8px;" onclick="navigator.clipboard.writeText(document.getElementById('px_php').value);toast('Copied!','ok')"><i class="fas fa-copy"></i></button>
                </div>
            </div>
        </div></div>`;
}

function renderHomoglyph(data) {
    const ad = document.getElementById('homoglyphAnalysis');
    ad.innerHTML = `<div class="module"><div class="module-head" style="display:flex;justify-content:space-between;">
        <span>${data.original}</span><span class="badge badge-ok">${data.homoglyphs.length} Variants</span></div>
        <div class="module-body">
            <table class="data-table"><thead><tr><th>Spoofed Domain Variant</th></tr></thead><tbody>
                ${data.homoglyphs.map(v => `<tr><td style="font-size:14px;font-family:monospace;">${v}</td></tr>`).join('')}
            </tbody></table>
        </div></div>`;
}

function renderObfuscated(data) {
    const ad = document.getElementById('obfuscateAnalysis');
    ad.innerHTML = `<div class="module"><div class="module-head">Obfuscated HTML (${data.mode})</div>
        <div class="module-body">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span class="badge badge-ok">Ready</span>
                <button class="btn btn-ghost" style="padding:4px 8px;font-size:12px;" onclick="navigator.clipboard.writeText(document.getElementById('obf_code').textContent);toast('Copied!','ok')"><i class="fas fa-copy"></i> Copy</button>
            </div>
            <pre style="background:var(--bg);padding:12px;border-radius:4px;overflow-y:auto;font-size:11px;color:var(--soft); max-height: 250px; white-space: pre-wrap; word-break: break-all;"><code id="obf_code">${data.obfuscated.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div></div>`;
}

// ── Neural Flow Background ────────────────────────────────
function initNeuralBackground(containerId, color, particleCount, speed, trailOpacity) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    container.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = container.clientWidth;
    let height = container.clientHeight;
    let particles = [];
    let animationFrameId;
    let mouse = { x: -1000, y: -1000 };

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = 0;
            this.vy = 0;
            this.age = 0;
            this.life = Math.random() * 200 + 100;
        }
        update() {
            const angle = (Math.cos(this.x * 0.005) + Math.sin(this.y * 0.005)) * Math.PI;
            this.vx += Math.cos(angle) * 0.2 * window.bgSettings.speed;
            this.vy += Math.sin(angle) * 0.2 * window.bgSettings.speed;

            const dx = mouse.x - this.x;
            const dy = mouse.y - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const interactionRadius = 150;

            if (distance < interactionRadius) {
                const force = (interactionRadius - distance) / interactionRadius;
                this.vx -= dx * force * 0.05;
                this.vy -= dy * force * 0.05;
            }

            this.x += this.vx;
            this.y += this.vy;
            this.vx *= 0.95;
            this.vy *= 0.95;

            this.age++;
            if (this.age > this.life) this.reset();

            if (this.x < 0) this.x = width;
            if (this.x > width) this.x = 0;
            if (this.y < 0) this.y = height;
            if (this.y > height) this.y = 0;
        }
        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = 0;
            this.vy = 0;
            this.age = 0;
            this.life = Math.random() * 200 + 100;
        }
        draw(context) {
            context.fillStyle = color;
            const alpha = 1 - Math.abs((this.age / this.life) - 0.5) * 2;
            context.globalAlpha = alpha;
            context.fillRect(this.x, this.y, 1.5, 1.5);
        }
    }

    const init = () => {
        const dpr = window.devicePixelRatio || 1;
        width = container.clientWidth;
        height = container.clientHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        particles = [];
        for (let i = 0; i < particleCount; i++) particles.push(new Particle());
    };

    let lastTime = 0;
    const fpsInterval = 1000 / 60; // Max 60fps

    const animate = (currentTime) => {
        animationFrameId = requestAnimationFrame(animate);

        if (!currentTime) return;
        if (!lastTime) lastTime = currentTime;

        const deltaTime = currentTime - lastTime;
        if (deltaTime < fpsInterval) return;

        // Adjust for any small timing variances to keep steady 60fps
        lastTime = currentTime - (deltaTime % fpsInterval);

        // Theme background is #0a0a0a (rgb: 10,10,10)
        ctx.fillStyle = `rgba(10, 10, 10, ${trailOpacity})`;
        ctx.fillRect(0, 0, width, height);
        particles.forEach(p => { p.update(); p.draw(ctx); });
    };

    const handleResize = () => init();
    const handleMouseMove = (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    };
    const handleMouseLeave = () => { mouse.x = -1000; mouse.y = -1000; };

    init();
    animate();

    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);
}

function openEmailPreview() {
    const preview = document.getElementById('previewOverlay');
    const iframe = document.getElementById('modal_email_preview');

    // Get form values
    const fromName = document.getElementById('from_name')?.value || 'Unknown Sender';
    const fromEmail = document.getElementById('from_email')?.value || 'sender@example.com';
    const toEmail = document.getElementById('to_email')?.value || 'recipient@example.com';
    const subject = document.getElementById('subject')?.value || '(No Subject)';
    const content = document.getElementById('message')?.value || '';
    const isHtml = document.getElementById('html')?.checked;

    // Populate UI
    const sEl = document.getElementById('preview_subject'); if (sEl) sEl.textContent = subject;
    const fnEl = document.getElementById('preview_from_name'); if (fnEl) fnEl.textContent = fromName;
    const feEl = document.getElementById('preview_from_email'); if (feEl) feEl.textContent = `<${fromEmail}>`;
    const toEl = document.getElementById('preview_to'); if (toEl) toEl.textContent = toEmail;

    // Avatar initals
    const initial = fromName.trim().charAt(0).toUpperCase();
    const avEl = document.getElementById('preview_avatar'); if (avEl) avEl.textContent = initial || '?';

    // Date
    const now = new Date();
    const dateStr = now.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
    const dEl = document.getElementById('preview_date'); if (dEl) dEl.textContent = dateStr;

    if (preview && iframe) {
        iframe.style.background = 'transparent'; // Remove white background

        if (isHtml) {
            // Inject a dark mode style to prevent black text on dark background
            const darkStyle = `<style>body { color: #fafafa !important; background-color: #0a0a0a !important; color-scheme: dark; }</style>`;
            let finalHtml = content;
            if (finalHtml.match(/<head[^>]*>/i)) {
                finalHtml = finalHtml.replace(/(<head[^>]*>)/i, `$1${darkStyle}`);
            } else if (finalHtml.match(/<html[^>]*>/i)) {
                finalHtml = finalHtml.replace(/(<html[^>]*>)/i, `$1<head>${darkStyle}</head>`);
            } else {
                finalHtml = `${darkStyle}\n${finalHtml}`;
            }
            iframe.srcdoc = finalHtml;
        } else {
            // Plain text emails get a dark mode styling
            iframe.srcdoc = `
                <html>
                <head>
                    <style>
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                            padding: 24px; 
                            font-size: 14px; 
                            color: #fafafa; 
                            background-color: #0a0a0a;
                            line-height: 1.6; 
                            margin: 0; 
                        }
                    </style>
                </head>
                <body>
                    <div style="white-space: pre-wrap;">${content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                </body>
                </html>
            `;
        }
        preview.classList.add('show');
    }
}

function closePreview() {
    const preview = document.getElementById('previewOverlay');
    if (preview) {
        preview.classList.remove('show');
    }
}

async function applyEvasion(mode) {
    const msg = document.getElementById('message');
    const html = msg.value.trim();
    if (!html) return toast('Message body is empty', 'fail');

    showLoading('Applying evasion...');
    try {
        const r = await fetch('/bypass_html', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ html, mode })
        });
        const data = await r.json();
        hideLoading();
        if (data.success) {
            msg.value = data.obfuscated;
            toast(`Applied ${mode === 'base64' ? 'JS Unwrapper' : 'HTML Entities'}`, 'ok');
            if (typeof openEmailPreview === 'function') {
                // Optionally show preview after transformation
                // openEmailPreview(); 
            }
        } else {
            toast(data.error, 'fail');
        }
    } catch (err) {
        hideLoading();
        toast('Error: ' + err.message, 'fail');
    }
}

// ── Scroll Animations ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = { threshold: 0.15, rootMargin: "0px 0px -50px 0px" };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-on-scroll').forEach(el => {
        observer.observe(el);
    });

    // Handle initial hash navigation
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        if (targetId.startsWith('section-')) {
            switchSection(targetId.replace('section-', ''));
        } else {
            scrollToSection(targetId);
        }
    }
});

// ── Drafts Manager ─────────────────────────────────────────

function openSaveDraftModal() {
    const subject = document.getElementById('subject').value;
    const defaultName = subject ? subject : 'Untitled Draft (' + new Date().toLocaleTimeString() + ')';
    document.getElementById('draft_name_modal').value = defaultName;
    document.getElementById('saveDraftOverlay').classList.add('active');
    setTimeout(() => document.getElementById('draft_name_modal').focus(), 100);
}

function closeSaveDraftModal() {
    document.getElementById('saveDraftOverlay').classList.remove('active');
}

function confirmSaveDraft(btn) {
    const nameInput = document.getElementById('draft_name_modal');
    const name = nameInput.value.trim() || 'Untitled Draft (' + new Date().toLocaleTimeString() + ')';

    const draft = {
        name: name,
        date: new Date().toLocaleString(),
        data: {
            smtp_server: document.getElementById('smtp_server').value,
            smtp_port: document.getElementById('smtp_port').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            from_name: document.getElementById('from_name').value,
            from_email: document.getElementById('from_email').value,
            reply_to: document.getElementById('reply_to').value,
            to_email: document.getElementById('to_email').value,
            subject: document.getElementById('subject').value,
            message: document.getElementById('message').value,
            html: document.getElementById('html').checked,
            send_count: document.getElementById('send_count').value
        }
    };

    let drafts = JSON.parse(localStorage.getItem('mailsploit_drafts') || '[]');
    drafts.unshift(draft);
    localStorage.setItem('mailsploit_drafts', JSON.stringify(drafts));

    nameInput.value = '';
    updateDraftUI();

    // Visual Feedback
    if (btn) {
        const oldHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Saved!';
        btn.style.borderColor = 'var(--pure)';
        setTimeout(() => {
            btn.innerHTML = oldHtml;
            btn.style.borderColor = 'var(--border)';
            closeSaveDraftModal();
        }, 1000);
    } else {
        closeSaveDraftModal();
    }
}

function openDrafts() {
    const drafts = JSON.parse(localStorage.getItem('mailsploit_drafts') || '[]');
    const list = document.getElementById('draftsList');
    const empty = document.getElementById('draftsListEmpty');

    list.innerHTML = '';
    if (drafts.length === 0) {
        empty.style.display = 'block';
    } else {
        empty.style.display = 'none';
        drafts.forEach((d, i) => {
            const card = document.createElement('div');
            card.className = 'draft-card';
            card.innerHTML = `
                <div class="draft-info">
                    <div class="draft-name">${d.name}</div>
                    <div class="draft-meta">${d.date} • ${d.data.subject || '(No Subject)'}</div>
                </div>
                <div class="draft-actions">
                    <button type="button" class="draft-btn" onclick="loadDraft(${i})"><i class="fas fa-upload"></i> Load</button>
                    <button type="button" class="draft-btn draft-btn-delete" onclick="deleteDraft(${i})"><i class="fas fa-trash"></i></button>
                </div>
            `;
            list.appendChild(card);
        });
    }
    document.getElementById('draftsOverlay').classList.add('active');
}

function closeDrafts() {
    document.getElementById('draftsOverlay').classList.remove('active');
}

function loadDraft(index) {
    const drafts = JSON.parse(localStorage.getItem('mailsploit_drafts') || '[]');
    const d = drafts[index];
    if (!d) return;

    const data = d.data;
    for (const key in data) {
        const el = document.getElementById(key);
        if (el) {
            if (el.type === 'checkbox') el.checked = data[key];
            else el.value = data[key];
        }
    }

    closeDrafts();
    // Visual Feedback on Load
    const sendSection = document.getElementById('section-send');
    if (sendSection) {
        sendSection.style.transition = 'background 0.3s ease';
        sendSection.style.background = 'rgba(255,255,255,0.03)';
        setTimeout(() => sendSection.style.background = 'transparent', 500);
    }
}

function deleteDraft(index) {
    let drafts = JSON.parse(localStorage.getItem('mailsploit_drafts') || '[]');
    drafts.splice(index, 1);
    localStorage.setItem('mailsploit_drafts', JSON.stringify(drafts));
    openDrafts(); // refresh list
    updateDraftUI();
}

function updateDraftUI() {
    const drafts = JSON.parse(localStorage.getItem('mailsploit_drafts') || '[]');
    const count = document.getElementById('draftCount');
    if (count) count.innerText = drafts.length;
}

// Initial UI Sync
document.addEventListener('DOMContentLoaded', () => {
    updateDraftUI();
});
