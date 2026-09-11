# PropertyPilot AI 🏠

**AI-powered real-estate workflow copilot for Pakistan.**

PropertyPilot AI is a hackathon MVP that helps real-estate professionals turn natural-language client requirements into structured requirements, ranked property matches, explanations, missing-information prompts and follow-up messages.

## MVP workflow

Client requirement → Requirement Agent → Matching Engine → Analysis Agent → Lead Agent → Communication Agent

## Features

- Natural-language property requirement input
- Groq-powered requirement extraction when `GROQ_API_KEY` is available
- Deterministic property matching and ranking
- Match explanations
- Missing-information prompts
- Client follow-up message generation
- Streamlit interface
- Synthetic property dataset for demonstration

## Tech stack

- Python
- Streamlit
- Groq API
- Pandas
- CSV

Groq's official documentation recommends storing the API key as an environment variable rather than hard-coding it in application code. The app therefore reads `GROQ_API_KEY` from the environment.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For AI extraction, set the environment variable before running:

```bash
export GROQ_API_KEY="your-key"
```

On Windows PowerShell:

```powershell
$env:GROQ_API_KEY="your-key"
```

If no key is available, the application uses a lightweight demo parser so the prototype can still run.

## Important demo limitation

The included properties are **synthetic demo records**. They are not live property listings and must not be presented as real market inventory.

Match weights are prototype design assumptions, not professional valuation standards.

## Security

Never commit API keys, passwords or other secrets to GitHub. Use environment variables locally and platform secrets for deployment.

## Hackathon positioning

PropertyPilot AI is positioned as a workflow layer for real-estate professionals rather than another property marketplace. The hypothesis is that AI can reduce repetitive work involved in structuring client requirements, matching available inventory, explaining matches and preparing follow-up communication.
