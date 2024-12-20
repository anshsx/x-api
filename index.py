from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def fetch_google_results(query):
    google_results = {"images": [], "videos": [], "webpages": []}
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}&hl=en"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "url?q=" in href:
                actual_link = parse_qs(urlparse(href).query)["q"][0]
                if "youtube.com" in actual_link or "youtu.be" in actual_link:
                    google_results["videos"].append(actual_link)
                else:
                    google_results["webpages"].append(actual_link)

        # Extract images
        for img in soup.find_all("img"):
            img_src = img.get("src")
            if img_src and img_src.startswith("http"):
                google_results["images"].append(img_src)

    except Exception as e:
        print(f"Google search failed: {e}")
    
    return google_results


def fetch_bing_results(query):
    bing_results = {"images": [], "videos": [], "webpages": []}
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(" ", "+")
    url = f"https://www.bing.com/search?q={query}&form=QBLH"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "youtube.com" in href or "youtu.be" in href:
                bing_results["videos"].append(href)
            elif "http" in href:
                bing_results["webpages"].append(href)

        # Extract images
        image_section = soup.find("div", {"id": "b_content"})
        if image_section:
            for img in image_section.find_all("img"):
                img_src = img.get("src")
                if img_src and img_src.startswith("http"):
                    bing_results["images"].append(img_src)

    except Exception as e:
        print(f"Bing search failed: {e}")
    
    return bing_results


def combine_and_deduplicate_results(results1, results2):
    combined_results = {
        "images": list(set(results1["images"] + results2["images"])),
        "videos": list(set(results1["videos"] + results2["videos"])),
        "webpages": list(set(results1["webpages"] + results2["webpages"])),
    }
    return combined_results


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        google_results = fetch_google_results(query)
        if not google_results["webpages"]:  # If Google fails, use Bing
            bing_results = fetch_bing_results(query)
            return jsonify(bing_results)
        else:
            bing_results = fetch_bing_results(query)
            combined_results = combine_and_deduplicate_results(google_results, bing_results)
            return jsonify(combined_results)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"images": [], "videos": [], "webpages": []})


if __name__ == "__main__":
    app.run(debug=True)
