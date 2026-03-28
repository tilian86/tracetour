// Cloudflare Worker – TraceTour AI Proxy
// Deploy: https://developers.cloudflare.com/workers/
// 1. npx wrangler init tracetour-ai
// 2. Paste this code into src/index.js
// 3. npx wrangler secret put ANTHROPIC_API_KEY (paste your key)
// 4. npx wrangler deploy
// 5. Set the worker URL in index.html: window.TRACETOUR_AI_ENDPOINT = 'https://tracetour-ai.<your-subdomain>.workers.dev'

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
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
      const body = await request.json();

      // Validate: only allow our model, short messages, limited tokens
      if (body.max_tokens > 300) body.max_tokens = 300;
      body.model = 'claude-haiku-4-5-20251001'; // Force Haiku regardless of client request

      // Only allow single short user message
      if (!body.messages || body.messages.length !== 1 || body.messages[0].role !== 'user') {
        return new Response(JSON.stringify({ error: 'Invalid request' }), {
          status: 400,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
      }

      // Limit user message length
      if (body.messages[0].content.length > 500) {
        body.messages[0].content = body.messages[0].content.slice(0, 500);
      }

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
