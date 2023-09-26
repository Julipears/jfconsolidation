// images, css, javascript files go here
// anything that doesn't change
function deleteNote(noteId) {
    // sends post request to delete-note endpoint
  fetch('/delete-note', {
    method: 'POST',
    body: JSON.stringify({noteId: noteId})
  }).then((_res) => {
    window.location.href = '/';
  })
}

function delete_package(pk_id, delete_type = "permanent") {
  // sends post request to delete-note endpoint
fetch('/delete-package', {
  method: 'POST',
  body: JSON.stringify({pk_id: pk_id, delete_type: delete_type})
}).then((_res) => {
  window.location.href = '/';
})
}

function consolidate_package(checked_items) {
  fetch('/consolidate-packages', {
    method: 'POST',
    body: JSON.stringify(checked_items),
  }).then((_res) => {
    console.log('redirect after consolidating');
    window.location.href = '/';
  })
}

function toggleView(elementID) {
  console.log(elementID)
  //var viewForm = document.getElementById("view-form-" + packageId);
  var viewForm = document.getElementById(elementID);
  if (viewForm.style.display === "none") {
    viewForm.style.display = "block";
  } else {
    viewForm.style.display = "none";
  }
}

// allowing only .jf files instead of redirecting to error page
document.getElementById("fileInput").addEventListener("change", validateFile)
function validateFile() {
  const allowedExtension = 'jf';
  const {name:fileName} = this.files[0];
  const fileExtension = fileName.split(".").pop();
  if(!allowedExtension.includes(fileExtension)) {
    alert("File type not allowed. Please upload a .jf file");
    this.value = null;
  }
}

var col1 = document.getElementsByClassName("collapsible-bar");
var i;
for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
