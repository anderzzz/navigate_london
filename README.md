# AI Assistant Prototype for London Transit Planning
Transport for London (TfL) publishes a number of APIs for public transit in London, UK. The code in this repo is a prototype AI assistant comprising four AI agents that through tool-use gathers data from the TfL APIs and presents the results in various ways (text summary, map drawings, calendar reminders). The tool-using AIs are all based on Anthropic's LLM APIs.

The prototype is discussed in detail in the following [article in Towards AI.](https://pub.towardsai.net/london-commute-agent-from-concepts-to-pretty-maps-6b2a0a28dcc8)

The prototype can be run on command-line, see the script `main_agents.py`.

To run the prototype two API keys are required:
* Anthropic API key, assumed to be stored in environment variable `ANTHROPIC_API_KEY`.
* TfL API key, assumed to be stored  in environment variable `TFL_API_KEY`.

The latter can be requested for free after registration at: https://api-portal.tfl.gov.uk/signup

## Agent Design and Instantiation
The agent design is shown in the image below.

![agent_design](https://github.com/anderzzz/navigate_london/blob/main/blog/agent_design.png?raw=true)

All agents in the prototype are instantiated in `agent/build_agents.py`. They are instances of the `Engine` class in `semantics/anthropic/engine.py`.

## TfL APIs and Payload Processing
The TfL API endpoint Journey/JourneyResult is relatively complex. In order to manage calls to it, the parameters for the TfL API are a Pydantic model in `journey_planner`. This was created in November 2024 and at the time compatible with the TfL API.
