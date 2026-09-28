# Northstar AI Sales Agent

A conversational AI sales agent I built for a fictional real-estate project, **Northstar One**.

The idea was simple: instead of building another chatbot that only answers questions, I wanted to build something closer to how an actual sales representative would work — understand what the customer wants, remember important details, qualify the lead, and help them book a site visit.

## What it does

- Talks naturally with prospective buyers
- Supports English, Hindi, and Hinglish
- Understands requirements like 2/3 BHK, budget, and purchase purpose
- Remembers information across the conversation
- Identifies high-intent leads
- Handles site-visit bookings
- Handles unavailable booking slots
- Avoids making up information it doesn't know
- Supports human escalation and do-not-contact requests
- Generates structured lead analytics
- Includes a simple web interface

## Example

A conversation can look like this:

> **User:** I'm looking for a 3 BHK.  
> **User:** My budget is around 2 crore.  
> **User:** It's for my own use.  
> **User:** Can I visit on Saturday at 11 AM?

The agent gradually builds the lead profile and can confirm the visit with a booking reference.

Instead of asking the customer to fill out a long form, the information is collected naturally through conversation.

## Handling things the AI doesn't know

One thing I specifically wanted to avoid was the agent confidently making up project information.

For example, if someone asks:

> **"What is the possession date?"**

and that information isn't verified, the agent says it doesn't have confirmed information and offers to get it checked by the team.

## How I built it

The project uses:

- **Python + FastAPI** for the backend
- **LLM via OpenRouter** for conversations
- **Pydantic** for structured lead data
- **HTML/CSS/JavaScript** for the interface
- **Pytest** for testing

I kept important actions like booking confirmation and lead-state updates in application logic rather than leaving everything to the language model.

## Project Structure

```text
northstar-ai-agent/
├── app/
│   ├── agent.py
│   ├── analytics.py
│   ├── extractor.py
│   ├── main.py
│   ├── memory.py
│   ├── models.py
│   ├── prompts.py
│   └── tools.py
├── prompt/
├── static/
├── tests/
├── requirements.txt
└── README.md
