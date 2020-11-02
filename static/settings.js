function htmlUpdate () {
  link = document.getElementById("update");
  input = document.getElementById("new_username").value;

  link.setAttribute("action", "/update/"+input)

        console.log(link);
}

window.onchange = htmlUpdate


function tripName () {
  button = document.getElementById("submit_button");
  input = document.getElementById("new_username");

  if (input.value === "") {
    button.disabled = true;
  } else {
    button.disabled = false;
  }
}
window.onload = tripName
window.oninput = tripName