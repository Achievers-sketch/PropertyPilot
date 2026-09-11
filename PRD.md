# PropertyPilot AI — Product Requirements Document

## 1. Product

PropertyPilot AI is an AI workflow copilot for real-estate professionals. It helps agents structure client requirements, identify relevant properties from available inventory, explain why properties match, identify missing information and prepare follow-up communication.

## 2. Problem hypothesis

Real-estate agents may receive requirements in unstructured natural language and then manually search, compare, clarify missing information and follow up with clients. PropertyPilot AI tests whether an AI-assisted workflow can make this process faster and more consistent.

This is a hypothesis to validate, not a proven market claim.

## 3. Primary target user

Independent real-estate agents and small/mid-sized agencies in Pakistan.

Secondary users may include property seekers, investors, developers and property managers in later versions.

## 4. MVP objective

Demonstrate an end-to-end workflow from a natural-language client requirement to ranked property matches, match explanations and a ready-to-review follow-up message.

## 5. Functional requirements

### FR1 — Requirement extraction
The system should extract:
- City
- Preferred area
- Property type
- Size
- Maximum budget
- Minimum bedrooms
- Purpose: buy/rent

### FR2 — Property matching
The system should compare extracted requirements with structured property records.

### FR3 — Ranking
The system should calculate a transparent prototype match score.

Current design assumption:
- Budget: 30%
- City/location: 30%
- Property type: 15%
- Size: 15%
- Bedrooms: 10%

These weights are product-design assumptions and require validation.

### FR4 — Explanation
The system should show simple reasons for a match, such as location match, budget fit and bedroom requirement met.

### FR5 — Lead intelligence
The system should identify important missing search information and recommend a next action.

### FR6 — Communication
The system should prepare a client-facing follow-up draft for human review.

## 6. Agent architecture

1. **Requirement Agent** — converts natural language into structured search requirements.
2. **Matching Engine** — deterministic Python filtering and scoring.
3. **Analysis Agent** — explains why the shortlisted properties match.
4. **Lead Agent** — identifies missing information and next actions.
5. **Communication Agent** — prepares a follow-up message.

The architecture intentionally uses an LLM for language tasks and deterministic Python logic for property scoring.

## 7. Non-goals for hackathon MVP

- Live marketplace
- Legal/property ownership verification
- Real-time land registry integration
- Property valuation engine
- Mortgage processing
- Payments or transactions
- Automated property purchase/sale
- Nationwide verified property database
- Automated WhatsApp sending

## 8. Data

The MVP uses synthetic property records for demonstration. No demo property should be represented as a live listing.

## 9. Success metrics to validate later

- Requirement extraction accuracy
- Time saved per property search
- Percentage of agents accepting suggested matches
- Percentage of generated messages requiring edits
- Repeat usage per agent
- Pilot conversion to paid usage

## 10. Validation plan

### Hypothesis
Agents experience repetitive manual work when converting client requirements into property shortlists and follow-up.

### Experiment
Interview and observe 10–20 independent agents and small agencies.

### Metric
Percentage reporting the workflow as frequent and sufficiently painful to justify a solution.

### Threshold
Define the threshold before running interviews; for example, proceed to a pilot only if a clear majority report the problem as frequent and important.

### Decision
- Strong evidence → pilot with agents.
- Mixed evidence → narrow the workflow.
- Weak evidence → reconsider target user/problem.

## 11. Future roadmap

**Version 1:** Agent pilot + inventory upload + matching.

**Version 2:** CRM, lead history and area comparison.

**Version 3:** Verified information and market intelligence integrations.

**Version 4:** Broader real-estate workflow infrastructure.
