// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to display posts on the page
function displayPosts(data) {
    const postContainer = document.getElementById('post-container');
    postContainer.innerHTML = '';

    data.forEach(post => {
        const postDiv = document.createElement('div');
        postDiv.className = 'post';

        // Mask text content to prevent XSS attacks.
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

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(baseUrl + '/posts')
        .then(response => response.json())
        .then(data => {
            displayPosts(data);
        })
        .catch(error => console.error('Error:', error));
}



// Function to sort blog posts
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
                    "<p class='no-results'>"
                    + "No posts available to sort."
                    + "</p>";

                return;
            }

            displayPosts(data);
        })
        .catch(error => {
            console.error("Error sorting posts:", error);
        });
}

// Helper function for escaping special HTML characters (protection against XSS)
// Note: If this function already exists in your main.js, you can leave it there.
function escapeHtml(text) {
    if (!text) return "";
    return text
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date') ? document.getElementById('post-date').value : "";

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor, date: postDate })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Post deleted:', data);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));
}

// Function to send a POST request to the API to like a post
function likePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId + '/like', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post liked:', post);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Function to show the edit form for a post
function editPost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts')
        .then(response => response.json())
        .then(posts => {
            var post = posts.find(post => post.id === postId);

            if (!post) {
                console.error('Post not found.');
                return;
            }

            const postContainer =
                document.getElementById('post-container');

            const postElements =
                postContainer.getElementsByClassName('post');

            for (let postElement of postElements) {
                const editButton =
                    postElement.querySelector('.edit-btn');

                if (
                    editButton &&
                    editButton.getAttribute('onclick') ===
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
        .catch(error => console.error('Error:', error));
}

// Function to save the edited post
function savePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    var newTitle =
        document.getElementById('edit-title-' + postId).value.trim();

    var newAuthor =
        document.getElementById('edit-author-' + postId).value.trim();

    var newContent =
        document.getElementById('edit-content-' + postId).value.trim();

    if (
        newTitle === '' ||
        newAuthor === '' ||
        newContent === ''
    ) {
        alert('Title, author and content must not be empty.');
        return;
    }

    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: newTitle,
            content: newContent,
            author: newAuthor
        })
    })
        .then(response => response.json())
        .then(post => {
            console.log('Post updated:', post);
            loadPosts();
        })
        .catch(error => console.error('Error:', error));
}

