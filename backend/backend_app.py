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

    GET: Returns a list of all existing posts.
    POST: Creates a new post. Requires 'title' and 'content'.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    
    if request.method == "GET":
        return jsonify(POSTS)

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

        if POSTS:
            new_id = max(post["id"] for post in POSTS) + 1
        else:
            new_id = 1
            
        new_post = {"id": new_id, "title": title, "content": content}

        POSTS.append(new_post)
        return jsonify(new_post), 201
    
    
@app.route("/api/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    """Deletes a specific blog post based on its ID.

    Args:
        id (int): The unique ID of the post to be deleted.

    Returns:
        tuple: JSON response with a success or error message and an HTTP status code.
    """
    for post in POSTS:
        if post["id"] == id:
            POSTS.remove(post)
            return jsonify({
                "message": f"Post with id {id} has been deleted successfully."
            }), 200

    return jsonify({
        "error": f"Post with id {id} was not found."
    }), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
