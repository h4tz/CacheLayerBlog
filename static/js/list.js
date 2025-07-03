
document.addEventListener("DOMContentLoaded", () => {
    const loading = document.getElementById('loading');
    const container = document.getElementById('post-list');
    const error = document.getElementById('error');

    if (!container) return;
    loading.style.display = 'block';

    fetch('/api/posts/')
    .then(response => response.json())
    .then(posts => {
        loading.style.display = 'none' ;
        container.innerHTML = '';
        posts.forEach(post => {
            container.innerHTML += `
            <div class = "post-card">
            <h2><a href="/blog/${post.slug}/">${post.title}</a></h2>
            <p>${post.content.substring(0,100)}...</p>
            </div>
            `
        })
    })
    .catch(err => {
        loading.style.display = 'none';
        error.innerText = 'Failed to load posts. ';
        console.error(err);
    })
})
