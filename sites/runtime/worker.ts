interface Statement {
  bind(...values: (string | number)[]): Statement;
  run(): Promise<unknown>;
}
interface Environment {
  DB: { prepare(sql: string): Statement };
  ASSETS: { fetch(request: Request): Promise<Response> };
}
const headers = { 'Cache-Control': 'no-store', 'Content-Type': 'application/json; charset=utf-8' };
function reply(status: number, message: string): Response {
  return new Response(JSON.stringify({ message }), { status, headers });
}
export async function saveFeedback(request: Request, env: Environment): Promise<Response> {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } });
  if (request.headers.get('Origin') !== new URL(request.url).origin) return reply(403, 'Please send feedback from this site.');
  if (!request.headers.get('Content-Type')?.startsWith('application/json')) return reply(415, 'Expected JSON.');
  if (Number(request.headers.get('Content-Length')) > 8192) return reply(413, 'Message too long.');
  const reader = request.body?.getReader();
  if (!reader) return reply(400, 'Please include a message.');
  const chunks: Uint8Array[] = [];
  let length = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    length += value.byteLength;
    if (length > 8192) { await reader.cancel(); return reply(413, 'Message too long.'); }
    chunks.push(value);
  }
  let input: unknown;
  try {
    const bytes = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
    input = JSON.parse(new TextDecoder().decode(bytes));
  } catch { return reply(400, 'Please check your message.'); }
  if (!input || typeof input !== 'object') return reply(400, 'Please include a message.');
  const fields = input as Record<string, unknown>;
  if (fields.website) return reply(400, 'Please check your message.');
  if (typeof fields.id !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(fields.id)) return reply(400, 'Please try again.');
  if (typeof fields.message !== 'string' || fields.message.trim().length < 5 || fields.message.trim().length > 2000) return reply(400, 'Use 5–2,000 characters.');
  if (typeof fields.category !== 'string' || !['idea', 'correction', 'view'].includes(fields.category)) return reply(400, 'Choose a category.');
  const allowedPages = ['/', '/index', '/3d', '/gallery', '/map', '/build', '/process', '/index.html', '/3d.html', '/gallery.html', '/map.html', '/build.html', '/process.html'];
  if (typeof fields.page !== 'string' || !allowedPages.includes(fields.page)) return reply(400, 'Unknown page.');
  // A retry after an uncertain network response must not create a second entry.
  await env.DB.prepare('INSERT INTO feedback (id, message, category, page, created_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING')
    .bind(fields.id, fields.message.trim(), fields.category, fields.page, Date.now()).run();
  return reply(201, 'Saved.');
}
export default {
  async fetch(request: Request, env: Environment): Promise<Response> {
    const path = new URL(request.url).pathname;
    if (path === '/map' || path === '/map.html') return Response.redirect(new URL('/', request.url), 302);
    if (path !== '/api/feedback') return env.ASSETS.fetch(request);
    try { return await saveFeedback(request, env); }
    catch (error: unknown) {
      console.error('Feedback save failed', error instanceof Error ? error.name : 'UnknownError');
      return reply(503, 'Feedback could not be saved. Please try again.');
    }
  },
};
