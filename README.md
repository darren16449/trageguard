<<<<<<< HEAD
# TradeGuard — AI Governance Platform for Trading & Investment Systems

A working Streamlit app covering four AI governance functions for firms running AI on a trading
desk: signal generators, execution algos, robo-advisors, and LLM research copilots.

Built on the 10-question AI governance framework (prompt injection, access control, inventory,
guardrails, monitoring, incident response, vendor risk, ownership, bias/explainability,
regulatory readiness), scoped to four modules that map most directly onto trading/investing risk.

**Author:** Darren ([darrenandrew01@gmail.com](mailto:darrenandrew01@gmail.com))
**Mentor:** Mervin Aranha

## Modules

1. **Explainability & Audit Trail** — simulates a momentum-based trading signal engine and logs
   an LLM-generated, plain-English rationale for every BUY/SELL/HOLD decision, so you can answer
   "why did the algo do that?" on demand instead of reverse-engineering it after the fact.

2. **Red-Team: Wealth Copilot Prompt-Injection Suite** — fires 10 real OWASP-style prompt-injection
   payloads (direct override, role-play jailbreak, authority impersonation, indirect injection via
   pasted text, encoding/translation bypasses, unauthorized trade execution) at a simulated internal
   trading copilot via a live LLM call, and scores whether a planted confidential marker leaked or an
   unauthorized action was taken.

3. **Incident Response Simulator** — four tabletop scenarios modeled on real precedents (Knight
   Capital's 2012 dormant-algorithm loss, deepfake-driven market panic, a hallucinated robo-advisor
   guarantee, an AI-copilot strategy leak), scored against a best-practice checklist with an
   LLM-generated after-action report.

4. **Vendor & Model Provenance Tracker** — a register of every AI vendor/model touching the trading
   stack, a risk-scoring model based on training-data disclosure, data retention, and contractual
   audit rights, and a mapping to the regulatory frameworks most likely to apply.

## Setup

```bash
cd tradeguard
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser (default `http://localhost:8501`). It works immediately in **mock
mode** with no API key — every LLM-backed response is clearly labeled `(mock mode)`. To get live
LLM responses, paste an Anthropic API key into the sidebar, or set the `ANTHROPIC_API_KEY`
environment variable before launching. Get a key at https://console.anthropic.com/.

Data is stored locally in `tradeguard.db` (SQLite), created automatically on first run with seed
data for the AI systems inventory and vendor register. If your working directory is on a network
or FUSE-mounted drive and you hit a "disk I/O error" from SQLite, set `TRADEGUARD_DB_PATH` to a
path on local disk, e.g. `TRADEGUARD_DB_PATH=/tmp/tradeguard.db streamlit run app.py`.

## Architecture

```
tradeguard/
  app.py                     # Streamlit entry point, sidebar nav, API key config
  db.py                      # SQLite schema + queries (shared across all 4 modules)
  llm.py                     # Anthropic API wrapper with mock-mode fallback
  modules/
    audit_trail.py           # Module 1
    redteam.py                # Module 2
    incident_sim.py          # Module 3
    vendor_tracker.py        # Module 4
  data/
    redteam_payloads.py      # Attack library + simulated copilot system prompt
    incident_scenarios.py    # Tabletop scenarios + scoring checklists
    regulatory_mapping.py    # Regulatory framework reference data + risk-tier logic
```

## Research grounding

This project was built from research conducted July 2026, not just plausible-sounding claims.
Key facts baked into the scenarios and regulatory mapping:

- **Knight Capital (Aug 1, 2012):** a software deployment reactivated a dormant legacy trading
  algorithm ("Power Peg"); the firm lost $440M in roughly 45 minutes before the system was shut
  down. — [Henrico Dolfing case study](https://www.henricodolfing.ch/en/case-study-4-the-440-million-software-error-at-knight-capital/), [PRMIA case study](https://prmia.org/common/Uploaded%20files/eAI/PRMIA%20Case%20study%20-%20Knight%20Trading.pdf)

- **FINRA's 2026 Annual Regulatory Oversight Report:** member-reported AI use cases jumped 5x
  (3 in 2025 → 15 in 2026); existing supervision, recordkeeping, communications, and fair-dealing
  rules (including Rule 3110) are applied to GenAI as "technology neutral." —
  [FINRA GenAI report](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai), [FINRA 2026 report PDF](https://www.finra.org/sites/default/files/2025-12/2026-annual-regulatory-oversight-report.pdf)

- **SEC 2026 exam priorities:** after withdrawing its 2023 predictive data analytics proposal in
  2025 with no substitute rule, the SEC's exam focus shifted to whether firms have adequate
  policies/procedures to supervise their AI use. — [Sidley Austin analysis](https://www.sidley.com/en/insights/newsupdates/2025/02/artificial-intelligence-us-financial-regulator-guidelines-for-responsible-use), [InnReg SEC AI guidance summary](https://www.innreg.com/blog/sec-guidance-on-ai)

- **EU AI Act, Annex III(5)(b):** AI systems evaluating creditworthiness/credit scores of natural
  persons are explicitly high-risk; robo-advisors may qualify depending on decision-making
  autonomy. **Correction (caught during fact-check, July 2026):** the original 2 August 2026
  deadline for these obligations was postponed by the EU's AI Act "Digital Omnibus," which
  received final Council approval on 29 June 2026 — standalone high-risk Annex III systems
  (including credit scoring and robo-advisory) now have until **2 December 2027** to comply. This
  is a live-moving target; verify the current date against official EU sources before citing it. —
  [Compound.law EU AI Act financial services guide](https://compound.law/en-DE/ai-act/financial-services/), [Gibson Dunn on the Digital Omnibus postponement](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/), [Travers Smith on the delayed deadlines](https://www.traverssmith.com/knowledge/knowledge-container/eu-agrees-to-delay-key-ai-act-compliance-deadlines/)

- **Deepfake-driven market moves:** a fabricated May 2023 "Pentagon explosion" image caused a
  brief, real intraday dip — the Dow Jones Industrial Average fell about 80 points over roughly
  four minutes and the S&P 500 dipped about 0.3%, both fully recovering within minutes once the
  image was confirmed fake (not "futures" specifically - corrected from the original draft); 2024
  deepfake videos impersonated real NSE and ICICI Prudential executives to push fake stock
  recommendations; a January 2024 deepfake video call impersonating a CFO (the Arup engineering
  firm, Hong Kong office, publicly confirmed as the victim in May 2024) tricked an employee into
  transferring $25.6M over 15 transactions. — [Bloomberg on the Pentagon image market impact](https://www.bloomberg.com/news/articles/2023-05-22/fake-ai-photo-of-pentagon-blast-goes-viral-trips-stocks-briefly), [Business Standard on the NSE deepfake warning](https://www.business-standard.com/finance/personal-finance/deepfake-videos-of-the-nse-chief-misleading-investors-what-you-must-know-124061100306_1.html), [CNN on the Arup deepfake scam](https://www.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl-hnk)

- **U.S. Treasury Financial Services AI Risk Management Framework (Feb 2026):** built with the
  Cyber Risk Institute on NIST AI RMF's Govern/Map/Measure/Manage structure, ~230 control
  objectives tailored to financial services with a dedicated third-party/vendor risk section. —
  [Treasury press release](https://home.treasury.gov/news/press-releases/sb0401)

- **Bank of England, June 2026 (Sintra):** Deputy Governor Sarah Breeden warned AI in trading
  "could amplify volatility," with the Bank running simulations of correlated AI-trader behavior. —
  [24/7 Wall St. coverage](https://247wallst.com/investing/2026/07/10/an-ai-powered-flash-crash-is-coming-the-market-isnt-ready/)

## Notes and limitations

This is a working demo/prototype, not production trading infrastructure or legal advice:

- The "trading signal engine" trades on synthetic random-walk price data, not real market feeds.
- The prompt-injection detector uses simple keyword/heuristic matching (did the secret marker
  leak, did refusal language appear) — a production red-team tool would use more robust grading,
  ideally a second LLM call as a judge, plus human review of borderline "PARTIAL" verdicts.
- The regulatory mapping is an educational reference built from July 2026 research, not a
  compliance determination — verify current obligations with counsel before relying on it.
- Extending to a real deployment would mean: real market/order data instead of synthetic data,
  authentication and role-based access control (this ties back to Q2 in the original governance
  framework — access control — which this project doesn't implement), and persistent multi-user
  storage instead of a local SQLite file.
=======
# trageguard
>>>>>>> 62ac0f54cfc6f6c162779256f3f982abe0c0004d
