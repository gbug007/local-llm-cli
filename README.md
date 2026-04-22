# Overview
This is a CLI program using the Rich Python library and a local LLM (using standard OpenAI compatible endpoints). The intention is to develop a system that can access your codebase and use it for responses.

# Long-term System Goal:
My goal with this project is to automate some C debugging by integrating the LLM with some C tools. I'm also generally using this to explore what's possible with a local LLM and an API.

# TODO List
- Determine agentic system for interacting with tools
- Figure out how to utilize tools with endpoints
- Determine if this tool is sufficient for what I want to use it for
    - From current testing it can generate good code and answer a variety of questions pretty well
    - May want to try out with non-local LLMs in the future
- Determine if any other steps are needed for interfacing with code (reading the files either
by text or through the API somehow)