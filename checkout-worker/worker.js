// TraceTour Checkout Worker
// - POST /webhook   : Stripe checkout.session.completed -> Code vergeben + Mail via Resend
// - GET  /code      : ?session_id=cs_... -> Code für die Danke-Seite (Fallback ohne Mail)
// - POST /validate  : {code} -> Code gültig? (App-Login)
// Idempotent: pro Stripe-Session wird genau ein Code vergeben (Retry-sicher).
//
// Testcodes stehen NICHT im Quelltext, sondern im Secret TESTER_CODES (kommagetrennt):
//   npx wrangler secret put TESTER_CODES
//   Wert z. B.: TT-ABCD-EFGH=adult, TT-JKLM-NPQR=kids, TT-STUV-WXYZ=both+debug, TT-HJKM-2345=adult+personal
//   Flags: adult | kids | both (Tour), debug (Debug-Leiste), personal (persönliche Begrüßung)
// Testcodes haben kein Geräte-Limit und kein 48-h-Fenster. Sperren = Code aus dem Secret löschen.

const JSON_HEADERS = { 'content-type': 'application/json' };

function cors(env) {
  return {
    'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || 'https://tracetour.de',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type',
    'Vary': 'Origin',
  };
}

// ALLOWED_ORIGIN darf eine Komma-Liste sein (z. B. + http://localhost:8767 zum lokalen Testen);
// geantwortet wird mit dem passenden Eintrag, sonst dem ersten.
function pickOrigin(request, env) {
  const list = String(env.ALLOWED_ORIGIN || 'https://tracetour.de').split(',').map(o => o.trim()).filter(Boolean);
  const origin = request.headers.get('Origin');
  return list.includes(origin) ? origin : list[0];
}

export default {
  async fetch(request, env, ctx) {
    env = { ...env, ALLOWED_ORIGIN: pickOrigin(request, env) };
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: cors(env) });
    }
    try {
      if (url.pathname === '/webhook' && request.method === 'POST') {
        return await handleWebhook(request, env);
      }
      if (url.pathname === '/code' && request.method === 'GET') {
        return await handleGetCode(url, env);
      }
      if (url.pathname === '/validate' && request.method === 'POST') {
        return await handleValidate(request, env);
      }
      return new Response('Not found', { status: 404 });
    } catch (err) {
      console.error('Unhandled:', err.stack || err);
      return new Response(JSON.stringify({ error: 'internal' }), { status: 500, headers: JSON_HEADERS });
    }
  },
};

// ---------- Stripe-Signatur (HMAC-SHA256, v1-Schema) ----------
async function verifyStripeSignature(payload, sigHeader, secret) {
  if (!sigHeader || !secret) return false; // ohne Secret nie annehmen (sonst fälschbar)
  const pairs = sigHeader.split(',').map(p => p.split('='));
  const t = (pairs.find(([k]) => k === 't') || [])[1];
  // Bei Secret-Wechsel schickt Stripe mehrere v1-Signaturen → jede prüfen
  const sigs = pairs.filter(([k]) => k === 'v1').map(([, v]) => v || '');
  if (!t || !sigs.length) return false;
  // Toleranz: 5 Minuten gegen Replay
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const mac = await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${payload}`));
  const expected = [...new Uint8Array(mac)].map(b => b.toString(16).padStart(2, '0')).join('');
  // Konstantzeit-Vergleich
  return sigs.some(v1 => {
    if (expected.length !== v1.length) return false;
    let diff = 0;
    for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ v1.charCodeAt(i);
    return diff === 0;
  });
}

// ---------- Webhook ----------
async function handleWebhook(request, env) {
  const payload = await request.text();
  const ok = await verifyStripeSignature(payload, request.headers.get('stripe-signature'), env.STRIPE_WEBHOOK_SECRET || '');
  if (!ok) return new Response('Bad signature', { status: 400 });

  const event = JSON.parse(payload);
  // completed = Kauf abgeschlossen; async_payment_succeeded = verspätete Zahlung (z. B. Lastschrift) ist angekommen
  if (event.type !== 'checkout.session.completed' && event.type !== 'checkout.session.async_payment_succeeded') {
    return new Response(JSON.stringify({ received: true, ignored: event.type }), { headers: JSON_HEADERS });
  }

  const session = event.data.object;
  // Noch nicht bezahlt (verzögerte Zahlungsart) → Code erst bei async_payment_succeeded vergeben
  if (session.payment_status === 'unpaid') {
    return new Response(JSON.stringify({ received: true, pending: true }), { headers: JSON_HEADERS });
  }
  const sessionId = session.id;
  const email = session.customer_details?.email || session.customer_email || '';
  const name = session.customer_details?.name || '';
  // Tour-Bindung: Payment-Link-Metadata wird von Stripe in die Session kopiert
  const tour = session.metadata?.tour === 'kids' ? 'kids' : 'adult';
  // Geräte-Limit pro Ticket (Payment-Link-Metadatum `devices`); fehlt es, gilt DEVICE_CAP
  const cap = parseInt(session.metadata?.devices, 10) || null;

  // Idempotenz: gibt es für diese Session schon einen Code?
  const existingRaw = await env.CODES.get(`session:${sessionId}`);
  const existing = existingRaw ? JSON.parse(existingRaw) : null;
  // Schon gemailt (Stripe-Wiederholung) → nichts doppelt schicken
  if (existing?.mailed) {
    return new Response(JSON.stringify({ received: true, duplicate: true }), { headers: JSON_HEADERS });
  }
  let code;
  if (existing) {
    code = existing.code;
  } else {
    code = await assignCode(env, { sessionId, email, name, tour, cap });
    if (!code) {
      console.error('CODE POOL EMPTY!');
      await sendAlert(env, 'TraceTour: Code-Vorrat LEER', `Ein Kauf (Session ${sessionId}) wartet auf einen Code. Bitte sofort Codes nachfüllen – Stripe wiederholt den Webhook noch einige Tage.`);
      return new Response('No codes left', { status: 500 }); // Stripe retried -> Zeit zum Nachfüllen
    }
  }

  // Ohne E-Mail-Adresse (sollte bei Payment Links nie vorkommen): Code steht auf der Danke-Seite,
  // Wiederholungen würden nichts ändern → sauber beenden statt endlos 500
  if (!email) {
    console.warn(`Keine E-Mail für ${sessionId} — Code nur über Danke-Seite`);
    return new Response(JSON.stringify({ received: true, no_email: true }), { headers: JSON_HEADERS });
  }

  // Mail senden (nicht fatal wenn's fehlschlägt: /code-Fallback existiert,
  // aber 500 zurückgeben, damit Stripe es erneut versucht, solange Resend fehlt)
  const mailed = await sendCodeMail(env, { to: email, name, code, tour, cap: cap || parseInt(env.DEVICE_CAP || '4', 10), session });
  if (!mailed) {
    console.warn(`Mail fehlgeschlagen für ${sessionId} (Code ${code}) — Stripe wird retryn`);
    return new Response('Mail failed, will retry', { status: 500 });
  }
  const entry = JSON.parse((await env.CODES.get(`session:${sessionId}`)) || '{}');
  await env.CODES.put(`session:${sessionId}`, JSON.stringify({ ...entry, code, tour, mailed: true }));
  return new Response(JSON.stringify({ received: true }), { headers: JSON_HEADERS });
}

// Warnmail an Florian (höchstens einmal pro Tag je Betreff)
async function sendAlert(env, subject, text) {
  const to = env.ALERT_EMAIL || 'info@tracetour.de';
  if (!env.RESEND_API_KEY) return;
  const flag = `meta:alert:${subject}`;
  if (await env.CODES.get(flag)) return;
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: env.FROM_EMAIL, to, subject, text }),
    });
    await env.CODES.put(flag, '1', { expirationTtl: 86400 });
  } catch (e) { console.error('Alert-Mail fehlgeschlagen', e); }
}

async function assignCode(env, meta) {
  // Zähler-basierte Vergabe. KV ist eventually consistent — bei sehr zeitgleichen
  // Käufen theoretisch derselbe Index; darum bis zu 5 Indizes probieren und
  // den Code-Status als Wahrheit nehmen.
  for (let attempt = 0; attempt < 5; attempt++) {
    const counter = parseInt((await env.CODES.get('meta:counter')) || '0', 10) + attempt;
    const code = await env.CODES.get(`idx:${counter}`);
    if (!code) return null; // Pool erschöpft
    const state = JSON.parse((await env.CODES.get(`code:${code}`)) || '{}');
    if (state.status !== 'unused') continue;
    await env.CODES.put(`code:${code}`, JSON.stringify({
      status: 'assigned', tour: meta.tour, cap: meta.cap || undefined, session: meta.sessionId, email: meta.email, name: meta.name, ts: Date.now(),
    }));
    await env.CODES.put(`session:${meta.sessionId}`, JSON.stringify({ code, tour: meta.tour, ts: Date.now() }));
    await env.CODES.put('meta:counter', String(counter + 1));
    // Frühwarnung: weniger als 50 Codes übrig
    if (!(await env.CODES.get(`idx:${counter + 50}`))) {
      await sendAlert(env, 'TraceTour: Code-Vorrat fast leer', `Nach Code Nr. ${counter + 1} sind weniger als 50 Codes übrig. Bitte nachfüllen.`);
    }
    return code;
  }
  return null;
}

// Rechtstexte als PDF-Anhang (Vertragsbestätigung nach § 312f BGB). Bei neuer AGB-Fassung:
// neue PDFs mit neuem Datum in /rechtstexte/ ablegen und hier eintragen (alte bleiben liegen).
const LEGAL_PDFS = [
  { filename: 'TraceTour-AGB.pdf', url: 'https://tracetour.de/rechtstexte/agb-2026-11-18.pdf' },
  { filename: 'TraceTour-Widerrufsbelehrung.pdf', url: 'https://tracetour.de/rechtstexte/widerruf-2026-11-18.pdf' },
];

const TICKETS = {
  solo: 'Solo-Ermittler (1 Person, bis 2 Handys)',
  kids: 'Kindertour mit Tübi (1 Familie, bis 2 Handys)',
  team: 'Ermittler-Team (bis 5 Personen, bis 5 Handys)',
  class: 'Schulklasse (bis 30 Schüler/innen plus Begleitung, bis 10 Handys)',
};

function ticketLabel(session, tour, cap) {
  const t = String(session?.metadata?.ticket || '').toLowerCase();
  if (TICKETS[t]) return TICKETS[t];
  if (tour === 'kids') return TICKETS.kids;
  if (cap >= 10) return TICKETS.class;
  if (cap >= 5) return TICKETS.team;
  return TICKETS.solo;
}

function euro(cents) {
  return (cents / 100).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' });
}

function toBase64(buf) {
  const bytes = new Uint8Array(buf);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

async function legalAttachments(env) {
  try {
    const files = await Promise.all(LEGAL_PDFS.map(async f => {
      const r = await fetch(f.url, { cf: { cacheTtl: 3600 } });
      if (!r.ok) throw new Error(`${f.url} → ${r.status}`);
      return { filename: f.filename, content: toBase64(await r.arrayBuffer()) };
    }));
    return files;
  } catch (e) {
    console.error('Rechtstexte-PDF fehlt:', e);
    await sendAlert(env, 'TraceTour: AGB-PDF für Kauf-Mail fehlt', `Die Kauf-Mail ging ohne PDF-Anhang raus (${e.message}). Bitte /rechtstexte/ prüfen.`);
    return [];
  }
}

async function sendCodeMail(env, { to, name, code, tour, cap, session }) {
  if (!env.RESEND_API_KEY || !to) return false;
  const first = (name || '').split(' ')[0] || 'Entdecker/in';
  const kids = tour === 'kids';
  const tourName = kids ? 'TraceTour Kids – Tübis Geheimnisse' : 'TraceTour Tübingen';
  const tourUrl = kids ? 'https://tracetour.de/kinder.html' : 'https://tracetour.de/app.html';
  const startHint = kids
    ? 'Startet am Marktplatz beim Rathaus – Tübi wartet schon! 🐉'
    : 'Starte am Schloss Hohentübingen – und folge Heinrichs Spur 🔍';
  const ticket = ticketLabel(session, tour, cap);
  const total = Number.isFinite(session?.amount_total) ? session.amount_total : null;
  const discount = session?.total_details?.amount_discount || 0;
  const priceText = total === null ? '–' : `${euro(total)}${discount > 0 ? ` (Gutschein: −${euro(discount)})` : ''}`;
  const orderDate = new Date((session?.created || Date.now() / 1000) * 1000)
    .toLocaleString('de-DE', { timeZone: 'Europe/Berlin', dateStyle: 'long', timeStyle: 'short' });
  const orderNo = String(session?.id || '').slice(-10).toUpperCase();
  const attachments = await legalAttachments(env);
  const td = 'style="padding:2px 12px 2px 0;vertical-align:top;color:#64748b"';
  const body = {
    from: env.FROM_EMAIL,
    to: [to],
    reply_to: 'info@tracetour.de',
    ...(attachments.length ? { attachments } : {}),
    subject: `Dein Zugangscode für ${tourName}: ${code}`,
    html: `
<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:560px;margin:0 auto;padding:24px;color:#1e293b">
  <h1 style="font-size:1.4rem">Willkommen bei ${tourName}, ${escapeHtml(first)}! ${kids ? '🐉' : '🔍'}</h1>
  <p>vielen Dank für deinen Kauf. Hier ist dein persönlicher Zugangscode:</p>
  <div style="background:${kids ? '#006a2d' : '#1e293b'};color:#fff;font-size:1.6rem;font-weight:800;letter-spacing:2px;text-align:center;padding:18px;border-radius:12px;margin:20px 0">${code}</div>
  <p><strong>So geht's los:</strong></p>
  <ol>
    <li>Öffne <a href="${tourUrl}">${tourUrl.replace('https://', '')}</a> auf deinem Smartphone</li>
    <li>Gib den Code ein${kids ? ' und euren Drachenkind-Namen' : ' und wähle deinen Ermittler-Namen'}</li>
    <li>${startHint}</li>
  </ol>
  <p style="font-size:.85rem;color:#64748b">Tipp: Lade die Tour am Tag eurer Tour vorher im WLAN herunter (dann startet auch die 48-Stunden-Zeit). Kopfhörer oder Lautsprecher nicht vergessen!</p>
  <p style="font-size:.8rem;color:#94a3b8">Gut zu wissen: Der Code läuft auf bis zu ${cap} Handys. Ab dem ersten Start habt ihr 48 Stunden Zeit, weitere Handys dazuzunehmen und die Tour so oft zu spielen, wie ihr wollt. Aktiviere den Code also erst, wenn ihr wirklich losgeht. Einlösbar bis 12 Monate nach Kauf.</p>
  <p style="font-size:.85rem;color:#64748b">Fragen? Antworte einfach auf diese E-Mail.</p>
  <h2 style="font-size:1rem;margin:28px 0 8px">Deine Bestellung</h2>
  <table style="font-size:.85rem;color:#1e293b;border-collapse:collapse">
    <tr><td ${td}>Ticket</td><td>${ticket}</td></tr>
    <tr><td ${td}>Tour</td><td>${tourName}</td></tr>
    <tr><td ${td}>Bezahlt</td><td>${priceText}</td></tr>
    <tr><td ${td}>Bestellt am</td><td>${orderDate} Uhr</td></tr>
    <tr><td ${td}>Bestellnummer</td><td>${orderNo}</td></tr>
  </table>
  <p style="font-size:.8rem;color:#64748b">Alle Preise sind Endpreise. Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.</p>
  <p style="font-size:.8rem;color:#64748b"><strong>Bestätigung zum Widerrufsrecht:</strong> Du hast beim Kauf ausdrücklich zugestimmt, dass wir vor Ablauf der Widerrufsfrist mit der Bereitstellung der digitalen Inhalte beginnen, und bestätigt, dass dein Widerrufsrecht damit erlischt. Mit dieser E-Mail und dem Zugangscode haben wir begonnen.</p>
  <p style="font-size:.8rem;color:#64748b">Unsere AGB und die Widerrufsbelehrung ${attachments.length ? 'hängen als PDF an dieser E-Mail und stehen auch' : 'stehen'} unter <a href="https://tracetour.de/agb.html" style="color:#64748b">tracetour.de/agb.html</a> und <a href="https://tracetour.de/widerruf.html" style="color:#64748b">tracetour.de/widerruf.html</a>.</p>
  <p style="font-size:.75rem;color:#94a3b8;border-top:1px solid #e2e8f0;padding-top:12px;margin-top:20px">Anbieter: Florian S. Thiel – TraceTour · Sonnenhalde 72 · 72829 Engstingen · Telefon +49 1525 9295405 · <a href="mailto:info@tracetour.de" style="color:#94a3b8">info@tracetour.de</a> · <a href="https://tracetour.de" style="color:#94a3b8">tracetour.de</a></p>
</div>`,
  };
  try {
    const resp = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!resp.ok) console.error('Resend error:', resp.status, await resp.text());
    return resp.ok;
  } catch (e) {
    console.error('Resend fetch failed:', e);
    return false;
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// ---------- Danke-Seite: Code per Session-ID abholen ----------
async function handleGetCode(url, env) {
  const sessionId = url.searchParams.get('session_id') || '';
  if (!/^cs_(test|live)_[a-zA-Z0-9]+$/.test(sessionId)) {
    return new Response(JSON.stringify({ error: 'bad_session' }), { status: 400, headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  // Webhook kann ein paar Sekunden nach Redirect eintreffen — Danke-Seite pollt.
  const entry = await env.CODES.get(`session:${sessionId}`);
  if (!entry) {
    return new Response(JSON.stringify({ pending: true }), { status: 202, headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  const e = JSON.parse(entry);
  return new Response(JSON.stringify({ code: e.code, tour: e.tour || 'adult' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
}

// ---------- Testcodes (aus Secret, nicht im Repo) ----------
function findTesterCode(env, code) {
  for (const entry of String(env.TESTER_CODES || '').split(',')) {
    const [c, flagStr = ''] = entry.split('=');
    if (!c || c.trim().toUpperCase() !== code) continue;
    const flags = flagStr.toLowerCase().split('+').map(f => f.trim());
    return {
      tour: flags.includes('both') ? 'both' : flags.includes('kids') ? 'kids' : 'adult',
      debug: flags.includes('debug'),
      personal: flags.includes('personal'),
    };
  }
  return null;
}

// ---------- App-Login: Code validieren ----------
async function handleValidate(request, env) {
  let body;
  try { body = await request.json(); } catch { body = {}; }
  const code = String(body.code || '').trim().toUpperCase();
  if (!/^TT-[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(code)) {
    return new Response(JSON.stringify({ valid: false, reason: 'format' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  const tester = findTesterCode(env, code);
  if (tester) {
    const wanted = body.tour === 'kids' ? 'kids' : 'adult';
    if (tester.tour !== 'both' && tester.tour !== wanted) {
      return new Response(JSON.stringify({ valid: false, reason: 'wrong_tour', codeTour: tester.tour }), { headers: { ...JSON_HEADERS, ...cors(env) } });
    }
    // tours: für welche Touren der Code gilt – die Seite code.html bietet bei beiden eine Auswahl an
    const tours = tester.tour === 'both' ? ['adult', 'kids'] : [tester.tour];
    return new Response(JSON.stringify({ valid: true, tester: true, debug: tester.debug, personal: tester.personal, tours }), { headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  const state = JSON.parse((await env.CODES.get(`code:${code}`)) || 'null');
  if (!state || state.status !== 'assigned') {
    return new Response(JSON.stringify({ valid: false, reason: 'unknown' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  // Tour-Bindung: Code gilt nur für die gekaufte Tour
  const requestedTour = body.tour === 'kids' ? 'kids' : 'adult';
  const codeTour = state.tour || 'adult';
  if (codeTour !== requestedTour) {
    return new Response(JSON.stringify({ valid: false, reason: 'wrong_tour', codeTour }), { headers: { ...JSON_HEADERS, ...cors(env) } });
  }

  // Schutz gegen Weitergabe — zwei kombinierte Schranken:
  //  1) Aktivierungs-Zeitfenster: ab dem ersten Start bleibt der Code ACTIVATION_HOURS lang
  //     aktivierbar. Danach wird KEIN neues Gerät mehr freigeschaltet (Code "verglüht").
  //  2) Geräte-Limit: maximal DEVICE_CAP verschiedene Geräte insgesamt.
  // Bereits aktivierte (bekannte) Geräte bleiben IMMER gültig — kein Rauswurf mitten in der Tour,
  // auch offline. Nur NEUE Geräte unterliegen Fenster + Limit. So wird das Durchschleusen
  // (Code an Freunde weitergeben) gestoppt, ohne den ehrlichen Käufer zu behindern.
  // Limit pro Code (beim Kauf aus dem Payment Link übernommen), sonst global
  const DEVICE_CAP = parseInt(state.cap, 10) || parseInt(env.DEVICE_CAP || '4', 10);
  const WINDOW_MS = parseInt(env.ACTIVATION_HOURS || '48', 10) * 3600 * 1000;
  const device = String(body.device || '').slice(0, 64);
  // Ohne Geräte-Kennung würde das Limit nicht greifen (alle Seiten schicken sie mit)
  if (!device) {
    return new Response(JSON.stringify({ valid: false, reason: 'format' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
  }
  const now = Date.now();
  state.devices = Array.isArray(state.devices) ? state.devices : [];
  const known = device && state.devices.includes(device);
  if (!known) {
    // Fenster nur prüfen, wenn der Code schon einmal aktiviert wurde
    if (state.firstUse && WINDOW_MS > 0 && (now - state.firstUse) > WINDOW_MS) {
      return new Response(JSON.stringify({ valid: false, reason: 'expired' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
    }
    if (state.devices.length >= DEVICE_CAP) {
      return new Response(JSON.stringify({ valid: false, reason: 'device_limit' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
    }
    if (device) state.devices.push(device);
    if (!state.firstUse) state.firstUse = now;
  }
  await env.CODES.put(`code:${code}`, JSON.stringify(state));
  const hoursLeft = state.firstUse ? Math.max(0, Math.round((state.firstUse + WINDOW_MS - now) / 3600000)) : Math.round(WINDOW_MS / 3600000);
  return new Response(JSON.stringify({ valid: true, devicesUsed: state.devices.length, deviceCap: DEVICE_CAP, hoursLeft, tours: [codeTour] }), { headers: { ...JSON_HEADERS, ...cors(env) } });
}
