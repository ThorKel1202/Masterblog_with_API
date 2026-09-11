from datetime import datetime
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


def load_posts():
    """Loads the blog posts from the JSON file.

    Returns:
        list: A list of dictionaries representing the entries.
    """
    try:
        with open("posts.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_posts(posts):
    """Saves the blog posts to the JSON file.

    Args:
        posts (list): The list of posts to be saved.
    """
    with open("posts.json", "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)


app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Masterblog API"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/api/posts", methods=["GET", "POST"])
def get_post_posts():
    """Manages the retrieval and creation of blog posts.

    GET: Returns a list of all posts, optionally sorted by 'title',
        'content', 'author', or 'date' and 'direction' ('asc' or 'desc').
    POST: Creates a new post. Requires 'title', 'content',
        'author', and 'date'.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    if request.method == "GET":
        posts = load_posts()
        sort = request.args.get("sort")
        direction = request.args.get("direction", "asc")

        if sort is None:
            return jsonify(posts)

        if sort not in ["title", "content", "author", "date"]:
            return jsonify({
                "error": (
                    "Invalid sort field. "
                    "Use 'title', 'content', 'author', or 'date'."
                )
            }), 400

        if direction not in ["asc", "desc"]:
            return jsonify({
                "error": "Invalid direction. Use 'asc' or 'desc'."
            }), 400

        if sort == "date":
            sorted_posts = sorted(
                posts,
                key=lambda post: datetime.strptime(post["date"], "%Y-%m-%d"),
                reverse=(direction == "desc")
            )
        else:
            sorted_posts = sorted(
                posts,
                key=lambda post: post[sort].lower(),
                reverse=(direction == "desc")
            )

        return jsonify(sorted_posts)

    if request.method == "POST":
        data = request.get_json()
        
        title = data.get("title")
        content = data.get("content")
        author = data.get("author")
        
        missing_fields = []
        
        if not title:
            missing_fields.append("title")
        
        if not content:
            missing_fields.append("content")
        
        if not author:
            missing_fields.append("author")
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        posts = load_posts()
        
        if posts:
            new_id = max(post["id"] for post in posts) + 1
        else:
            new_id = 1
        
        date = datetime.now().strftime("%Y-%m-%d")
        
        new_post = {
            "id": new_id,
            "title": title,
            "content": content,
            "author": author,
            "date": date
        }
        
        posts.append(new_post)
        
        save_posts(posts)
        
        return jsonify(new_post), 201


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Searches for blog posts in all text fields.

    Accepts the 'search' query parameter via the URL. The search is
    case-insensitive and checks the title, content, author, and date.

    Returns:
        tuple: JSON response with matching posts and status code 200.
    """
    search_query = request.args.get("search", "").lower()
    posts = load_posts()
    results = []

    for post in posts:
        title_matches = search_query in post["title"].lower()
        content_matches = search_query in post["content"].lower()
        author_matches = search_query in post["author"].lower()
        date_matches = search_query in post["date"].lower()

        if (
            title_matches
            or content_matches
            or author_matches
            or date_matches
        ):
            results.append(post)

    return jsonify(results), 200


@app.route("/api/posts/<int:id>", methods=["PUT", "DELETE"])
def update_or_delete_post(id):
    """Updates or deletes a blog post based on its ID.

    Args:
        id (int): The unique ID of the affected post.

    Returns:
        tuple: JSON response and the HTTP status code.
    """
    posts = load_posts()

    for post in posts:
        if post["id"] == id:
            if request.method == "DELETE":
                posts.remove(post)
                save_posts(posts)
                return jsonify({
                    "message": f"Post with id {id} has been deleted successfully."
                }), 200

            if request.method == "PUT":
                data = request.get_json()
                if "title" in data:
                    post["title"] = data["title"]
                if "content" in data:
                    post["content"] = data["content"]
                if "author" in data:
                    post["author"] = data["author"]
                
                post["date"] = datetime.now().strftime("%Y-%m-%d")

                save_posts(posts)
                return jsonify(post), 200

    return jsonify({
        "error": f"Post with id {id} was not found."
    }), 404


@app.route("/api/posts/<int:id>/like", methods=["POST"])
def like_post(id):
    """Increase the number of likes for a post."""
    posts = load_posts()

    for post in posts:
        if post["id"] == id:
            post["likes"] += 1
            save_posts(posts)

            return jsonify(post), 200

    return jsonify({
        "error": f"Post with id {id} was not found."
    }), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
