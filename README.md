# AI Assistant Prototype for London Transit Planning
Transport for London (TfL) publishes a number of APIs for public transit in London, UK. The code in this repo is a prototype AI assistant comprising four AI agents that through tool-use gathers data from the TfL APIs and presents the results in various ways (text summary, map drawings, calendar reminders). The tool-using AIs are all based on Anthropic's LLM APIs.

The prototype is discussed in detail in the following blog post: <INSERT URL>

The prototype can be run on command-line, see the script `main_agents.py`.

To run the prototype two API keys are required:
* Anthropic API key, assumed to be stored in environment variable `ANTHROPIC_API_KEY`.
* TfL API key, assumed to be stored  in environment variable `TFL_API_KEY`.

The latter can be requested for free after registration at: https://api-portal.tfl.gov.uk/signup

## Agent Design and Instantiation

