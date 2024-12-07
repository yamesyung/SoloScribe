console.log(genres);

function validateForm() {

  var language = document.querySelector('input[name="language"]:checked');
  var genre = document.querySelector('input[name="genre"]:checked');


  if (language && genre) {

    document.getElementById("wordCloudForm").submit();
  } else {

    alert("Please select both language and genre before generating the word cloud.");
  }
}