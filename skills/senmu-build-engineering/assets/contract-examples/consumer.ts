// Types come from the selected example's generated contract, never a second field list.
import type { paths } from "./generated/api.js";
type CreateBody = paths["/items"]["post"]["requestBody"]["content"]["application/json"];
type Item = paths["/items"]["post"]["responses"][201]["content"]["application/json"];
declare const process: { argv: string[]; exitCode: number };

type Exchange = { method: string; url: string; requestBody?: unknown;
  status: number; headers: Record<string, string>; body: unknown };
const events: Exchange[] = [];

async function call(method: string, url: string, body?: CreateBody) {
  const response = await fetch(url, { method, headers: { "Content-Type": "application/json" },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
  const actual: unknown = await response.json();
  events.push({ method, url, requestBody: body, status: response.status,
    headers: Object.fromEntries(response.headers.entries()), body: actual });
  return actual;
}

async function main() {
  const base = process.argv[2];
  if (!/^http:\/\/127\.0\.0\.1:\d+$/.test(base)) throw new Error("loopback target required");
  const request: CreateBody = { name: "sample", note: null };
  // Static annotation is NOT a network validator: check.py validates this actual exchange.
  const created = await call("POST", base + "/items", request) as Item;
  const id: string = created.id;
  await call("GET", base + "/items/" + encodeURIComponent(id));
  await call("POST", base + "/items", { name: "", note: null });
  await call("GET", base + "/items/missing");
  console.log(JSON.stringify({ events }));
}
main().catch(error => { console.error(String(error)); process.exitCode = 1; });
