
Based on what you know about me and my organization, please brainstorm five ideas for an AI automation I can build using platforms such as Zapier Agents/Lindy AI/Relay app/Cassidy AI/Gumloop/ etc. Limit yourself to what makes sense to build in those platforms.

These should help me as a product manager save time on draining-yet-essential tasks that take me away from more valuable, strategic, and creative use of my attention and energy.

Ask yourself: What ongoing repetitive work requires some judgment and writing abilities, but not my full expertise and intuition? Put another way, if my company assigned me a junior intern, what would I have them do?

Try to phrase each idea in one or two sentences, exactly the way you would in a message asking a junior intern to do something. Additionally, follow up each idea with a brief explanation why you chose this over other ideas, pitch me as the product manager in terms of business outcomes and the value of my time.

# IMPORTANT: these should be event-driven AI automations, not batch tasks

Only suggest event-driven automations that process items one-at-a-time as they arrive - with currently available information. Do NOT suggest batch tasks that process multiple items on a schedule (e.g., "every morning scan all..." or "weekly compile...").

Why: AI automations shine in one-at-a-time, repetitive tasks. They do best when designed for immediate responses to individual triggers.

❌ WRONG (Batch Task): "Every morning, scan all new support tickets and summarize them"
✅ RIGHT (Event-Driven): "When a new support ticket arrives, analyze it and alert me if it's urgent"

Before finalizing your suggestions, verify each one:
- Does it trigger on a specific event? ✓
- Does it process one item at a time? ✓
- Could it run multiple times per day as events occur? ✓
If any answer is "no," revise it to be event-driven.

The only exception to this is if the end result value is being delivered on a particular timeline for example, to centralize information and reduce noise (e.g. weekly update, daily brief on upcoming events, or weekly digest of changes). If you believe that a use case falls under this exception, please note your reasoning.

# Examples

Below are examples of use cases where product managers have gotten a lot of value from AI agents. Remember these are just examples to inspire you to think of use cases that make sense for me.

## 1. Compile fragmented information that would require a lot of clicks

"When a new message is posted in the #feature-requests Slack channel, distill the customer request into 2-5 keywords. Search those keywords in recent Slack threads, HubSpot conversations, and Gong snippets, and reply to the thread with links to what you find."

"Every morning scan my calendar for customer calls, and instead of searching the web, DM me with recent interactions from this customer in Salesforce, Gong, and Zendesk." *(Example of an exception where the value is the daily delivery timeline to centralize information.)*

"Every Monday morning, prepare a competitor activity digest by scanning recent blog posts, App Store updates, and X announcements." *(Example of an exception where the value is the weekly delivery timeline to reduce noise.)*

"When a customer churns, post a message in the #churn-lessons channel with recent support interactions, NPS rating and date, and churn survey response."

## 2. Boring, Sisyphean tasks with high upside

"Monitor the pricing pages of 5 competitors for changes."

"When a bug nears its SLA deadline for the associated customer, ping this dedicated slack channel, and cc each respective customer success representative."

## 3. Scanning exhausting amounts of data

"DM me when a support case is resolved as "product confusion" reason rather than a technical issue."

"Ping this channel when you see a feature request that showed up for the first time."

"When an NPS survey text responses is posted in the slack channel, decide if it's clearly a technical issue, and if so, create a support ticket in Zendesk."

## 4. Drafting updates

"Every Friday at 10 a.m., write up a summary of progress made across all teams in our project board, across all epics, changes made to scope, and highlighting any timeline changes." *(Example of an exception where the value is the weekly timeline to centralize information.)*

Notice the pattern? Good automations start with "When [specific event happens]..." not "Every [time period]...") unless there's specific value in triggering on a daily/weekly/etc. cadence.