$(document).ready(function() {

  // Initialize CodeMirror for BibTeX display
  var editor = CodeMirror.fromTextArea(document.getElementById("bibtex"), {
      lineNumbers: false,
      lineWrapping: true,
      readOnly: true
  });

  // Initialize Bootstrap tooltips
  $(function () {
      $('[data-toggle="tooltip"]').tooltip()
  });

});
