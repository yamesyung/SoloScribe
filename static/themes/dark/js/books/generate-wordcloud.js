console.log(wordFreqs);

let wordFreqsCopy = JSON.parse(JSON.stringify(wordFreqs));

function calculateWeightFactor(wordFreqs) {

  if (wordFreqs.length > 0) {
    var maxFrequency = wordFreqs[0][1]; // Assuming the array is sorted by frequency
    return Math.ceil(120 / maxFrequency); // Round the result
  } else {
    return 1; // Default weight factor
  }
}

var weightFactor = calculateWeightFactor(wordFreqs);

var weightFactorInput = document.getElementById('weightFactorRange');
weightFactorInput.value = weightFactor;
const magnificationValue = document.getElementById('magnificationValue');
magnificationValue.textContent = weightFactor;

document.addEventListener("DOMContentLoaded", (event) => {
  WordCloud(document.getElementById('wordCanvas'),  {
  list: wordFreqs,
  weightFactor: weightFactor,
  drawOutOfBound: false,
  shrinkToFit: true,
  ellipticity: 0.8,
  shuffle: 1,
  });
});

function updateCoordinates() {
  const canvas = document.getElementById('wordCanvas');
  const originSelect = document.getElementById('origin');

  const canvasRect = canvas.getBoundingClientRect();
  let x, y;

  switch (originSelect.value) {
    case 'middle':
      x = canvasRect.width / 2;
      y = canvasRect.height / 2;
      break;
    case 'top-left':
      x = 0;
      y = 0;
      break;
    case 'top-center':
      x = canvasRect.width / 2;
      y = 0;
      break;
    case 'top-right':
      x = canvasRect.width;
      y = 0;
      break;
    case 'middle-left':
      x = 0;
      y = canvasRect.height / 2;
      break;
    case 'middle-right':
      x = canvasRect.width;
      y = canvasRect.height / 2;
      break;
    case 'bottom-left':
      x = 0;
      y = canvasRect.height;
      break;
    case 'bottom-center':
      x = canvasRect.width / 2;
      y = canvasRect.height;
      break;
    case 'bottom-right':
      x = canvasRect.width;
      y = canvasRect.height;
      break;
    default:
      x = canvasRect.width / 2;
      y = canvasRect.height / 2;
  }

  return [x,y];
}

function handleColorCountChange(count) {
      // Hide all color containers
      document.querySelectorAll('.color-container').forEach(container => {
        container.style.display = 'none';
      });

      // Show color containers based on the selected count
      for (let i = 1; i <= count; i++) {
        document.getElementById(`colorContainer${i}`).style.display = 'block';
      }
}

const drawCanvasButton = document.getElementById("redrawButton");
const canvasDiv = document.getElementById('wordCanvas');

const widthSlider = document.getElementById('widthSlider');
const widthValue = document.getElementById('widthValue');

widthSlider.addEventListener('input', function() {
    const newSize = widthSlider.value;
    widthValue.textContent = newSize;
});

const heightSlider = document.getElementById('heightSlider');
const heightValue = document.getElementById('heightValue');

heightSlider.addEventListener('input', function() {
    const newSize = heightSlider.value;
    heightValue.textContent = newSize;
});

const magnificationSlider = document.getElementById('weightFactorRange');


magnificationSlider.addEventListener('input', function() {
    const newSize = magnificationSlider.value;
    magnificationValue.textContent = newSize;
});

function colorWords() {
  const colorsNumber = document.getElementById('colorCount').value;
  const colorList = [];

  for (let i = 0; i < colorsNumber; i++) {
    // Assume you have an input field for each color with class 'colorInput'
    const colorInput = document.getElementById(`colorInput${i + 1}`);
    colorList.push(colorInput.value);
  }

  // Generate a random index within the range of colorList length
  const randomIndex = Math.floor(Math.random() * colorList.length);

  // Return the randomly selected color
  return colorList[randomIndex];
}

const wordFreqsShuffled = [...wordFreqs];

drawCanvasButton.addEventListener("click", function() {

  canvasDiv.style.width = widthSlider.value + 'px';
  canvasDiv.style.height = heightSlider.value + 'px';

  const gridSizeOption = document.getElementById("gridSizeRange").value;
  const cloudShape = document.getElementById("shapes").value;
  const ellipticityOption = document.getElementById("ellipticityRange").value;
  const weightFactorOption = document.getElementById("weightFactorRange").value;
  const backgroundColorOptions = document.getElementById("backgroundColor").value;
  const colorOptions = document.getElementById("colors").value;
  const colorsNumber = document.getElementById('colorCount').value;
  const randomizeOrder = document.getElementById("randOrder");


  filterInvalidEntries();
  wordFreqs.sort((a, b) => b[1] - a[1]);

  const wordCloudConfig = {
    list: wordFreqs,
    gridSize: gridSizeOption,
    clearCanvas: true,
    shape: cloudShape,
    ellipticity: ellipticityOption,
    weightFactor: weightFactorOption,
    backgroundColor: backgroundColorOptions,
    drawOutOfBound: false,
    color: colorWords,
    origin: updateCoordinates(),
    shuffle: true,
  };

  if (colorsNumber == 0) {
    wordCloudConfig.color = colorOptions;
    }
  if (randomizeOrder.checked == true) {
     wordFreqsShuffled.sort(() => Math.random() - 0.5);
     wordCloudConfig.list = wordFreqsShuffled;
 }


  WordCloud(document.getElementById('wordCanvas'), wordCloudConfig);
});


document.getElementById('downloadBtn').addEventListener('click', function() {
    // Get the target div
    var targetDiv = document.getElementById('wordCanvas');

    // Use html2canvas to capture the content of the div
    html2canvas(targetDiv).then(function(canvas) {
      // Convert the canvas to a data URL
      var dataURL = canvas.toDataURL('image/png');

      // Create a temporary link element
      var link = document.createElement('a');

      // Set the download attribute with a filename for the image
      link.download = 'wordcloud.png';

      // Set the href attribute with the data URL
      link.href = dataURL;

      // Append the link to the document and trigger a click to start the download
      document.body.appendChild(link);
      link.click();

      // Remove the link from the document
      document.body.removeChild(link);
    });
  });


// Toggle collapsible sections
document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
        const collapseSection = document.getElementById(button.dataset.toggle);
        collapseSection.classList.toggle('show');
    });
});

// Show/hide custom color inputs based on selection
function handleColorCountChange(value) {
    const colorContainers = document.querySelectorAll(".color-container");
    colorContainers.forEach((container, index) => {
        container.style.display = index < value ? "flex" : "none";
    });
}
handleColorCountChange(document.getElementById('colorCount').value);

const editBtn = document.getElementById('editBtn');
const editModal = document.getElementById('editModal');
const wordListContainer = document.getElementById('wordListContainer');
const saveChangesBtn = document.getElementById('saveChangesBtn');
const closeModalBtn = document.getElementById('closeModalBtn');


editBtn.addEventListener('click', () => {
    // Populate modal with word frequency inputs
    wordListContainer.innerHTML = '';
    wordFreqs.forEach((item, index) => {
        const wordInput = document.createElement('input');
        wordInput.type = 'text';
        wordInput.value = item[0];
        wordInput.id = `word-${index}`;

        const freqInput = document.createElement('input');
        freqInput.type = 'number';
        freqInput.value = item[1];
        freqInput.id = `freq-${index}`;

        wordListContainer.appendChild(wordInput);
        wordListContainer.appendChild(freqInput);
        wordListContainer.appendChild(document.createElement('br'));
    });

    editModal.style.display = 'block';
});

// Save changes and close modal
saveChangesBtn.addEventListener('click', () => {
    wordFreqs.forEach((item, index) => {
        const newWord = document.getElementById(`word-${index}`).value;
        const newFreq = parseInt(document.getElementById(`freq-${index}`).value, 10);
        item[0] = newWord;
        item[1] = newFreq;
    });
    console.log(wordFreqs);
    editModal.style.display = 'none';
});

// load original word list and close modal
restoreChangesBtn.addEventListener('click', () => {
    wordFreqs = JSON.parse(JSON.stringify(wordFreqsCopy));

    editModal.style.display = 'none';
});

function filterInvalidEntries() {
    // Filter out entries where word is empty or frequency is NaN or not a number
    wordFreqs = wordFreqs.filter(([word, freq]) => word !== '' && !isNaN(freq) && freq > 0);
}

closeModalBtn.addEventListener('click', () => {
    editModal.style.display = 'none';
});

document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
     editModal.style.display = 'none';
  }
});