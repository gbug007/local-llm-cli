# Overview
This is a CLI program using the Rich Python library and a local LLM (using standard OpenAI compatible endpoints). The intention is to develop a system that can access your codebase and use it for responses.

# Long-term System Goal:
My goal with this project is to automate some C debugging by integrating the LLM with some C tools. I'm also generally using this to explore what's possible with a local LLM and an API.

# How to Use:
To use, swap out the endpoint and model with whatever one you're using. I've only tested it on a local LLM but it should work with others. Also note that you may need to use an API_KEY, which should be stored as an environment variable or some other secure way.

[Handy Reddit guide I used as a starting point.](https://www.reddit.com/r/LocalLLaMA/comments/16y95hk/a_starter_guide_for_playing_with_your_own_local_ai/)

[To set it up exactly like I did, check out KoboldCPP.](https://github.com/lostruins/koboldcpp)

[They also have a posting of .gguf files, which you need to download to run the LLM.](https://github.com/LostRuins/koboldcpp/wiki#what-models-does-koboldcpp-support-what-architectures-are-supported)





# TODO List
- Determine agentic system for interacting with tools
- Figure out how to utilize tools with endpoints
- Determine if this tool is sufficient for what I want to use it for
    - From current testing it can generate good code and answer a variety of questions pretty well
    - May want to try out with non-local LLMs in the future
- Determine if any other steps are needed for interfacing with code (reading the files either
by text or through the API somehow)