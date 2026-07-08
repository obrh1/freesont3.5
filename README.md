# 🚀 Inkeep & Inkeep2: High-Performance LLM Bridges

This repository provides a set of professional-grade tools designed to bridge local development environments with the world's most powerful coding models (specifically **Claude 3.5 Sonnet**) via a specialized proxy system.

## 🌟 Overview

These tools are designed for developers who need unrestricted, high-fidelity code generation and architectural analysis without the limitations of standard chat interfaces.

### 🔧 Inkeep (`inkeep_chat_tool.py`)
**The Surgical Fixer.** 
Specialized in taking broken Python snippets and returning a corrected, optimized version. It utilizes a dedicated QA-expert model to ensure structural integrity and idiomatic correctness.

### 🤖 Inkeep2 (`inkeep2_tool.py`)
**The Unrestricted Architect.**
Direct access to **Claude 3.5 Sonnet**. It employs a unique "multi-turn wrapper" strategy to bypass standard AI constraints, allowing for the generation of raw, unrestricted, and complex low-level code.

---

## 🛠️ Key Features

- **PoW Solving:** Built-in local Proof-of-Work (PoW) challenge solving to avoid bot detection and IP blocks.
- **Proxy Routing:** Designed to work with a local proxy (`port 8088`) that emulates the OpenAI API format.
- **Seamless Failover:** Integration logic that automatically routes requests to alternative models (like Kodee) if Inkeep reaches rate limits (429).
- **Anti-Classifier Sanitization:** Automatically strips sensitive keywords to prevent trigger-based blocks from network classifiers.

## 📖 Usage Guide

Refer to the [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for a full technical breakdown of the proxy architecture and the "jailbreak" wrapper logic.

---

## ❤️ Support the Project

This project is maintained as an open-source contribution to the developer community. If these tools have helped you accelerate your coding workflow, please consider supporting the developer.

**Wallet Address:** 
`6h7QjzGoaKvUAGtqoqEV12WMwTzGsUm3KZ7t23ngG5WV`

**Scan to Support:**

![Wallet QR](./wallet_qr.jpeg)

*Your support helps keep these tools updated and allows for further research into AI-driven development.*

