# The Chameleon 🦎
**An Infinite-Interaction AI Honeypot & Threat Analyzer**

Traditional honeypots use static file systems. Hackers and botnets detect them in seconds, disconnect, and leave before you can gather any meaningful threat intelligence. 

**The Chameleon** solves the "Attacker Dwell Time" problem. Instead of hardcoded rules, it routes an attacker's SSH inputs through a Generative AI model specifically prompted to act as an Ubuntu 22.04 terminal. If the attacker creates a file, the AI remembers it. If they try to read a sensitive database, the AI hallucinates fake data on the fly.

While the attacker is trapped in this infinite, realistic loop, a secondary AI "Glass Box" model analyzes their commands in real-time to build a behavioral threat profile.

## Key Features
* **Generative File System:** No static files. Every directory, error message, and file content is generated dynamically based on attacker context.
* **Infinite State Memory:** Maintains session state so attackers can navigate directories and edit files consistently.
* **Real-Time SOC Analysis:** Analyzes attacker intent (Malicious, Suspicious, Safe) in the background without alerting the intruder.
* **Custom SSH Listener:** Uses Paramiko to bind to Port 22 and route traffic directly to the AI engine.

## The Architecture
1. **The Trap:** A Python socket/Paramiko server listening on Port 22 accepts any credentials.
2. **The Brain:** Google's Gemini API hallucinating the raw Ubuntu environment.
3. **The Analyst:** A secondary AI prompt analyzing the raw inputs and logging intent to a background dashboard.

## Authors
* Shlok & Sidh

graph TD
    A([Attacker]) -->|SSH Port 22| B{Paramiko Listener}
    
    %% The Terminal Loop
    B -->|Command Input| C[Terminal AI Engine]
    C -->|Fake Ubuntu Output| A
    
    %% The Analyst Branch
    B -->|Background Logging| D[Analyst AI Engine]
    D -->|Intent Verdict| E[(Glass Box Dashboard)]
    
    classDef hacker fill:#ff4d4d,stroke:#333,stroke-width:2px,color:#fff;
    class A hacker;
