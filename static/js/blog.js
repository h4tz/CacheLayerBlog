fetch('/api/posts/')
.then(response => response.json())
.then(posts => {
    const container = document.getElementById('post-list');
    container.innerHTML = '';
    posts.forEach(post => { 
        container.innerHTML += `
        <div class="post-card">
        <h2><a href="/blog/${post.slug}/">${post.title}</a></h2>
        <p>${post.content.substring(0,100)}...</p>
        </div>
        `;  
    });
})
.catch(error => {
    document.getElementById('error').innerText = 'Failed to load posts.';
})

fetch(`/api/posts/${slug}`)
.then(response => response.json())
.then(post => {
    document.getElementById('post-title').innerText = post.title;
    document.getElementById('post-content').innerHTML = `<p>${post.content}</p>`
})
.catch(error => {
    document.getElementById('post-container').innerText = 'Post not found ';
})

document.getElementById('loading').style.display = 'block';
document.getElementById('loading').style.display = 'none';