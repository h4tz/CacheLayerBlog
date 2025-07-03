
document.addEventListener('DOMContentLoaded', () => {
    const postContainer = document.getElementById('post-container');
    const titleEl = document.getElementById('post-title');
    const contentEl = document.getElementById('post-content');

    if (!postContainer || slug) return;  // exit if not on detail page

    fetch(`/api/posts/${slug}/`)
    .then(response => {
        if (!response.ok) throw new Error('Not Found');
        return response.json();
    })
    .then(post => {
        titleEl.innerText = post.title;
        contentEl.innerHTML = `<p>${post.content}</p>`;
    })
    .catch(err => {
        postContainer.innerText = 'Post not found';
        console.error(err);
    })
})