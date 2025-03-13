import feedparser
import csv
import ast, re
import time
import json
from google import genai
from google.genai import types

def load_settings():
    print("[DEBUG] Loading settings from settings.json...")
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
        print("[INFO] Settings loaded successfully")
        return settings
    except FileNotFoundError:
        print("[ERROR] settings.json file not found")
        exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON in settings.json")
        exit(1)

def generate(prompt, model, api_key):
    print(f"[DEBUG] Generating response for prompt ({len(prompt)} characters)...")
    client = genai.Client(api_key=api_key)

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    result = ''
    try:
        print(f"[DEBUG] Starting API request to {model}...")
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            result += chunk.text
        print(f"[DEBUG] API request completed successfully")
    except Exception as e:
        print(f"[ERROR] API request failed: {str(e)}")
        return ''

    return result

def read_rss_sources(file_path):
    print(f"[DEBUG] Reading RSS sources from {file_path}...")
    with open(file_path, 'r') as file:
        links = [line.strip() for line in file.readlines() if line.strip()]
    print(f"[INFO] Found {len(links)} RSS feeds in source file")
    return links

def parse_rss_feeds(rss_links):
    print(f"[DEBUG] Parsing {len(rss_links)} RSS feeds...")
    stories = []
    story_index = 1

    for link in rss_links:
        print(f"[INFO] Processing RSS feed: {link}")
        feed = feedparser.parse(link)
        if feed.entries:
            print(f"[INFO] Found {len(feed.entries)} articles in this feed")
            for entry in feed.entries:
                article_link = entry.link if 'link' in entry else 'NO_LINK'
                stories.append([story_index, entry.title, article_link])
                story_index += 1
        else:
            print(f"[WARNING] No articles found in feed {link}")

    print(f"[INFO] Total stories collected: {len(stories)}")
    return stories

def save_to_csv(stories, output_file):
    print(f"[DEBUG] Saving {len(stories)} stories to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["story_index", "title", "article_link", "rating"])
        writer.writerows(stories)
    print("[INFO] CSV save completed")

def send_to_llm(stories, model, api_key, interests):
    prompt = """
        Rate these stories on how interesting they are from 1 to 100.
        Return your answer strictly as a Python list of numbers (for example, [10, 11, 73, 30, 60... etc]).
        Do NOT add whitespace between the numbers and the commas. "
        The ratings must be normally distributed between 50 (100 is most interesting, 0 is least).
        Do not include any extra text.
        Make sure you return EXACTLY ONE NUMBER PER STORY.
        Your output must contain exactly {len(stories)} numbers in the list.
        COMPLETELY ignore the "story_index" value in your assessment, it is irrelevant.
        Focus ONLY on the title and maybe the link.
        Take into account the following interests when rating: {interests}
    """

    print(f"[DEBUG] Sending batch of {len(stories)} stories to LLM")
    modified_prompt = prompt.replace("{len(stories)}", str(len(stories))).replace("{interests}", interests)
    print(f"[API] Prompt length: {len(modified_prompt)} characters")

    response = generate(modified_prompt, model, api_key)
    print(f"[API] Raw LLM response: {response}")

    match = re.search(r'.*(\[.*\])', response)
    if match:
        try:
            ratings = ast.literal_eval(match.group(1))
            print(f"[INFO] Successfully parsed {len(ratings)} ratings")
            return ratings
        except Exception as e:
            print(f"[ERROR] Error parsing ratings: {str(e)}")
            return []
    print("[ERROR] No valid ratings list found in response")
    return []

def batch_stories(stories, batch_size=20):
    print(f"[DEBUG] Batching {len(stories)} stories into groups of {batch_size}")
    for i in range(0, len(stories), batch_size):
        yield stories[i:i + batch_size]

def parse_and_rate():
    # Load settings from JSON file
    settings = load_settings()

    # Extract settings
    model = settings.get("model", "gemini-2.0-flash-lite")
    batch_size = settings.get("batch_size", 20)
    rss_file = settings.get("input_file", "rss_sources.txt")
    output_file = settings.get("output_file", "results.csv")
    api_key = settings.get("google_api_key", "")
    interests = settings.get("interests", "")

    if not api_key:
        print("[ERROR] Google API key is missing in settings.json")
        exit(1)

    print("=== debrief - parsing and rating ===")
    print(f"Using model: {model}")
    print(f"Batch size: {batch_size}")
    print(f"Input file: {rss_file}")
    print(f"Output file: {output_file}")
    print(f"Interests: {interests}")

    rss_links = read_rss_sources(rss_file)

    stories = parse_rss_feeds(rss_links)
    if not stories:
        print("[ERROR] No stories collected")
        return

    all_ratings = []
    for batch_num, batch in enumerate(batch_stories(stories, batch_size), 1):
        print(f"[INFO] Processing batch #{batch_num} ({len(batch)} stories)")
        ratings = send_to_llm(batch, model, api_key, interests)

        if len(ratings) != len(batch):
            print(f"[ERROR] Batch {batch_num} error: Expected {len(batch)} ratings, got {len(ratings)}")
            return

        all_ratings.extend(ratings)
        print(f"[INFO] Completed batch {batch_num}. Total ratings collected: {len(all_ratings)}")

        if batch_num % 15 == 0:
            print("[API] Approaching API limit - waiting 60 seconds")
            time.sleep(60)
        else:
            print("[API] Waiting 4 seconds for rate limit...")
            time.sleep(4)

    if len(all_ratings) != len(stories):
        print(f"[ERROR] Total ratings ({len(all_ratings)}) don't match stories ({len(stories)})")
        return

    for i in range(len(all_ratings)):
        stories[i].append(all_ratings[i])

    print("[INFO] Sorting stories by rating...")
    stories.sort(key=lambda x: x[3], reverse=True)

    save_to_csv(stories, output_file)

    print("[RESULT] Top stories:")
    for story in stories[:5]:
        print(f"Rating {story[3]}: {story[1]} - {story[2]}")

if __name__ == "__main__":
    parse_and_rate()
