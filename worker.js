// Cloudflare Worker – TraceTour AI Proxy
// Deploy: https://developers.cloudflare.com/workers/
// 1. npx wrangler init tracetour-ai
// 2. Paste this code into src/index.js
// 3. npx wrangler secret put ANTHROPIC_API_KEY (paste your key)
// 4. npx wrangler deploy
// 5. Set the worker URL in index.html: window.TRACETOUR_AI_ENDPOINT = 'https://tracetour-ai.<your-subdomain>.workers.dev'

// Nur Aufrufe von der eigenen Seite (Browser schicken Origin immer mit)
const ALLOWED_ORIGINS = ['https://tracetour.de', 'https://www.tracetour.de', 'http://localhost:8000', 'http://localhost:8767'];
const BASE_CORS = {
  'Access-Control-Allow-Origin': 'https://tracetour.de',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Vary': 'Origin',
};

// Rate limiting: max requests per IP per hour
const RATE_LIMIT = 30;
const rateLimitMap = new Map();

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  if (!entry || now - entry.start > 3600000) {
    rateLimitMap.set(ip, { start: now, count: 1 });
    return true;
  }
  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (!ALLOWED_ORIGINS.includes(origin)) {
      return new Response('Forbidden', { status: 403 });
    }
    const CORS_HEADERS = { ...BASE_CORS, 'Access-Control-Allow-Origin': origin };
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: CORS_HEADERS });
    }

    // Rate limit
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (!checkRateLimit(ip)) {
      return new Response(JSON.stringify({ error: 'Rate limit exceeded' }), {
        status: 429,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    try {
      const input = await request.json();

      // Nur genau eine kurze Nutzerfrage
      const msg = Array.isArray(input.messages) && input.messages.length === 1 ? input.messages[0] : null;
      if (!msg || msg.role !== 'user' || typeof msg.content !== 'string') {
        return new Response(JSON.stringify({ error: 'Invalid request' }), {
          status: 400,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
      }

      // Nur erlaubte Felder weiterreichen (keine Tools, kein Streaming, festes Modell)
      const body = {
        model: 'claude-haiku-4-5-20251001',
        max_tokens: Math.min(300, parseInt(input.max_tokens, 10) || 300),
        ...(input.system ? { system: String(input.system).slice(0, 6000) } : {}),
        messages: [{ role: 'user', content: msg.content.slice(0, 500) }],
      };

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      return new Response(JSON.stringify(data), {
        status: response.status,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: 'Internal error' }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }
  },
};
