let palette = null;

const backgroundImage = getComputedStyle(document.body).backgroundImage;
const imageUrl = backgroundImage.slice(5, -2);

const img = new Image();
img.src = imageUrl;

img.onload = () => {
  const colorThief = new ColorThief();
  palette = colorThief.getPalette(img, 2);     // Array of [R, G, B]

  if (palette) {
    palette.sort((a, b) => {
      const brightnessA = 0.299 * a[0] + 0.587 * a[1] + 0.114 * a[2];
      const brightnessB = 0.299 * b[0] + 0.587 * b[1] + 0.114 * b[2];
      return brightnessA - brightnessB;
    });
  }
  else {
    palette = [[255, 255, 255], [255, 255, 255]];
  }

};

img.onerror = () => {
  console.error('Failed to load image');
};


function showQuoteOverlay() {
    document.getElementById("quote-overlay").style.display = "block";
}

function closeQuoteOverlay() {
    document.getElementById('quote-overlay').style.display = 'none';
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        closeQuoteOverlay();
    }
});

function adjustTextareaHeight() {
    var reviewTextarea = document.getElementById("quote-input");

    function autoGrowTextarea() {
        reviewTextarea.style.height = "auto";
        reviewTextarea.style.height = (reviewTextarea.scrollHeight + 40) + "px";
    }

    autoGrowTextarea();
}

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "quote-overlay") {
        var input = document.querySelector('.customLook');
        var button = input ? input.nextElementSibling : null;

        if (input && !input.dataset.tagifyInitialized) {
            // Initialize Tagify
            var tagify = new Tagify(input, {
                pattern: /^[^,]+$/,
                transformTag: function(tagData) {
                    tagData.value = tagData.value.replace(/\s+/g, '-');
                    return tagData;
                },
                editTags: {
                    keepInvalid: false,
                },
                validate: (tag) => {
                    const maxLength = 45;
                    if (tag.value.length > maxLength) {
                        tag.error = `Tag is too long (max ${maxLength} characters allowed)`;
                        return false;
                    }
                    return true;
                }
            });

            input.dataset.tagifyInitialized = "true";

            if (button) {
                button.addEventListener("click", function() {
                    tagify.addEmptyTag();
                });
            }

        }
        const overlay = document.getElementById('quote-overlay');
        const gradient = `radial-gradient(circle,
            rgb(${palette[1][0]}, ${palette[1][1]}, ${palette[1][2]}),
            rgb(${palette[0][0]}, ${palette[0][1]}, ${palette[0][2]}))`;
        overlay.style.background = gradient;
    }
});

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "review-wrapper") {
        var reviewBtn = document.getElementById('review-btn');
        var reviewContent = document.getElementById('review-wrapper')

         if (reviewContent && reviewContent.textContent.trim() !== "") {
            reviewBtn.innerText = "Edit review";
        } else {
            reviewBtn.innerText = "Add review";
        }
    }
});