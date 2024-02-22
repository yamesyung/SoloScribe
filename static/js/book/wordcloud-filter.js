console.log(genres);

function validateForm() {
  // Get selected language and genre
  var language = document.querySelector('input[name="language"]:checked');
  var genre = document.querySelector('input[name="genre"]:checked');

  // Check if both language and genre are selected
  if (language && genre) {
    // If both are selected, submit the form
    document.getElementById("wordCloudForm").submit();
  } else {
    // If either language or genre is not selected, show an alert or perform other validation actions
    alert("Please select both language and genre before generating the word cloud.");
  }
}