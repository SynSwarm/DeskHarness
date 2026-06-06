# DeskHarness ⚙️
**The Central Nervous System for Next-Generation AI Applications.**
DeskHarness is a minimalist, headless routing gateway designed to completely decouple your AI's cognitive logic from its peripheral execution and user interfaces. Built for SMEs, solo developers, and high-net-worth business automation, it acts as the absolute single source of truth for protocol translation and state routing.
Stop building monolithic AI bots. Build a resilient, plug-and-play architecture.
## 🎯 The Philosophy: Absolute Decoupling
In the era of disposable LLMs and fragile third-party APIs, your core business data and routing protocols are your only real moats. DeskHarness strictly enforces a 4-layer architecture:
 1. **Skin (I/O & UI):** Telegram bots, Webhooks, social media monitors. (Disposable)
 2. **DeskHarness (The Gateway):** Protocol translation, state management, and strict JSON standardization. (The Core)
 3. **Brain (Cognitive):** LLMs and RAG integrations. Purely stateless reasoning. (Swappable)
 4. **Action (Execution):** RPA scripts, database CRUD, and external API calls. (Mechanical)
DeskHarness sits exactly at Layer 2. It does not "think," and it does not "act." It ensures that your Brain never has to worry about how a Telegram message is formatted, and your RPA scripts never have to parse raw user intent.
## ✨ Core Features
 * **Headless by Design:** 100% UI-agnostic. Bring your own frontend, RPA scripts, or headless clients.
 * **Protocol Standardization:** Washes heterogeneous external inputs (text, voice, system events) into a unified, strict JSON payload.
 * **Stateless Cognitive Routing:** Maintains session pointers and rate-limiting via high-performance KV caching, keeping your LLM logic layer completely stateless and horizontally scalable.
 * **Low-Ops & Lightweight:** Designed specifically for solo enterprises and agile teams. Deployable as a single binary or a lightweight container without bloated enterprise dependencies.
## 🏗️ Architecture Flow
```text
[External Chaos]  -->  (Skin) Custom Bots / Web UI / RPA Monitors
                             |
                      [DeskHarness Gateway] 
           Standardizes Payload | Manages State | Routes Intent
                             |
                        (Brain) LLM / RAG Engine 
                      Returns decision (No direct actions)
                             |
                      [DeskHarness Gateway]
           Dispatches strict commands to execution endpoints
                             |
                      (Action) Database CRUD / Automation Scripts
                             |
                      [Data Assets]

```
## 🚀 Why DeskHarness?
Most frameworks force you into their proprietary "Agent" wrappers. DeskHarness provides the raw infrastructure to build your own. If a platform's API changes tomorrow and your RPA breaks, you only rewrite one isolated script. Your AI logic, prompt engineering, and state management within DeskHarness remain entirely untouched.
## 💼 Enterprise & Commercial Ecosystem
DeskHarness is open-source under the **Apache License 2.0**. It is production-ready for standard deployments.
For teams requiring advanced multi-seat management (e.g., granular RBAC starting from 2 basic seats), high-concurrency private domain automation plugins, or dedicated commercial architecture consulting (FDA/FDE implementations), please refer to our commercial orchestration platform.
