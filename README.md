# Megamania

A 2D space shooter based on Activision's [Megamania](https://en.wikipedia.org/wiki/Megamania) game from 1982. It is written with Python and the Arcade 3.0 library, and uses [Rye for package management](https://rye.astral.sh/).

This game itself has been made entirely using Anthropic's AI, [Claude 3 Sonnet](https://claude.ai), with prompt engineering supplied by me.

I ask Claude to maintain separate [requirements](https://github.com/bcorfman/megamania/blob/main/actions_req.txt) [files](https://github.com/bcorfman/megamania/blob/main/game_requirements.txt) for the code that it wrote, once it got beyond the first simple coding tasks. For one thing, Claude -- just like ChatGPT or any other RAG-based AIs -- has a hard time keeping track of why features were added or changed in the code. This kind of info could be maintained through code comments, but personally I find it's easier to read and reference a separate file. Regardless, maintaining the requirements file, referencing it, and then having Claude update it to reflect any code changes are what I've found to be a personal best practice for LLM software development. It seems to be the best way to keep the AI from repeating prior errors and keep it progressing forward.
