# Enterprise MCP & LangGraph AI Runtime

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Orchestration](https://img.shields.io/badge/Orchestrator-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Protocol](https://img.shields.io/badge/Tooling-Model_Context_Protocol_(MCP)-purple.svg)](https://modelcontextprotocol.io/)
[![Evals](https://img.shields.io/badge/Testing-DeepEval_%2F_Pytest-green.svg)](https://github.com/confident-ai/deepeval)

An enterprise-grade production runtime bridging transactional systems (Dataverse, CRM, Relational DBs) with LLM agents using **Model Context Protocol (MCP)**, **LangGraph deterministic state machines**, and **automated continuous evaluation harnesses**.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph ClientLayer [Client & Security Perimeter]
        User[Client App / Webhook / UI] --> Gateway[API Gateway: OAuth2 + RBAC]
    end

    subgraph Runtime [LangGraph Deterministic Orchestration Runtime]
        Gateway --> GuardNode[1. Input Guardrail: PII & Injection Filter]
        GuardNode --> Router[2. Semantic Intent Router Node]
        Router --> Planner[3. State Evaluation & Plan Node]
        Planner --> ToolCall[4. MCP Tool Execution Node]
        ToolCall --> EvalGate{5. Confidence & Schema Check}
        EvalGate -- Passed --> ResponseFormatter[6. Response Formatter Node]
        EvalGate -- Failed / Hallucination Detected --> FallbackNode[Deterministic Fallback Handler]
    end

    subgraph DataPlane [Context & Enterprise Integration Layer]
        ToolCall <-->|Model Context Protocol - JSON-RPC| MCPServer[Enterprise MCP Server]
        MCPServer <-->|Dataverse / CRM API| CRM[(Transactional CRM / Dataverse)]
        MCPServer <-->|Vector + BM25 Hybrid| KnowledgeBase[(Enterprise Vector Store)]
    end

    subgraph Observability [Observability & Regression Pipeline]
        Runtime -.-> Tracing[OpenTelemetry / LangSmith Traces]
        CI[GitHub Actions CI/CD] --> EvalHarness[DeepEval Regression Harness]
        EvalHarness --> GoldenSet[(Golden Dataset: Hallucination & RBAC Checks)]
    end
