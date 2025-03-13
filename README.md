# debrief
open source, ai rss news aggregator with interest-based sorting
![usage example](styles/screenshot.png)

## prerequisites

- Python 3
- [Google AI Studio API key](https://aistudio.google.com/apikey)
Windows:
- `pip install -r requirements.txt`
Linux (apt-based):
- `sudo apt update && sudo apt install -y python3-full python3-venv python3-pip`
- `python3 -m venv .myenv`
- `source .myenv/bin/activate`
- `pip install -r requirements.txt`

## execution

- Configure your RSS sources from `rss_sources.txt`
- Add your API key to `settings.json` (general configuration is also handled from this file - for example *interests*)
- `python main.py`
- Wait for the parsing, analysis and html-building to finish
- Open `debrief.html` using your browser and read the newspaper that you created based on your interests!
