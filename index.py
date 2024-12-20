from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Function to fetch Google search results based on content type
def fetch_google_results(query, content_type):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(" ", "+")
    
    # Build Google search URL based on content type
    if content_type == "image":
        url = f"https://www.google.com/search?tbm=isch&q={query}"
    elif content_type == "video":
        url = f"https://www.google.com/search?tbm=vid&q={query}"
    else:
        url = f"https://www.google.com/search?q={query}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract URLs based on content type
        if content_type == "image":
            for img in soup.find_all("img"):
                img_src = img.get("src")
                if img_src and img_src.startswith("http"):
                    results.append(img_src)
        elif content_type == "video":
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "url?q=" in href:
                    actual_link = parse_qs(urlparse(href).query)["q"][0]
                    if "youtube.com" in actual_link or "youtu.be" in actual_link:
                        results.append(actual_link)
        else:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "url?q=" in href:
                    actual_link = parse_qs(urlparse(href).query)["q"][0]
                    results.append(actual_link)

    except Exception as e:
        print(f"Google search failed: {e}")
    
    return results

# Function to fetch Bing search results based on content type
def fetch_bing_results(query, content_type):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(" ", "+")
    
    # Build Bing search URL based on content type
    if content_type == "image":
        url = f"https://www.bing.com/images/search?q={query}"
    elif content_type == "video":
        url = f"https://www.bing.com/videos/search?q={query}"
    else:
        url = f"https://www.bing.com/search?q={query}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract URLs based on content type
        if content_type == "image":
            for img in soup.find_all("img"):
                img_src = img.get("src")
                if img_src and img_src.startswith("http"):
                    results.append(img_src)
        elif content_type == "video":
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "youtube.com" in href or "youtu.be" in href:
                    results.append(href)
        else:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("http"):
                    results.append(href)

    except Exception as e:
        print(f"Bing search failed: {e}")
    
    return results


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    content_type = request.args.get("type", "webpage")  # Default to "webpage" if no type is specified

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    if content_type not in ["image", "video", "webpage"]:
        return jsonify({"error": "Invalid type. Must be 'image', 'video', or 'webpage'"}), 400

    try:
        # Fetch results from Google and Bing
        google_results = fetch_google_results(query, content_type)
        bing_results = fetch_bing_results(query, content_type)
        
        # Combine and deduplicate results
        combined_results = list(set(google_results + bing_results))
        return jsonify({content_type: combined_results})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({content_type: []})


if __name__ == "__main__":
    app.run(debug=True)
