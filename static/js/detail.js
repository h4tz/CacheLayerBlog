document.addEventListener("DOMContentLoaded", () => {
  if (typeof slug === "undefined") {
    console.error("Slug not defined.");
    return;
  }

  fetch(`/api/posts/${slug}/`)
    .then(response => {
      if (!response.ok) throw new Error("Post not found");
      return response.json();
    })
    .then(post => {
      document.getElementById("post-title").innerText = post.title;
      document.getElementById("post-content").innerHTML = `<p>${post.content}</p>`;
    })
    .catch(error => {
      document.getElementById("post-container").innerText = 'Post not found';
      console.error(error);
    });
});
