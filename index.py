from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Function to fetch YouTube video IDs from Google
def fetch_youtube_results(query):
    results = {"video_ids": []}
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(" ", "+")

    # Google search URL for YouTube videos
    url = f"https://www.google.com/search?q=site:youtube.com+{query}&tbm=vid"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract YouTube video IDs
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "url?q=" in href:
                actual_link = parse_qs(urlparse(href).query).get("q", [None])[0]
                if actual_link and ("youtube.com/watch" in actual_link or "youtu.be" in actual_link):
                    parsed_url = urlparse(actual_link)
                    if "youtube.com/watch" in actual_link:
                        video_id = parse_qs(parsed_url.query).get("v", [None])[0]
                    elif "youtu.be" in actual_link:
                        video_id = parsed_url.path.lstrip("/")
                    if video_id:
                        results["video_ids"].append(video_id)
    except Exception as e:
        print(f"Failed to fetch YouTube results: {e}")
    
    # Remove duplicates
    results["video_ids"] = list(set(results["video_ids"]))
    return results

@app.route("/youtube-search", methods=["GET"])
def youtube_search():
    query = request.args.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Fetch YouTube results
        youtube_results = fetch_youtube_results(query)

        return jsonify(youtube_results)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"video_ids": []})

if __name__ == "__main__":
    app.run(debug=True)
