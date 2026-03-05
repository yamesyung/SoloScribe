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

var table = $('#books-table').DataTable({
    searching: false,
    lengthChange: false,
    paging: false,
    info: false,
    order: [[ 1, 'asc']],
    columnDefs: [{ targets: 4, orderable: false }]
});


document.addEventListener('DOMContentLoaded', () => {
  const content = document.getElementById('content');
  const showMore = document.getElementById('showMore');

  if (!content || !showMore) return;

  if (content.scrollHeight <= content.clientHeight) {
    showMore.style.display = 'none';
  }
});

function toggleText() {
  const content = document.getElementById('content');
  const showMore = document.getElementById('showMore');
  const showLess = document.getElementById('showLess');

  if (!content || !showMore || !showLess) return;

  const isExpanded = content.classList.contains('expanded');
  content.classList.toggle('expanded');
  showMore.style.display = isExpanded ? 'inline' : 'none';
  showLess.style.display = isExpanded ? 'none' : 'inline';
}

document.addEventListener('DOMContentLoaded', function() {
    const colorThief = new ColorThief();

    document.querySelectorAll('.cover-image').forEach((img, index) => {
        if (img.complete) {

            const color = colorThief.getColor(img);
            const row = document.getElementById(`row-${index + 1}`);
            if (color && row) {
                row.style.background = `linear-gradient(to right, rgba(21, 27, 35, 0), rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
            }
        } else {
            img.onload = function() {
                const color = colorThief.getColor(img);
                const row = document.getElementById(`row-${index + 1}`);
                if (color && row) {
                row.style.background = `linear-gradient(to right, rgba(21, 27, 35, 0), rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
                }
            };
        }
    });
});

function showAuthorOverlay() {
    document.getElementById("author-overlay").style.display = "block";
}

function closeAuthorOverlay() {
    document.getElementById('author-overlay').style.display = 'none';
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        closeAuthorOverlay();
    }
});

function adjustTextareaHeight(selector) {
    const textarea = document.querySelector(selector);
    if (!textarea) return;

    function autoGrow() {
        textarea.style.height = "auto";
        textarea.style.height = (textarea.scrollHeight + 40) + "px";
    }

    autoGrow();
    textarea.addEventListener("input", autoGrow);
}

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "author-overlay") {
    const overlay = document.getElementById('author-overlay');
        const gradient = `radial-gradient(circle,
            rgb(${palette[1][0]}, ${palette[1][1]}, ${palette[1][2]}),
            rgb(${palette[0][0]}, ${palette[0][1]}, ${palette[0][2]}))`;
        overlay.style.background = gradient;
    }
});
