
tinymce.init({
    selector: 'textarea',
    height: 200,
    width:'100%',
    menubar: false,
    plugins: [
      'advlist autolink lists charmap print preview anchor',
      'searchreplace visualblocks fullscreen',
      'insertdatetime paste code help wordcount'
    ],
    toolbar: 'undo redo | formatselect | ' +
    'bold italic backcolor | alignleft aligncenter ' +
    'alignright alignjustify | bullist numlist outdent indent | ' +
    'removeformat | help',
    content_css: '//www.tiny.cloud/css/codepen.min.css'
  });
  
  
  