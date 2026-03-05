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
                row.style.background = `linear-gradient(to right, #ffffff, rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
            }
        } else {
            img.onload = function() {
                const color = colorThief.getColor(img);
                const row = document.getElementById(`row-${index + 1}`);
                if (color && row) {
                    row.style.background = `linear-gradient(to right, #ffffff, rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
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