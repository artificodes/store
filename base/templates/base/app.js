var spa_links = $('.spa')




// function loadSpaRedirect(spaObject) {
//   // if (spaObject['reload']) {

//     $.ajax({
//       beforeSend: function () {
//         showLoadingBar()
//       },
//       complete: function () {
//         hideLoadingBar()
//       },
//       type: 'get',
//       url: spaObject['url'],
//       data: {
//         'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//       },
//       success: function (response) {
//         if (response.content) {
//           spaObject['content'] = response.content
//           spaObject['title'] = response.title
//           document.title = spaObject['title']

//           app.html(spaObject['content']);
//         }

//       },
//       // async:   false,
//       error: function (xhr, status, error) {
//         alert('there was an error')
//       }
//     });
//   // }
//   // else if (spaObject['content']) {

//   //   document.title = spaObject['title']

//   //   app.html(spaObject['content']);
//   // }

//   // else {
//   //   $.ajax({
//   //     beforeSend: function () {
//   //       showLoadingBar()
//   //     },
//   //     complete: function () {
//   //       hideLoadingBar()
//   //     },
//   //     type: 'get',
//   //     url: spaObject['url'],
//   //     data: {
//   //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//   //     },
//   //     success: function (response) {

//   //       if (response.content) {
//   //         spaObject['content'] = response.content
//   //         spaObject['title'] = response.title
//   //         document.title = spaObject['title']
//   //         app.html(spaObject['content']);

//   //       }

//   //     },
//   //     // async:   false,
//   //     error: function (xhr, status, error) {
//   //       alert('there was an error')
//   //     }
//   //   });
//   // }

// }

// $('.spa').on('click',function(event){
//   // updateLinks()
//   var link = $(this)
//   var url = link.attr('href')
//   if (window.location.hash == url) {
//     Main.refresh();
//   }
//   else {
//     window.location.hash = url;
//   }

// })


// $('.main-bind').on('click',function(event){
//   // updateLinks()
//   var link = $(this)
//   var url = link.attr('href')  

//   Main.get(url, function (context) {
//     loadMain(url)
//     }

//     );
//         Main.routes.get.unshift(Main.routes.get.pop());
//     // spaObject[$(spa_links[index]).attr('href')]['path']=route

//   if (window.location.hash == url) {
//     Main.refresh();
//   }
//   else {
//     window.location.hash = url;
//   }

// })




for (let index = 0; index < spa_links.length; index++) {

  spaObject['#' + $(spa_links[index]).attr('href')] = {}
  spaObject['#' + $(spa_links[index]).attr('href')]['url'] = $(spa_links[index]).attr('href')
  if($(spa_links[index]).attr('href').startsWith('#')){

  }
  else{
  $(spa_links[index]).attr('href', '#' + $(spa_links[index]).attr('href'))

  }
  // alert($(spa_links[index]).attr('href'))
  // spaObject[$(spa_links[index]).attr('href')]['url'] = $(spa_links[index]).attr('href')
  // spaObject[$(spa_links[index]).attr('href')]['href'] =$(spa_links[index]).attr('href')
  // spaObject[$(spa_links[index]).attr('href')]['element'] = $(spa_links[index])
  // spaObject[$(spa_links[index]).attr('href')]['index']=index
  // spaObject[$(spa_links[index]).attr('href')]['href']=spaObject[$(spa_links[index]).attr('href')]['element'].attr('href')

  //   Main.get($(spa_links[index]).attr('href'), function (context) {
  // loadSpa(spaObject[$(spa_links[index]).attr('href')])
  // }

  // );

  // var route = Main.routes.get.pop()
  // Main.routes.get.unshift(route);
  // spaObject[$(spa_links[index]).attr('href')]['path']=route
}






// // var Application = $.sammy(function () {
// //   this.element_selector = '#app';

// // this.get('#/dashboard', function(context) {
// //   $.ajax({
// //     beforeSend: function () {


// //       showLoadingBar()
// //     },
// //     complete: function () {
// //       hideLoadingBar()
// //     },
// //     type: 'get',
// //     url: "{% url 'admin_dashboard' %}",
// //     data: {
// //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
// //     },
// //     success: function (response) {
// //       context.app.swap('');
// //       document.title = response.title
// //       context.$element().append( response.content);
// //     },
// //     // async:   false,
// //     error: function (xhr, status, error) {
// //       alert('there was an error')
// //     }
// //   });
// //   });

// //   for (let index = 0; index < spa_links.length; index++) {
// //     spaObject[$(spa_links[index]).attr('contenturl')] ={}
// //     spaObject[$(spa_links[index]).attr('contenturl')]['element'] = $(spa_links[index])
// //     spaObject[$(spa_links[index]).attr('contenturl')]['index']=index
// //     this.get(spaObject[$(spa_links[index]).attr('contenturl')]['element'].attr('href'), function (context) {
// //       var spal = spal || index
// //       if(spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('reload')){
// //       $.ajax({
// //         beforeSend: function () {
// //           showLoadingBar()
// //         },
// //         complete: function () {
// //           hideLoadingBar()
// //         },
// //         type: 'get',
// //         url: spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('contenturl'),
// //         data: {
// //           'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
// //         },
// //         success: function (response) {
// //           context.app.swap('');
// //           spaObject[$(spa_links[spal]).attr('contenturl')]['content'] = response.content
// //           spaObject[$(spa_links[spal]).attr('contenturl')]['title'] = response.title
// //           document.title = spaObject[$(spa_links[spal]).attr('contenturl')]['title']
// //           context.$element().append(spaObject[$(spa_links[spal]).attr('contenturl')]['content']);
// //         },
// //         // async:   false,
// //         error: function (xhr, status, error) {
// //           alert('there was an error')
// //         }
// //       });
// //     }
// //     else if(spaObject[$(spa_links[spal]).attr('contenturl')]['content']){
// //       context.app.swap('');

// //       context.$element().append( spaObject[$(spa_links[spal]).attr('contenturl')]['content'] )
// //     }

// //     else{
// //       $.ajax({
// //         beforeSend: function () {
// //           showLoadingBar()
// //         },
// //         complete: function () {
// //           hideLoadingBar()
// //         },
// //         type: 'get',
// //         url: spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('contenturl'),
// //         data: {
// //           'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
// //         },
// //         success: function (response) {
// //           context.app.swap('');
// //          spaObject[$(spa_links[spal]).attr('contenturl')]['content'] = response.content
// //          spaObject[$(spa_links[spal]).attr('contenturl')]['title'] = response.title
// //          document.title = spaObject[$(spa_links[spal]).attr('contenturl')]['title']
// //           context.$element().append(spaObject[$(spa_links[spal]).attr('contenturl')]['content']);
// //         },
// //         // async:   false,
// //         error: function (xhr, status, error) {
// //           alert('there was an error')
// //         }
// //       });
// //     }

// //   }

// //  );


// // }
// // }
// // )







// var Application = $.sammy(function () {
//   this.element_selector = '#app';


//     for (let index = 0; index < spa_links.length; index++) {
//       spaObject[$(spa_links[index]).attr('contenturl')] ={}
//       spaObject[$(spa_links[index]).attr('contenturl')]['element'] = $(spa_links[index])
//       spaObject[$(spa_links[index]).attr('contenturl')]['index']=index
//       this.get(spaObject[$(spa_links[index]).attr('contenturl')]['element'].attr('href'), function (context) {
//         var spal = spal || index
//         if(spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('reload')){
//         $.ajax({
//           beforeSend: function () {
//             showLoadingBar()
//           },
//           complete: function () {
//             hideLoadingBar()
//           },
//           type: 'get',
//           url: spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('contenturl'),
//           data: {
//             'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//           },
//           success: function (response) {
//             spaObject[$(spa_links[spal]).attr('contenturl')]['content'] = response.content
//             spaObject[$(spa_links[spal]).attr('contenturl')]['title'] = response.title
//             document.title = spaObject[$(spa_links[spal]).attr('contenturl')]['title']
//             app.html(spaObject[$(spa_links[spal]).attr('contenturl')]['content']);
//           },
//           // async:   false,
//           error: function (xhr, status, error) {
//             alert('there was an error')
//           }
//         });
//       }
//       else if(spaObject[$(spa_links[spal]).attr('contenturl')]['content']){
//         app.html(spaObject[$(spa_links[spal]).attr('contenturl')]['content']);

//       }

//       else{
//         $.ajax({
//           beforeSend: function () {
//             showLoadingBar()
//           },
//           complete: function () {
//             hideLoadingBar()
//           },
//           type: 'get',
//           url: spaObject[$(spa_links[spal]).attr('contenturl')]['element'].attr('contenturl'),
//           data: {
//             'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//           },
//           success: function (response) {

//            spaObject[$(spa_links[spal]).attr('contenturl')]['content'] = response.content
//            spaObject[$(spa_links[spal]).attr('contenturl')]['title'] = response.title
//            document.title = spaObject[$(spa_links[spal]).attr('contenturl')]['title']
//            app.html(spaObject[$(spa_links[spal]).attr('contenturl')]['content']);
//           },
//           // async:   false,
//           error: function (xhr, status, error) {
//             alert('there was an error')
//           }
//         });
//       }

//     }

//    );


//   }
//   // this.get('#/', function(context) {

//   //   $.ajax({
//   //     beforeSend: function () {

//   //       showLoadingBar()
//   //     },
//   //     complete: function () {
//   //       hideLoadingBar()
//   //     },
//   //     type: 'get',
//   //     url: "",
//   //     data: {
//   //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//   //     },
//   //     success: function (response) {
//   //       context.app.swap('');
//   //       document.title = response.title
//   //       context.$element().append(response.content);

//   //     },
//   //     // async:   false,
//   //     error: function (xhr, status, error) {
//   //       alert('there was an error')
//   //     }
//   //   });
//   //   window.location='#/dashboard'

//   //   });


//   // this.post('#/accounts/auth/', function(context) {
//   //   var formInstance = $('#loginform').get(0)
//   //   var form = $('#loginform')
//   //   var post_url = form.attr("contenturl"); //get form action url
//   //     var request_method = form.attr("method"); //get form GET/POST method
//   //     var form_data = new FormData(formInstance); //Creates new FormData object
//   //     $.ajax({
//   //         beforeSend: function () {
//   //             showLoadingBar()
//   //         },
//   //         complete: function () {
//   //             hideLoadingBar()
//   //         },
//   //         url: post_url,
//   //         type: request_method,
//   //         data: form_data,
//   //         contentType: false,
//   //         cache: false,
//   //         processData: false,

//   //         success: function (response) {
//   //           if (response.modal_message) {
//   //             messageModal(response.modal_message, response.heading)

//   //         }
//   //         if (response.modal_notification) {
//   //             notificationModal(response.modal_notification)

//   //         }

//   //         if (response.modal_content) {
//   //             contentModal(response.modal_content, response.heading)

//   //         }
//   //         if (response.message) {
//   //             UIkit.notification.closeAll()
//   //             UIkit.notification(response.message)
//   //         }
//   //         if(response.logged_in){
//   //           context.app.swap('');
//   //           document.title = response.title
//   //           context.$element().append(response.content);
//   //           Application.run();
//   //           window.location='#/dashboard'
//   //         }
//   //         },
//   //         error: function (xhr, status, error) {
//   //             UIkit.notification.closeAll()
//   //             UIkit.notification('Operation not successful. Check your internet connection',)
//   //         }


//   //     }); 
//   // });

//   this.get('#/login', function(context) {
//     $.ajax({
//       beforeSend: function () {
//         showLoadingBar()
//       },
//       complete: function () {
//         hideLoadingBar()
//       },
//       type: 'get',
//       url: "{% url 'account_login' %}",
//       data: {
//         'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//       },
//       success: function (response) {
//         context.app.swap('');
//         document.title = response.title
//         context.$element().append( response.content);
//       },
//       // async:   false,
//       error: function (xhr, status, error) {
//         alert('there was an error')
//       }
//     });
// });
// // this.get('#/dashboard', function(context) {
// //   $.ajax({
// //     beforeSend: function () {
// //       showLoadingBar()
// //     },
// //     complete: function () {
// //       hideLoadingBar()
// //     },
// //     type: 'get',
// //     url: "{% url 'admin_dashboard' %}",
// //     data: {
// //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
// //     },
// //     success: function (response) {
// //       context.app.swap('');
// //       document.title = response.title
// //       context.$element().append( response.content);
// //     },
// //     // async:   false,
// //     error: function (xhr, status, error) {
// //       alert('there was an error')
// //     }
// //   });
// //   });

//   this.post('#/new/accounts/signup/', function(context) {
//     var formInstance = $('#signupform').get(0)
//     var form = $('#signupform')
//     var post_url = form.attr("contenturl"); //get form action url
//       var request_method = form.attr("method"); //get form GET/POST method
//       var form_data = new FormData(formInstance); //Creates new FormData object
//       $.ajax({
//           beforeSend: function () {
//               showLoadingBar()
//           },
//           complete: function () {
//               hideLoadingBar()
//           },
//           url: post_url,
//           type: request_method,
//           data: form_data,
//           contentType: false,
//           cache: false,
//           processData: false,

//           success: function (response) {
//               if (response.invalid) {

//                   function hideAlert() {
//                       $('#signup-error').addClass('uk-animation-slide-top-medium')
//                       $('#signup-error').hide()
//                       $('#signupform').removeClass('uk-animation-slide-top-medium')
//                       $('#signupform').addClass('uk-animation-slide-bottom-medium')

//                   }
//                   if (response.modal_notification) {
//                       $('#signup-error').empty()
//                       $('#signup-error').append(response.modal_notification)
//                       $('#signup-error').show()
//                       setTimeout(hideAlert, 3000)


//                   }
//               }
//               else if (response.logged_in) {
//                Application.run('#'+response.redirecturl)

//               }
//           },
//           error: function (xhr, status, error) {
//               UIkit.notification.closeAll()
//               UIkit.notification('Operation not successful. Check your internet connection',)
//           }
//       }); 
//   });


// }
// )
{% if request.user.is_authenticated %}
// Application.run();

{% else %}
// Application.run('#/login');
{% endif %}


