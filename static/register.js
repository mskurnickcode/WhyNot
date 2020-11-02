var check = function() {
  if (document.getElementById('password').value ==
    document.getElementById('passwordVerify').value) {
    document.getElementById('password_message').style.color = 'green';
    document.getElementById('password_message').innerHTML = 'Password Match';
  } else {
    document.getElementById('password_message').style.color = 'red';
    document.getElementById('password_message').innerHTML = 'Not Matching';
  }
}
