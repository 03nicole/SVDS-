# Chapter 7: Discussion

## 7.1 Introduction

This chapter interprets the results of Chapter 6, compares them with related practice, states the contributions, and discusses limitations.

## 7.2 Interpretation of Findings

**Research question 1** (can a plain WebSocket channel, authenticated with the same token as the rest of the API, deliver detections to all connected officers with no polling?). Yes, in the conditions tested. A match produced a message to every connected police and admin client, unauthorised connections were refused, and a dead connection did not block delivery. The token is reused as designed; the price is that it is checked only once.

**Research question 2** (can three processes be integrated using only network contracts?). Yes. The camera node, backend and browser share URLs, message shapes and configuration keys, and none imports another's code. The cost of this loose coupling is visible in R-13: configuration that must agree in several places, with nothing checking that it does.

**Research question 3** (what breaks?). The weaknesses fall into three groups:

1. **Lifetime problems** (R-2, R-3, R-8, R-9): the design treats a connection as permanent and a token as permanently valid. Both assumptions fail in real use, and the most damaging consequence is silent: an officer whose connection dropped sees nothing wrong and receives nothing.
2. **Honesty of the monitoring** (R-1, R-4, R-5, R-14): the health and status pages show some values that are measured and others that are constants or mislabelled, and the endpoint is public.
3. **Scaling and resource use** (R-6, R-11, R-12): the design is right for one server process, one camera and a few viewers, and unmeasured beyond that.

**The alert channel is not the slow part.** The 17 ms in-process figure only shows that broadcasting adds almost no delay. The time an officer waits is dominated by earlier steps: the camera node samples every fifth frame, runs detection and OCR, and is suppressed by a 15-second duplicate window. Improving the alert channel would not speed up a detection much; making it reliable (reconnection, re-checking the user) would matter more.

## 7.3 Comparison with Existing Work

No numeric comparison was made. Against the approaches in Chapter 2, this component gives push delivery without a broker, and lacks what libraries and brokers provide: automatic reconnection and heartbeats (Socket.IO-style libraries) and fan-out across processes (a broker). The lack of reconnection is the difference that would matter most to an officer. Against monitoring tools, the health page provides a small, readable summary but not measured, authenticated or historical monitoring.

## 7.4 Contributions of the Project

- **Practical:** a working push channel from detection to police screens on any page, an authenticated camera feed and a status page, and a single-command start-up.
- **Technical:** an alert channel reusing the REST token; per-connection error isolation in broadcast; a way to test the WebSocket route and the feed proxy without a phone, using a local stand-in camera.
- **Analytical:** a documented list of failure modes, separated into those demonstrated in tests and those found only by reading code.

## 7.5 Limitations and Implications

| Limitation | Implication |
|---|---|
| Everything ran in one process | Timing and connection behaviour on real networks are unknown |
| Front-end findings are from reading | R-8 to R-10 may behave differently in a browser (for example browsers may retry in some conditions), and should be confirmed by running the page |
| Stand-in camera, not the phone | Real MJPEG behaviour (frame sizes, stalls, disconnects) was not tested |
| No live `STOLEN` alert recorded | The whole path from a real vehicle to a real screen has not been observed |
| Severity ratings are the student's own | Not a formal scale |
| Findings not fixed | The delivered system still has them |
| Probes written by the author | They test the failure modes the author thought of |

## 7.6 Chapter Summary

The alert channel works and is simple. Its limits are about time and scale: what happens when a connection or a token outlives the conditions it was created in, and what happens beyond one process. Those limits, and the parts of the monitoring that are constants, are documented so they can be fixed.
