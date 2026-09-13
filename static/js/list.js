document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/posts/')
    .then(function (res) { return res.json() })
    .then(function (data) {
      var container = document.getElementById('post-list')
      if (!container) return
      var posts = data.results || []
      if (posts.length === 0) {
        container.innerHTML = '<p>No posts yet.</p>'
        return
      }
      var html = '<ul>'
      posts.forEach(function (post) {
        html += '<li><a href="/blog/' + post.slug + '/">' + post.title + '</a></li>'
      })
      html += '</ul>'
      container.innerHTML = html
    })
    .catch(function (err) {
      console.error('Failed to load posts:', err)
    })
})
