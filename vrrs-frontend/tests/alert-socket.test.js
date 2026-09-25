import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

test("alert socket ignores heartbeats, delivers alerts, and releases its timer", () => {
    const source = readFileSync(new URL("../src/services/api.js", import.meta.url), "utf8");
    // Execute the actual socket factory without the Vite-only import.meta.env or Axios.
    const factory = source.slice(source.indexOf("export const createAlertSocket"), source.indexOf("export default api"))
        .replace("export const createAlertSocket", "globalThis.createAlertSocket");
    const received = [];
    const sent = [];
    let tick;
    let cleared;
    const context = vm.createContext({
        WS_BASE_URL: "ws://test.local",
        localStorage: { getItem: () => "test-token" },
        WebSocket: class {
            readyState = 1;
            send(data) { sent.push(data); }
        },
        setInterval(callback, delay) { assert.equal(delay, 30000); tick = callback; return 42; },
        clearInterval(id) { cleared = id; },
        console: { log() {}, error() {} },
    });
    vm.runInContext(factory, context);
    const socket = context.createAlertSocket((data) => received.push(data));
    socket.onopen();
    tick();
    assert.deepEqual(sent, ["ping"]);
    socket.onmessage({ data: "pong" });
    assert.equal(received.length, 0);
    socket.onmessage({ data: JSON.stringify({ type: "STOLEN_DETECTED", alert_id: 123 }) });
    assert.equal(received.length, 1);
    assert.equal(received[0].alert_id, 123);
    socket.onclose();
    assert.equal(cleared, 42);
});
