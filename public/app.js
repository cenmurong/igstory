// IGStory Bot V2 — dashboard script
// Marks the page as loaded and stamps the deploy time.
document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("deploy-status");
  if (el) {
    el.textContent = "Live · " + new Date().toISOString().slice(0, 10);
  }
});
