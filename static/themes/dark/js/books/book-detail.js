function showQuoteOverlay() {
    document.getElementById("quote-overlay").style.display = "block";
}

function closeQuoteOverlay() {
    document.getElementById('quote-overlay').style.display = 'none';
}

function showMapOverlay() {
    document.getElementById("map-overlay").style.display = "block";
}

function closeMapOverlay() {
    document.getElementById('map-overlay').style.display = 'none';
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        closeQuoteOverlay();
        closeMapOverlay()
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
    if (event.detail.target.id === "quote-overlay") {
        var input = document.querySelector('.quoteTag');
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

    }
});

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "quote-overlay") {

        function initTagify(selector, pattern = /^[^,]+$/) {
            const input = document.querySelector(selector);
            const button = input ? input.nextElementSibling : null;

            if (input && !input.dataset.tagifyInitialized) {
                const tagify = new Tagify(input, {
                    pattern: pattern,
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
        }

        initTagify('.genresTagify');
        initTagify('.tagsTagify');
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


var picker = new Pikaday({
    field: document.getElementById('date-read'),
    format: 'YYYY MMM D',
    minDate: new Date(2000, 0, 1),
    maxDate: new Date(2029, 11, 31),
    firstDay: 1,
    trigger: document.getElementById('calendar-icon'),
    onSelect: function(date) {
        var dateField = document.getElementById('date-read');
        var dateButton = document.getElementById('date-button');

        //format twice, one for backend, one for text display
        var options = { year: 'numeric', month: 'short', day: 'numeric' };
        var formattedButtonDate = date.toLocaleDateString('en-US', options);

        var year = date.getFullYear();
        var month = (date.getMonth() + 1).toString().padStart(2, '0');
        var day = date.getDate().toString().padStart(2, '0');

        var formattedDate = `${year}-${month}-${day}`;
        dateField.value = formattedDate;
        dateButton.textContent = 'Set to: ' + formattedButtonDate;
        dateButton.style.display = 'block';
        dateButton.setAttribute('hx-vals', JSON.stringify({ date: formattedDate }));
    }
 });

function initLocationTagify() {
    var locationInput = document.querySelector('.locationsTagify');
    if (locationInput && !locationInput.dataset.tagifyInitialized) {
        var tagify = new Tagify(locationInput, {
            delimiters: ";",
            pattern: /^[^;]+$/,
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
            },
            whitelist: [],
            dropdown: {
                enabled: 1,
                maxItems: 10,
                searchKeys: ["value"], // Make sure it searches the right property
                highlightFirst: true
            },
            enforceWhitelist: false,
            skipInvalid: true
        });

        // Listen for when dropdown is about to be shown
        tagify.on('dropdown:show', function(e) {
            console.log('Dropdown show event triggered'); // Debug log
            const value = tagify.state.inputText || '';
            console.log('Current input value:', value); // Debug log

            if (!value || value.length < 1) return;

            console.log('Making fetch request for:', value);

            // Clear previous timeout
            clearTimeout(tagify.searchTimeout);
            tagify.searchTimeout = setTimeout(() => {
                fetch(`/books/locations-suggestions/?q=${encodeURIComponent(value)}`)
                    .then(res => {
                        console.log('Response status:', res.status);
                        return res.json();
                    })
                    .then(suggestions => {
                        console.log('Received suggestions:', suggestions);
                        tagify.whitelist = suggestions;
                        tagify.dropdown.refilter();
                    })
                    .catch(err => console.error("Fetch error:", err));
            }, 100);
        });

        // Also listen to input events for real-time suggestions
        tagify.on('input', function(e) {

            const value = e.detail.value.trim();

            if (value && value.length >= 1) {
                // Trigger dropdown to show, which will fire the dropdown:show event
                setTimeout(() => {
                    tagify.dropdown.show(value);
                }, 50);
            }
        });

        // For editing existing tags
        tagify.on('edit:input', function(e) {

            const value = e.detail.data.newValue?.trim() || '';

            if (value && value.length >= 1) {
                clearTimeout(tagify.editSearchTimeout);
                tagify.editSearchTimeout = setTimeout(() => {
                    fetch(`/books/locations-suggestions/?q=${encodeURIComponent(value)}`)
                        .then(res => res.json())
                        .then(suggestions => {
                            tagify.whitelist = suggestions;
                            tagify.dropdown.show(value);
                        })
                        .catch(err => console.error("Fetch error:", err));
                }, 300);
            }
        });

        locationInput.dataset.tagifyInitialized = "true";

        var addButton = locationInput.nextElementSibling;
        if (addButton) {
            addButton.addEventListener("click", function () {
                tagify.addEmptyTag();
            });
        }
    }
}


 document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "map-overlay") {
        setTimeout(() => {
            initLocationTagify();
        }, 100);

        setTimeout(() => {
            const placeData = window.placeData_json.map(p => ({
              name: p.name,
              value: [p.longitude, p.latitude]  // ✅ convert to correct format
            }));

      if (!placeData) {
        console.error("placeData_json not available yet.");
        return;
      }

      const chart = echarts.init(document.getElementById('locations-map'));
        console.log(placeData);
      fetch(mapPath)
        .then(res => res.json())
        .then(geoJson => {
          echarts.registerMap('myMap', geoJson);

      const lons = placeData.map(p => p.value[0]);
      const lats = placeData.map(p => p.value[1]);

      const minLon = Math.min(...lons);
      const maxLon = Math.max(...lons);
      const minLat = Math.min(...lats);
      const maxLat = Math.max(...lats);

      const centerLon = (minLon + maxLon) / 2;
      const centerLat = (minLat + maxLat) / 2;

      // Estimate zoom level (optional): you can tweak this or use fixed zoom
      const distance = Math.max(maxLon - minLon, maxLat - minLat);
      const zoom = distance < 5 ? 8 : distance < 20 ? 5 : distance < 60 ? 3 : 1.2;

          chart.setOption({
            geo: {
              map: 'myMap',
              roam: true,
              emphasis: false,
              zoom: 1.4,
              center: [centerLon, centerLat],
              zoom: zoom,
            },
            series: [{
              type: 'scatter',
              coordinateSystem: 'geo',
              symbolSize: 10,
              label: {
                show: true,
                formatter: '{b}',
                position: 'right'
              },
              itemStyle: {
                color: 'red'
              },
              data: placeData,
            }]
          });
        });
    }, 200); // short delay
  }
});