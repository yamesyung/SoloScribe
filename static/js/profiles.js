//switch focus to password field
document.body.addEventListener("htmx:afterSwap", function(evt) {

  if (evt.detail.target.id === "profile-form") {
    let pwField = evt.detail.target.querySelector('input[name="password"]');
    if (pwField) {
      pwField.focus();
    }
  }
});