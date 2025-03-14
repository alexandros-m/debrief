# debrief
open source, ai rss news aggregator with interest-based sorting

![usage example](style/screenshot.png)

## prerequisites:

- Python 3
- [Google AI Studio API key](https://aistudio.google.com/apikey)

Windows:

- `pip install -r requirements.txt`

Linux (apt-based):

- `sudo apt update && sudo apt install -y python3-full python3-venv python3-pip`
- `python3 -m venv .myenv`
- `source .myenv/bin/activate`
- `pip install -r requirements.txt`

## execution:

- Configure your RSS sources from `rss_sources.txt`
- Add your API key to `settings.json` (general configuration is also handled from this file - for example *interests*)
- `python main.py`
- Wait for the parsing, analysis and html-building to finish
- Open `debrief.html` using your browser and read the newspaper that you created based on your interests!

## todo:

- `"preview-sites": false` doesn't actually disable the http requests to the sites, so it basically does nothing for now
- option to run the llm locally - use different APIs with enough credits for the program to work consistently (like it does with Google AI Studio)
- better prompt - more suitable gemini model (?)
- format the object sent to the model in a better way, strip the index number that is also sent
- change the .html output's layout to something more sophisticated and maybe user-friendly
- transform the CLI scripts to a web server application with a proper website frontend - maybe integrate the whole project to an Electron-type program
- add a buffer for already rated and parsed stories, which would be a prerequisite for real-time aggregation (rating + parsing of the website for the preview)
