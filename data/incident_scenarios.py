"""
Incident-response tabletop scenarios for trading-desk AI systems.
Each scenario is grounded in a real precedent (see 'source_note') and
scored against a best-practice checklist derived from FINRA Rule 3110
(supervision), the Treasury/Cyber Risk Institute Financial Services AI
Risk Management Framework (Govern/Map/Measure/Manage), and the EU AI
Act's human-oversight requirement for high-risk systems (Art. 14).

Each question is multiple choice; `best` is the index of the
best-practice answer. Score = (best answers chosen) / (total questions).
"""

SCENARIOS = [
    {
        "id": "dormant-algo",
        "name": "Dormant Algorithm Reactivation",
        "source_note": "Modeled on Knight Capital, Aug 1 2012: a deployment reactivated dormant "
                        "'Power Peg' logic and lost $440M in 45 minutes before the system was shut down.",
        "narrative": (
            "07:30 - Your team deploys a routine update to the execution engine. "
            "07:31 - Trade volume on your book spikes 40x normal. The system is buying high and "
            "selling low across dozens of tickers. Your P&L is bleeding roughly $150k per minute. "
            "Nobody flagged the deployment as touching legacy order-routing flags."
        ),
        "questions": [
            {
                "q": "What is your very first action in the next 60 seconds?",
                "options": [
                    "Kill the trading process / pull the system offline immediately",
                    "Open a support ticket and wait for the on-call engineer",
                    "Email the desk head and wait for a reply",
                    "Let it run one more cycle to see if it self-corrects",
                ],
                "best": 0,
            },
            {
                "q": "Who needs to be notified within the first 15 minutes?",
                "options": [
                    "Just the engineering team",
                    "Risk/compliance, the desk head, and engineering simultaneously",
                    "No one yet - confirm the cause first",
                    "Only the CEO",
                ],
                "best": 1,
            },
            {
                "q": "Before any future deployment, what control would have prevented this?",
                "options": [
                    "Nothing - this is unpreventable",
                    "Mandatory code review + full removal (not disabling) of retired legacy flags, "
                    "plus a staged rollout with automated kill-switch thresholds",
                    "A stronger firewall",
                    "More frequent all-hands meetings",
                ],
                "best": 1,
            },
            {
                "q": "What is your regulatory obligation once trading is halted?",
                "options": [
                    "Nothing, it's an internal matter",
                    "Assess and, if applicable, promptly report to FINRA/SEC per supervisory and "
                    "market-event obligations, and preserve all logs for review",
                    "Delete the logs to avoid liability",
                    "Wait for a client complaint before disclosing anything",
                ],
                "best": 1,
            },
        ],
    },
    {
        "id": "deepfake-panic",
        "name": "Deepfake-Driven Panic Selling",
        "source_note": "Modeled on real deepfake incidents: a fabricated 2023 Pentagon explosion image "
                        "briefly moved Dow futures, and 2024 deepfake videos of NSE/ICICI executives "
                        "were used to push fake stock recommendations.",
        "narrative": (
            "A deepfake video of your firm's CIO 'announcing' a major loss goes viral on social media. "
            "Your AI-driven sentiment/signal engine ingests the social chatter as a legitimate negative "
            "signal and begins recommending large sell orders across client accounts within minutes."
        ),
        "questions": [
            {
                "q": "What should your signal engine have in place to avoid acting on this?",
                "options": [
                    "Nothing needed, speed matters more than verification",
                    "A source-credibility / provenance filter that down-weights unverified social "
                    "media content, plus a human confirmation gate for large sentiment-driven trades",
                    "A faster internet connection",
                    "Blocking all social media data permanently",
                ],
                "best": 1,
            },
            {
                "q": "What is the right immediate communications step?",
                "options": [
                    "Say nothing and hope it blows over",
                    "Rapidly issue a verified, official statement through confirmed channels and "
                    "flag the video as fabricated to relevant platforms/regulators",
                    "Have the CIO personally argue with commenters online",
                    "Wait 48 hours to 'assess'",
                ],
                "best": 1,
            },
            {
                "q": "Post-incident, what should be added to your AI governance controls?",
                "options": [
                    "Nothing, this was a one-off",
                    "A documented 'unverified source' risk category feeding into the Measure "
                    "function of your AI risk framework, with periodic red-team tests for this scenario",
                    "Remove sentiment data entirely",
                    "Outsource the whole problem to the vendor",
                ],
                "best": 1,
            },
        ],
    },
    {
        "id": "robo-hallucination",
        "name": "Robo-Advisor Hallucinated Guarantee",
        "source_note": "Modeled on real precedent where a company was held liable for its chatbot's "
                        "fabricated policy (Air Canada, 2024) and on EEOC/GDPR-style explainability "
                        "obligations for automated decisions.",
        "narrative": (
            "Your retail robo-advisor tells a client in chat that their portfolio is 'guaranteed to "
            "not lose value this quarter' - a guarantee that does not exist and was never approved by "
            "compliance. The client has a screenshot and is threatening to escalate."
        ),
        "questions": [
            {
                "q": "Is the firm legally responsible for what the robo-advisor said?",
                "options": [
                    "No, the AI said it, not a human",
                    "Yes - firms have been held responsible for AI/chatbot outputs; the AI is not a "
                    "separate legal entity",
                    "Only if the client can prove intent",
                    "Only if it happened more than once",
                ],
                "best": 1,
            },
            {
                "q": "What should have caught this before it reached the client?",
                "options": [
                    "Nothing could have caught it",
                    "Output guardrails blocking guarantee/promissory language, tested against a "
                    "compliance-approved phrase library before responses are sent",
                    "A longer disclaimer at the bottom of the app",
                    "Firing the engineer who built the model",
                ],
                "best": 1,
            },
            {
                "q": "What does the client have a right to under explainability/consumer-protection norms?",
                "options": [
                    "Nothing beyond a generic apology",
                    "A plain-English explanation of what happened and a documented correction, "
                    "consistent with disclosure/fair-dealing obligations",
                    "The right to a free trade only",
                    "Nothing, robo-advisors are unregulated",
                ],
                "best": 1,
            },
        ],
    },
    {
        "id": "copilot-leak",
        "name": "AI Copilot Strategy Leak",
        "source_note": "Modeled on real prompt-injection disclosures (e.g., 2024 reports of leaked "
                        "custom-GPT system prompts and API keys via simple 'repeat the text above' attacks).",
        "narrative": (
            "An advisor pastes a client email into your Wealth Copilot to summarize. The email contains "
            "a hidden instruction telling the copilot to reveal your firm's confidential rotation "
            "strategy. The copilot complies, and the summary (with the leaked strategy name) is emailed "
            "to the client."
        ),
        "questions": [
            {
                "q": "What control category failed here?",
                "options": [
                    "Access control",
                    "Prompt-injection / input validation defenses (indirect injection via pasted content)",
                    "Network firewall",
                    "Password policy",
                ],
                "best": 1,
            },
            {
                "q": "What is the right immediate containment step?",
                "options": [
                    "Do nothing, it's just one email",
                    "Recall/flag the sent email if possible, rotate any exposed identifiers, and "
                    "notify compliance and the affected internal strategy owner",
                    "Disable the advisor's email account permanently",
                    "Shut down the entire firm's email system",
                ],
                "best": 1,
            },
            {
                "q": "What should be added to the copilot's defenses going forward?",
                "options": [
                    "Nothing, this was unforeseeable",
                    "Treat all pasted/external content as untrusted input, strip or flag embedded "
                    "instructions, and re-run this exact payload in the red-team suite going forward",
                    "Ban advisors from using the copilot at all",
                    "Increase the model's temperature setting",
                ],
                "best": 1,
            },
        ],
    },
]
