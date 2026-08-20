# SupplyNode

> **Autonomous Inventory Intelligence & Adaptive Decision Layer for SMEs**

SupplyNode is an agentic AI intelligence layer designed to sit on top of existing business records (Zoho Books, Tally, Odoo, ERPNext, or flat spreadsheets). While traditional ERP systems act as passive data layers recording historical transactions, SupplyNode acts as an autonomous supply chain analyst—continuously monitoring data, identifying critical inventory risks, making deterministic decisions, and adapting over time via structured feedback loops.

---

## 📌 Architecture Overview

```text
[ Data Layer: Zoho / Tally / ERPNext / CSV ]
                     │
                     ▼
       [ Data Ingestion Engine ]
                     │
                     ▼
           [ KPI Compute Engine ]
   (Days of Supply, Poisson Risk, EOQ, ITR)
                     │
                     ▼
         [ Specialized Risk Engines ]
   (Stockout, Dead Stock, Reorder Optimization)
                     │
                     ▼
     [ Agentic AI Orchestrator (LangGraph) ]
                     │
                     ▼
       [ Actionable Alert Dispatcher ]
        (Terminal / JSON / WhatsApp)
                     │
                     ▼
     [ Adaptive Self-Learning Loop ]
 (Override Feedback • Seasonality • Dynamic Supplier Scoring)