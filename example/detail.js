var setup = function () {
  document.getElementById('clickme').onclick = function () {
    document.getElementById('content').innerHTML += "<div class='bloop'>HI</div>\n";
  }
}

window.onload = setup;
