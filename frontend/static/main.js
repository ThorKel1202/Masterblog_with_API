// Run once the window is fully loaded
window.onload = function () {
    const savedBaseUrl = localStorage.getItem("apiBaseUrl");

    if (savedBaseUrl) {
        document.getElementById("api-base-url").value = savedBaseUrl;
        loadPosts();
    }
};


// Display posts on the page
function displayPosts(data) {
    const postContainer = document.getElementById("post-container");

    postContainer.innerHTML = "";

    data.forEach(post => {
        const postDiv = document.createElement("div");

        postDiv.className = "post";

        // Escape text content to prevent XSS attacks
        const safeTitle = escapeHtml(post.title);
        const safeContent = escapeHtml(post.content);
        const safeAuthor = escapeHtml(post.author);
        const safeDate = escapeHtml(post.date);
        const safeLikes = post.likes !== undefined ? post.likes : 0;

        postDiv.innerHTML = `
            <h2>${safeTitle}</h2>
            <p>${safeContent}</p>

            <div class="post-meta">
                <span class="author">
                    Author: ${safeAuthor}
                </span>

                <span class="date">
                    Date: ${safeDate}
                </span>
            </div>

            <div class="post-actions">
                <button
                    class="like-btn"
                    onclick="likePost(${post.id})"
                >
                    👍 Like
                </button>

                <span class="likes-count">
                    ${safeLikes} Likes
                </span>

                <button
                    class="edit-btn"
                    onclick="editPost(${post.id})"
                >
                    Edit
                </button>

                <button
                    class="delete-btn"
                    onclick="deletePost(${post.id})"
                >
                    Delete
                </button>
            </div>
        `;

        postContainer.appendChild(postDiv);
    });
}


// Load all posts from the API
function loadPosts() {
    const baseUrl = document.getElementById("api-base-url").value;

    localStorage.setItem("apiBaseUrl", baseUrl);

    fetch(`${baseUrl}/posts`)
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(data => {
            displayPosts(data);
        })
        .catch(error => {
            console.error("Error loading posts:", error);
        });
}


// Search for blog posts
function searchPosts() {
    const baseUrl = document.getElementById("api-base-url").value;
    const searchQuery = document.getElementById("search-input").value;

    fetch(
        `${baseUrl}/posts/search?search=${encodeURIComponent(searchQuery)}`
    )
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                const postContainer =
                    document.getElementById("post-container");

                postContainer.innerHTML =
                    "<p class='no-results'>No posts found.</p>";

                return;
            }

            displayPosts(data);

            // Clear the search field after a successful search
            document.getElementById("search-input").value = "";
        })
        .catch(error => {
            console.error("Error searching for posts:", error);
        });
}


// Sort blog posts
function sortPosts(sortField, direction) {
    const baseUrl = document.getElementById("api-base-url").value;

    fetch(
        `${baseUrl}/posts?sort=${sortField}&direction=${direction}`
    )
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                const postContainer =
                    document.getElementById("post-container");

                postContainer.innerHTML =
                    "<p class='no-results'>" +
                    "No posts available to sort." +
                    "</p>";

                return;
            }

            displayPosts(data);
        })
        .catch(error => {
            console.error("Error sorting posts:", error);
        });
}


// Escape special HTML characters to prevent XSS attacks
function escapeHtml(text) {
    if (!text) {
        return "";
    }

    return text
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// Add a new post
function addPost() {
    const baseUrl = document.getElementById("api-base-url").value;
    const postTitle = document.getElementById("post-title").value;
    const postContent = document.getElementById("post-content").value;
    const postAuthor = document.getElementById("post-author").value;

    fetch(`${baseUrl}/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: postTitle,
            content: postContent,
            author: postAuthor
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(post => {
            console.log("Post added:", post);

            // Clear the input fields after adding the post
            document.getElementById("post-title").value = "";
            document.getElementById("post-content").value = "";
            document.getElementById("post-author").value = "";

            loadPosts();
        })
        .catch(error => {
            console.error("Error adding post:", error);
        });
}


// Delete a post
function deletePost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    fetch(`${baseUrl}/posts/${postId}`, {
        method: "DELETE"
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(data => {
            console.log("Post deleted:", data);
            loadPosts();
        })
        .catch(error => {
            console.error("Error deleting post:", error);
        });
}


// Like a post
function likePost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    fetch(`${baseUrl}/posts/${postId}/like`, {
        method: "POST"
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(post => {
            console.log("Post liked:", post);
            loadPosts();
        })
        .catch(error => {
            console.error("Error liking post:", error);
        });
}


// Show the edit form for a post
function editPost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    fetch(`${baseUrl}/posts`)
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(posts => {
            const post = posts.find(post => post.id === postId);

            if (!post) {
                console.error("Post not found.");
                return;
            }

            const postContainer =
                document.getElementById("post-container");

            const postElements =
                postContainer.getElementsByClassName("post");

            for (const postElement of postElements) {
                const editButton =
                    postElement.querySelector(".edit-btn");

                if (
                    editButton &&
                    editButton.getAttribute("onclick") ===
                        `editPost(${postId})`
                ) {
                    postElement.innerHTML = `
                        <h2>Edit Post</h2>

                        <input
                            type="text"
                            id="edit-title-${postId}"
                            value="${escapeHtml(post.title)}"
                        >

                        <input
                            type="text"
                            id="edit-author-${postId}"
                            value="${escapeHtml(post.author)}"
                        >

                        <textarea
                            id="edit-content-${postId}"
                        >${escapeHtml(post.content)}</textarea>

                        <div class="post-actions">
                            <button
                                class="like-btn"
                                onclick="savePost(${postId})"
                            >
                                Save
                            </button>

                            <button
                                class="delete-btn"
                                onclick="loadPosts()"
                            >
                                Cancel
                            </button>
                        </div>
                    `;

                    break;
                }
            }
        })
        .catch(error => {
            console.error("Error editing post:", error);
        });
}


// Save an edited post
function savePost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    const newTitle =
        document.getElementById(`edit-title-${postId}`).value.trim();

    const newAuthor =
        document.getElementById(`edit-author-${postId}`).value.trim();

    const newContent =
        document.getElementById(`edit-content-${postId}`).value.trim();

    if (
        newTitle === "" ||
        newAuthor === "" ||
        newContent === ""
    ) {
        alert("Title, author and content must not be empty.");
        return;
    }

    fetch(`${baseUrl}/posts/${postId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: newTitle,
            content: newContent,
            author: newAuthor
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(
                    `HTTP-Fehler! Status: ${response.status}`
                );
            }

            return response.json();
        })
        .then(post => {
            console.log("Post updated:", post);
            loadPosts();
        })
        .catch(error => {
            console.error("Error updating post:", error);
        });
}
