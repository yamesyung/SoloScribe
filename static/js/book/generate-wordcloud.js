console.log(wordFreqs);

function calculateWeightFactor(wordFreqs) {

  if (wordFreqs.length > 0) {
    var maxFrequency = wordFreqs[0][1]; // Assuming the array is sorted by frequency
    return Math.ceil(120 / maxFrequency); // Round the result
  } else {
    return 1; // Default weight factor
  }
}

var weightFactor = calculateWeightFactor(wordFreqs);

document.addEventListener("DOMContentLoaded", (event) => {
  WordCloud(document.getElementById('wordCanvas'),  {list: wordFreqs, weightFactor: weightFactor, drawOutOfBound: false, shrinkToFit: true, wait: 50}  );
});
