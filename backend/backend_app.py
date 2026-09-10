from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route("/api/posts", methods=["GET", "POST"])
def get_post_posts():
    """Manages the retrieval and creation of blog posts.

    GET: Returns a list of all existing posts, optionally sorted by 'title'
        or 'content' and 'direction' ('asc' or 'desc').
    POST: Creates a new post. Requires 'title' and 'content'.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    
    if request.method == "GET":
        sort = request.args.get("sort")
        direction = request.args.get("direction", "asc")

        if sort is None:
            return jsonify(POSTS)

        if sort not in ["title", "content"]:
            return jsonify({
                "error": "Invalid sort field. Use 'title' or 'content'."
            }), 400

        if direction not in ["asc", "desc"]:
            return jsonify({
                "error": "Invalid direction. Use 'asc' or 'desc'."
            }), 400

        sorted_posts = sorted(
            POSTS,
            key=lambda post: post[sort],
            reverse=(direction == "desc")
        )
        return jsonify(sorted_posts)

    if request.method == "POST":
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        missing_fields = []

        if not title:
            missing_fields.append("title")
        if not content:
            missing_fields.append("content")

        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400

        new_id = max((post["id"] for post in POSTS), default=0) + 1
        new_post = {
            "id": new_id,
            "title": title,
            "content": content
        }

        POSTS.append(new_post)
        return jsonify(new_post), 201


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search for blog posts by title or content.

    Accepts the query parameters 'title' and 'content' via the URL.
    The search is case-insensitive.

    Returns:
        tuple: List of matching posts as a JSON response
            and HTTP status code 200.
    """
    
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()
    results = []

    for post in POSTS:
        title_matches = title_query and title_query in post["title"].lower()
        content_matches = content_query and content_query in post["content"].lower()

        if title_matches or content_matches:
            results.append(post)

    return jsonify(results), 200


@app.route("/api/posts/<int:id>", methods=["PUT", "DELETE"])
def update_or_delete_post(id):
    """Updates or deletes a blog post based on its ID.

    Args:
        id (int): The unique ID of the affected post.

    Returns:
        tuple: JSON response containing the post data or a message (indicating success or failure),
            as well as the HTTP status code.
    """
    
    for post in POSTS:
        if post["id"] == id:
            if request.method == "DELETE":
                POSTS.remove(post)
                return jsonify({
                    "message": f"Post with id {id} has been deleted successfully."
                }), 200

            if request.method == "PUT":
                data = request.get_json()
                if "title" in data:
                    post["title"] = data["title"]
                if "content" in data:
                    post["content"] = data["content"]
                return jsonify(post), 200

    return jsonify({
        "error": f"Post with id {id} was not found."
    }), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
