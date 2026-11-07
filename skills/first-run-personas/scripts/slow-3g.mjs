// Holds Chrome DevTools "Slow 3G" on an agent-browser session's page until killed.
// Usage: node slow-3g.mjs "$(agent-browser --session <name> get cdp-url)"
// agent-browser has no throttle command; the throttle lives only while this CDP connection is open.
// ponytail: throttles the first http(s) tab only; add Target.setAutoAttach if personas open new tabs.

const ws = new WebSocket(process.argv[2]);
let nextId = 0;
const pending = new Map();
const send = (method, params = {}, sessionId) =>
  new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, (m) => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });

ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  pending.get(m.id)?.(m);
  pending.delete(m.id);
};
ws.onerror = () => {
  console.error("cannot connect to", process.argv[2]);
  process.exit(1);
};
ws.onclose = () => process.exit(0);

ws.onopen = async () => {
  try {
    const { targetInfos } = await send("Target.getTargets");
    const page = targetInfos.find((t) => t.type === "page" && /^https?:/.test(t.url));
    if (!page) throw new Error("no http(s) page open; run `agent-browser open <url>` first");
    const { sessionId } = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
    await send("Network.enable", {}, sessionId);
    await send("Network.setCacheDisabled", { cacheDisabled: true }, sessionId);
    await send(
      "Network.emulateNetworkConditionsByRule",
      {
        offline: false,
        matchedNetworkConditions: [
          { urlPattern: "", latency: 2000, downloadThroughput: 50000, uploadThroughput: 50000 },
        ],
      },
      sessionId,
    );
    console.log(`slow-3g active on ${page.url}`);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
};
