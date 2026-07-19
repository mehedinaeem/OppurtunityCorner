(function () {
  function initRichTextEditors() {
    if (!window.CKEDITOR) {
      return;
    }

    document.querySelectorAll("textarea.django-rich-text").forEach(function (textarea) {
      if (textarea.dataset.richTextReady === "true") {
        return;
      }

      textarea.dataset.richTextReady = "true";
      window.CKEDITOR.replace(textarea.id, {
        height: 320,
        removePlugins: "elementspath",
        resize_dir: "vertical",
        toolbar: [
          { name: "document", items: ["Source"] },
          { name: "clipboard", items: ["Undo", "Redo"] },
          { name: "styles", items: ["Format"] },
          { name: "basicstyles", items: ["Bold", "Italic", "Underline", "RemoveFormat"] },
          { name: "paragraph", items: ["NumberedList", "BulletedList", "Blockquote"] },
          { name: "links", items: ["Link", "Unlink"] },
        ],
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRichTextEditors);
  } else {
    initRichTextEditors();
  }
})();
