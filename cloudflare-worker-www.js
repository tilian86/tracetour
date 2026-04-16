/**
 * TraceTour www-Proxy Worker
 *
 * Liefert www.tracetour.de Inhalte DIREKT aus (kein Redirect).
 * Verhindert das WhatsApp/iMessage Preview-Problem bei Redirects.
 *
 * Setup:
 * 1. Cloudflare Dashboard → Workers & Pages → Create
 * 2. Diesen Code einfügen, deployen
 * 3. Worker Route: www.tracetour.de/* → dieser Worker
 * 4. Bestehende Bulk Redirects für www entfernen
 */

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Hostname von www.tracetour.de auf tracetour.de ändern
    url.hostname = "tracetour.de";

    // Originalen Request mit gleichen Headers/Body weiterleiten
    const proxiedRequest = new Request(url.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "follow",
    });

    // Response 1:1 zurückgeben
    const response = await fetch(proxiedRequest, {
      cf: {
        cacheTtl: 3600,
        cacheEverything: true,
      },
    });

    // Neue Response erstellen damit Headers modifizierbar sind
    const newResponse = new Response(response.body, response);

    // Cache-Control für Browser
    newResponse.headers.set("Cache-Control", "public, max-age=3600");

    return newResponse;
  },
};
