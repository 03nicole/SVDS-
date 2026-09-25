# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the concepts behind the real-time and integration component: how servers push data to browsers, how video is streamed to a web page, how services are monitored, and how separate programs are integrated. It then reviews existing approaches and identifies the gap.

## 2.2 Key Concepts and Theories

### 2.2.1 Getting data from server to browser

HTTP is request and response: the server can only answer when the browser asks. Three techniques let a server tell a browser about something new:

- **Polling:** the browser asks repeatedly ("anything new?"). Simple, but wasteful and always late by up to one polling interval.
- **Server-Sent Events:** a one-way stream from server to browser over HTTP.
- **WebSocket (RFC 6455):** a single long-lived, two-way connection, started with an HTTP request that is "upgraded". Messages flow either way with little overhead, which suits pushing an alert the instant it exists.

### 2.2.2 WebSocket authentication

A browser's `WebSocket` object cannot set an `Authorization` header. Common workarounds are to put a token in the URL query string, to send it as the first message, or to use a cookie. A token in a URL is easy to implement but is likely to be written to server logs and history, and it is only checked once, when the connection is opened.

### 2.2.3 The publish-to-connected-clients pattern

A server keeps a list of open connections and, when an event occurs, writes the message to each. This is simple and needs no message broker, but the list lives in one process's memory. If the server runs as several processes, each has its own list, so an event handled by one process reaches only its own clients. A shared broker (for example Redis publish/subscribe) removes that limit.

### 2.2.4 Streaming video to a browser: MJPEG

**Motion JPEG (MJPEG)** sends a video as a continuous series of JPEG images in one HTTP response with the content type `multipart/x-mixed-replace`. Browsers can show it in an ordinary `<img>` tag, which is why phone "IP camera" apps use it. It is easy but uses more bandwidth than modern codecs. Because an `<img>` tag cannot send custom headers, protecting such a stream also needs a query-string token or a cookie.

### 2.2.5 A proxy in front of a device

A reverse proxy relays a request to another server and returns its answer. Putting the server in front of the camera means the browser never learns the camera's address, and the server can check who is asking before relaying. The costs are extra load on the server and the need to close the upstream connection when the viewer leaves.

### 2.2.6 Health monitoring

A health endpoint reports whether a service and its dependencies are working. Good practice is that each reported value is *measured*, not asserted, and that the endpoint is not open to the public, because it reveals internal details. Distinguishing "liveness" (the process is up) from "readiness" (its dependencies work) is common practice in operations.

### 2.2.7 Integration by contract

Separately deployed programs integrate by agreeing on interfaces: URLs, message shapes, ports and configuration keys. Documenting the contract, and keeping configuration in one place, reduces the chance that a change in one program silently breaks another.

## 2.3 Existing Systems / Related Work

- **Polling dashboards** are the simplest approach and remain common in small systems; they trade latency for simplicity.
- **Socket.IO and similar libraries** add automatic reconnection, heartbeats and fall-backs on top of WebSockets. This project uses the browser's raw WebSocket and Starlette's WebSocket support, so it has to supply these itself.
- **Message brokers (Redis, RabbitMQ, Kafka)** are the standard answer to multi-process fan-out; not used here.
- **Video platforms and surveillance systems** use RTSP, WebRTC or HLS instead of MJPEG for efficiency; MJPEG was chosen because the phone app provides it directly.
- **Monitoring tools (Prometheus, Grafana, health-check libraries)** measure service state properly; this project has a small hand-written health endpoint instead.

*Note on sources.* This chapter relies on standards and public documentation listed in the References. No performance figures from other systems are quoted.

## 2.4 Comparative Analysis

| Criterion | This project | Polling | Socket.IO + broker |
|---|---|---|---|
| Delivery model | Push over WebSocket | Pull | Push |
| Automatic reconnection | Not implemented | Not needed | Built in |
| Works across several server processes | No | Yes | Yes |
| Setup effort | Low | Lowest | Higher |
| Delay to the officer | Depends on delivery only | Up to one polling interval | Depends on delivery only |

The table compares design properties, not measured performance.

## 2.5 Research / Knowledge Gap

Tutorials show how to broadcast to WebSocket clients but seldom show what happens when a client is deactivated, a connection drops, or a slow client is present. The gap this report addresses is a working alert channel for a police setting together with a **tested account of its failure modes**.

## 2.6 Conceptual Framework

```
camera node --HTTP--> backend --match--> ConnectionManager --WebSocket--> browsers (police, admin)
                          |                                                    ^
                          +------------ authenticated MJPEG proxy -------------+ (camera feed)
                          +------------ /system/health, /system/camera-nodes ---+ (status)
```

Detection is pushed; status is pulled; the camera feed is relayed. Each channel is authenticated with the same token as the rest of the API, except where noted in Chapter 6.

## 2.7 Chapter Summary

WebSockets are the right tool for pushing alerts. The simple in-memory design used here is adequate for one server process and leaves reconnection, multi-process delivery and continuous token checks to be added. MJPEG proxying and a hand-written health endpoint are workable for a prototype but need care.
