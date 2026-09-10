from datetime import datetime
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


def load_posts():
    """Lädt die Blog-Beiträge aus der JSON-Datei.

    Returns:
        list: Eine Liste von Dictionaries, die die Beiträge repräsentieren.
    """
    try:
        with open("posts.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_posts(posts):
    """Speichert die Blog-Beiträge in die JSON-Datei.

    Args:
        posts (list): Die Liste der zu speichernden Beiträge.
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
    """Verwaltet das Abrufen und Erstellen von Blog-Beiträgen.

    GET: Gibt eine Liste aller Beiträge zurück, optional sortiert nach 'title',
        'content', 'author' oder 'date' und 'direction' ('asc' oder 'desc').
    POST: Erstellt einen neuen Beitrag. Erfordert 'title', 'content',
        'author' und 'date'.

    Returns:
        tuple: JSON-Response und HTTP-Statuscode.
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
    """Sucht nach Blog-Beiträgen in allen Textfeldern.

    Akzeptiert den Query-Parameter 'search' über die URL. Die Suche ignoriert
    Groß- und Kleinschreibung und prüft Titel, Inhalt, Autor und Datum.

    Returns:
        tuple: JSON-Response mit passenden Beiträgen und Statuscode 200.
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
    """Aktualisiert oder löscht einen Blog-Beitrag anhand seiner ID.

    Args:
        id (int): Die eindeutige ID des betroffenen Beitrags.

    Returns:
        tuple: JSON-Response und der HTTP-Statuscode.
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
