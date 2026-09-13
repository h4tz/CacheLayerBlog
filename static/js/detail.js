document.addEventListener('DOMContentLoaded', function () {
  var slug = document.getElementById('post-detail')?.dataset?.slug
  if (!slug) return

  fetch('/api/posts/' + slug + '/')
    .then(function (res) {
      if (!res.ok) throw new Error('Post not found')
      return res.json()
    })
    .then(function (post) {
      var container = document.getElementById('post-detail')
      container.innerHTML =
        '<h1>' + post.title + '</h1>' +
        '<small>' + new Date(post.created_at).toLocaleDateString() + '</small>' +
        '<div>' + post.content + '</div>'
    })
    .catch(function (err) {
      console.error('Failed to load post:', err)
      var container = document.getElementById('post-detail')
      if (container) container.innerHTML = '<p>Post not found.</p>'
    })
})
