// TraceTour Checkout Worker
// - POST /webhook   : Stripe checkout.session.completed -> Code vergeben + Mail via Resend
// - GET  /code      : ?session_id=cs_... -> Code für die Danke-Seite (Fallback ohne Mail)
// - POST /validate  : {code} -> Code gültig? (App-Login)
// Idempotent: pro Stripe-Session wird genau ein Code vergeben (Retry-sicher).

const JSON_HEADERS = { 'content-type': 'application/json' };

function cors(env) {
  return {
    'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || 'https://tracetour.de',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type',
  };
}

export default {
  async fetch(request, env, ctx) {
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
  if (!sigHeader) return false;
  const parts = Object.fromEntries(sigHeader.split(',').map(p => p.split('=')));
  const t = parts.t, v1 = parts.v1;
  if (!t || !v1) return false;
  // Toleranz: 5 Minuten gegen Replay
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const mac = await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${payload}`));
  const expected = [...new Uint8Array(mac)].map(b => b.toString(16).padStart(2, '0')).join('');
  // Konstantzeit-Vergleich
  if (expected.length !== v1.length) return false;
  let diff = 0;
  for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ v1.charCodeAt(i);
  return diff === 0;
}

// ---------- Webhook ----------
async function handleWebhook(request, env) {
  const payload = await request.text();
  const ok = await verifyStripeSignature(payload, request.headers.get('stripe-signature'), env.STRIPE_WEBHOOK_SECRET || '');
  if (!ok) return new Response('Bad signature', { status: 400 });

  const event = JSON.parse(payload);
  if (event.type !== 'checkout.session.completed') {
    return new Response(JSON.stringify({ received: true, ignored: event.type }), { headers: JSON_HEADERS });
  }

  const session = event.data.object;
  const sessionId = session.id;
  const email = session.customer_details?.email || session.customer_email || '';
  const name = session.customer_details?.name || '';
  // Tour-Bindung: Payment-Link-Metadata wird von Stripe in die Session kopiert
  const tour = session.metadata?.tour === 'kids' ? 'kids' : 'adult';

  // Idempotenz: gibt es für diese Session schon einen Code?
  const existing = await env.CODES.get(`session:${sessionId}`);
  let code;
  if (existing) {
    code = JSON.parse(existing).code;
  } else {
    code = await assignCode(env, { sessionId, email, name, tour });
    if (!code) {
      console.error('CODE POOL EMPTY!');
      return new Response('No codes left', { status: 500 }); // Stripe retried -> Zeit zum Nachfüllen
    }
  }

  // Mail senden (nicht fatal wenn's fehlschlägt: /code-Fallback existiert,
  // aber 500 zurückgeben, damit Stripe es erneut versucht, solange Resend fehlt)
  const mailed = await sendCodeMail(env, { to: email, name, code, tour });
  if (!mailed) {
    console.warn(`Mail fehlgeschlagen für ${sessionId} (Code ${code}) — Stripe wird retryn`);
    return new Response('Mail failed, will retry', { status: 500 });
  }
  return new Response(JSON.stringify({ received: true }), { headers: JSON_HEADERS });
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
      status: 'assigned', tour: meta.tour, session: meta.sessionId, email: meta.email, name: meta.name, ts: Date.now(),
    }));
    await env.CODES.put(`session:${meta.sessionId}`, JSON.stringify({ code, tour: meta.tour, ts: Date.now() }));
    await env.CODES.put('meta:counter', String(counter + 1));
    return code;
  }
  return null;
}

async function sendCodeMail(env, { to, name, code, tour }) {
  if (!env.RESEND_API_KEY || !to) return false;
  const first = (name || '').split(' ')[0] || 'Entdecker/in';
  const kids = tour === 'kids';
  const tourName = kids ? 'TraceTour Kids – Tübis Geheimnisse' : 'TraceTour Tübingen';
  const tourUrl = kids ? 'https://tracetour.de/kinder.html' : 'https://tracetour.de/app.html';
  const startHint = kids
    ? 'Startet am Marktplatz beim Rathaus – Tübi wartet schon! 🐉'
    : 'Starte am Schloss Hohentübingen – und folge Heinrichs Spur 🔍';
  const body = {
    from: env.FROM_EMAIL,
    to: [to],
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
  <p style="font-size:.85rem;color:#64748b">Tipp: Lade die Tour vorher im WLAN für unterwegs herunter. Kopfhörer oder Lautsprecher nicht vergessen!</p>
  <p style="font-size:.85rem;color:#64748b">Fragen? Antworte einfach auf diese E-Mail.<br>TraceTour – by Florian S. Thiel · <a href="https://tracetour.de">tracetour.de</a></p>
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

// ---------- App-Login: Code validieren ----------
async function handleValidate(request, env) {
  let body;
  try { body = await request.json(); } catch { body = {}; }
  const code = String(body.code || '').trim().toUpperCase();
  if (!/^TT-[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(code)) {
    return new Response(JSON.stringify({ valid: false, reason: 'format' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
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

  // Geräte-Limit gegen Weitergabe: ein Code darf auf maximal DEVICE_CAP verschiedenen
  // Geräten aktiviert werden. Familie/Zweitgerät/Neuinstallation = ok, WhatsApp-Gruppe = blockiert.
  const DEVICE_CAP = parseInt(env.DEVICE_CAP || '4', 10);
  const device = String(body.device || '').slice(0, 64);
  state.devices = Array.isArray(state.devices) ? state.devices : [];
  const known = device && state.devices.includes(device);
  if (!known) {
    if (state.devices.length >= DEVICE_CAP) {
      return new Response(JSON.stringify({ valid: false, reason: 'device_limit' }), { headers: { ...JSON_HEADERS, ...cors(env) } });
    }
    if (device) state.devices.push(device);
  }
  if (!state.firstUse) state.firstUse = Date.now();
  await env.CODES.put(`code:${code}`, JSON.stringify(state));
  return new Response(JSON.stringify({ valid: true, devicesUsed: state.devices.length, deviceCap: DEVICE_CAP }), { headers: { ...JSON_HEADERS, ...cors(env) } });
}
