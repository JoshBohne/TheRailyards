import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync, mkdtempSync, rmSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import worker from './worker.ts';
const payload = { id: '15497227-cd50-4b1b-8a9b-774f2febca20', message: 'A view from the right-field terrace', category: 'view', page: '/build', website: '' };
function request(body: unknown = payload, origin = 'https://example.test') {
  return new Request('https://example.test/api/feedback', { method: 'POST', headers: { Origin: origin, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
}
test('feedback persists across reopening the database and retries create one record', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'railyards-feedback-'));
  const path = join(dir, 'feedback.sqlite');
  let database = new DatabaseSync(path);
  const migration = readdirSync(new URL('./drizzle/', import.meta.url)).find(name => name.endsWith('.sql'))!;
  database.exec(readFileSync(new URL(`./drizzle/${migration}`, import.meta.url), 'utf8'));
  const env = { DB: { prepare(sql: string) { return { bind(...values: (string | number)[]) { return { bind: this.bind, async run() { return database.prepare(sql).run(...values); } }; }, async run() { return database.prepare(sql).run(); } }; } }, ASSETS: { async fetch() { return new Response('asset'); } } };
  assert.equal((await worker.fetch(request(), env)).status, 201);
  database.close(); database = new DatabaseSync(path);
  assert.equal((await worker.fetch(request(), env)).status, 201);
  assert.equal(database.prepare('SELECT count(*) AS count FROM feedback').get()?.count, 1);
  assert.equal(database.prepare('SELECT message FROM feedback').get()?.message, payload.message);
  assert.equal((await worker.fetch(request({ ...payload, message: '   ' }), env)).status, 400);
  assert.equal((await worker.fetch(request(payload, 'https://elsewhere.test'), env)).status, 403);
  assert.equal((await worker.fetch(request({ ...payload, message: 'x'.repeat(9000) }), env)).status, 413);
  assert.equal((await worker.fetch(new Request('https://example.test/api/feedback'), env)).status, 405);
  assert.equal(database.prepare('SELECT count(*) AS count FROM feedback').get()?.count, 1);
  assert.equal((await worker.fetch(request({ ...payload, id: 'd1c2c077-971d-45b6-85e4-9b76517ec5fe', page: '/map' }), env)).status, 201);
  assert.equal((await worker.fetch(request({ ...payload, id: '145d3035-4f38-4629-a52a-7cdbb078d855', page: '/map.html' }), env)).status, 201);
  assert.equal((await worker.fetch(request({ ...payload, id: '7b0f0d5e-2c8a-4f1e-9b3d-4a6c2e1f8d90', page: '/sources' }), env)).status, 201);
  assert.equal((await worker.fetch(request({ ...payload, id: '9e4d1c2b-6a7f-4d3e-8c1b-2f5a6b7c8d91', page: '/sources.html' }), env)).status, 201);
  database.close(); rmSync(dir, { recursive: true });
});
test('database failure returns an error instead of claiming a save', async () => {
  const env = { DB: { prepare() { throw new Error('Unavailable'); } }, ASSETS: { async fetch() { return new Response('asset'); } } };
  assert.equal((await worker.fetch(request(), env)).status, 503);
});
