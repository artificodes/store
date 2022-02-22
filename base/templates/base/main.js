{% if request.user.is_authenticated and  request.user.is_superuser %}
var loggedIn = true
{% else %}
var loggedIn = false

{% endif %}
allRoutes = []
newSpaUrls = []
existingUrls = []
var splat = ''
var main = $('#main')
var nextUrl = '#/'
var app = false


function loadSpaRedirect(spaObject) {

    if(app){
      fetchAppContent(spaObject['splat'])
    } 
    else {
      $.ajax({
        beforeSend: function () {
          showLoadingBar()
        },
        complete: function () {
          hideLoadingBar()
          
        },
        type: 'get',
        url: "{% url 'admin_app' %}",
        data: {
          'csrfmiddlewaretoken': window.CSRF_TOKEN,
          'next':splat,// from index.html
        },
        success: function (response) {
          reloadApp(spaObject[splat],response)
  
        },
        // async:   false,
        error: function (xhr, status, error) {
          alert('there was an error')
        }
      });
    }




    // $.ajax({
    //   beforeSend: function () {
    //     showLoadingBar()
    //   },
    //   complete: function () {
    //     hideLoadingBar()
    //   },
    //   type: 'get',
    //   url: spaObject['url'],
    //   data: {
    //     'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
    //   },
    //   success: function (response) {
    //     if (response.content) {
    //       spaObject['content'] = response.content
    //       spaObject['title'] = response.title
    //       document.title = spaObject['title']

    //       app.html(spaObject['content']);
    //     }

    //   },
    //   // async:   false,
    //   error: function (xhr, status, error) {
    //     alert('there was an error')
    //   }
    // });
  }
var Main = $.sammy(function () {
  this.element_selector = '#main';

  this.get('#/', function (context) {

    $.ajax({
      beforeSend: function () {

        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      type: 'get',
      url: "{% url 'app' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
        context.app.swap('');
        document.title = response.title
        context.$element().append(response.content);
        window.location = '#/'+response.nexturl
        // reloadApp(response)

      },
      // async:   false,
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });

  });


  this.post('#/accounts/auth/', function (context) {
    var formInstance = $('#loginform').get(0)
    var form = $('#loginform')
    var post_url = form.attr("contenturl"); //get form action url
    var request_method = form.attr("method"); //get form GET/POST method
    var form_data = new FormData(formInstance); //Creates new FormData object
    $.ajax({
      beforeSend: function () {
        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      url: post_url,
      type: request_method,
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,

      success: function (response) {
        if (response.modal_message) {
          messageModal(response.modal_message, response.heading)

        }
        if (response.modal_notification) {
          notificationModal(response.modal_notification)

        }

        if (response.modal_content) {
          contentModal(response.modal_content, response.heading)

        }
        if (response.message) {
          UIkit.notification.closeAll()
          UIkit.notification(response.message)
        }
        if (response.logged_in) {
          loggedIn = true
          window.location = nextUrl
          // context.app.swap('');
          // document.title = response.title
          // context.$element().append(response.content);
        }
      },
      error: function (xhr, status, error) {
        UIkit.notification.closeAll()
        UIkit.notification('Operation not successful. Check your internet connection',)
      }


    });
  });

  // this.get('#/dashboard', function(context) {
  //   try {
  //       app = app
  //       $.ajax({
  //         beforeSend: function () {
  //           try {

  //           } catch (error) {

  //           }
  //           showLoadingBar()
  //         },
  //         complete: function () {
  //           hideLoadingBar()
  //         },
  //         type: 'get',
  //         url: "{% url 'admin_dashboard' %}",
  //         data: {
  //           'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //         },
  //         success: function (response) {

  //         document.title = response.title
  //         app.html(response.content);

  //         },
  //         // async:   false,
  //         error: function (xhr, status, error) {
  //           alert('there was an error')
  //         }
  //       });
  //     } catch (ReferenceError) {
  //       window.location ='#/'
  //       // window.location ='#/dashboard'
  //     }

  //   });



  // this.get('#/login', function (context) {
  //   $.ajax({
  //     beforeSend: function () {
  //       showLoadingBar()
  //     },
  //     complete: function () {
  //       hideLoadingBar()
  //     },
  //     type: 'get',
  //     url: "{% url 'account_login' %}",
  //     data: {
  //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //     },
  //     success: function (response) {
  //       context.app.swap('');
  //       document.title = response.title
  //       context.$element().append(response.content);
  //     },
  //     // async:   false,
  //     error: function (xhr, status, error) {
  //       alert('there was an error')
  //     }
  //   });
  // });

  this.post('#/admin/new/accounts/signup/', function (context) {
    var formInstance = $('#signupform').get(0)
    var form = $('#signupform')
    var post_url = form.attr("contenturl"); //get form action url
    var request_method = form.attr("method"); //get form GET/POST method
    var form_data = new FormData(formInstance); //Creates new FormData object
    $.ajax({
      beforeSend: function () {
        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      url: post_url,
      type: request_method,
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,

      success: function (response) {
        if (response.invalid) {

          function hideAlert() {
            $('#signup-error').addClass('uk-animation-slide-top-medium')
            $('#signup-error').hide()
            $('#signupform').removeClass('uk-animation-slide-top-medium')
            $('#signupform').addClass('uk-animation-slide-bottom-medium')

          }
          if (response.modal_notification) {
            $('#signup-error').empty()
            $('#signup-error').append(response.modal_notification)
            $('#signup-error').show()
            setTimeout(hideAlert, 3000)


          }
        }
        else if (response.logged_in) {
          loggedIn = true
          loadApp(Main)
          window.location = '#' + response.redirecturl
          // jQuery.each(Main.routes, function (verb, routes) {
          //   jQuery.each(routes, function (i, route) {
          //     allRoutes.push(Object.entries(route));
          //   });
          // });
          // jQuery.each(spaObject, function (href, Obj) {
          //   // alert(href)
          //   existingUrls.push(Obj['splat'])

          //     ;
          // });

          // if (url in existingUrls) {
          //   if (window.location.hash == url) {
          //     Main.refresh();
          //   }
          //   else {
          //     window.location.hash = url;
          //   }
          // }

          // else {
          //   newSpaUrls.push(url);
          //   spaObject[url] = {}
          //   spaObject[url]['url'] = '/' + splat
          //   spaObject[splat]['url'] = url
          //   Main.get(spaObject[splat]['url'], function (context) {
          //     loadSpa(spaObject[url])
          //   })

          //   Main.routes.get.unshift(Main.routes.get.pop());
          //   if (window.location.hash == url) {
          //     Main.refresh();
          //   }
          //   else {
          //     window.location.hash = url;
          //   }
          // }
        }
      },
      error: function (xhr, status, error) {
        UIkit.notification.closeAll()
        UIkit.notification('Operation not successful. Check your internet connection',)
      }
    });
  });


  this.get(/\#\/(.*)/, function (context) {
    var splat = '/'+this.params['splat'].join('/')
    spaObject[splat] = {}
    spaObject[splat]['splat'] = ''
    spaObject[splat]['url'] = ''
    spaObject[splat]['href'] = ''
    spaObject[splat]['splat'] = splat
// if(splat == 'login'){
//   jQuery.each(this.params, function (key, value) {
//     if (key == 'splat' || !key) {
//       return false
//     }
//     // elif()
//     else {
//       spaObject[splat]['query'] += key + '=' + value + '&'
//     }
//   });
//   spaObject[splat]['query'] = '?' + spaObject[splat]['query'] 
//   spaObject[splat]['query'] = spaObject[splat]['query'].split('&')
//   spaObject[splat]['query'].pop()
  
//   spaObject[splat]['query'] = spaObject[splat]['query'].join('&')


//     spaObject[splat]['url'] = splat
//     // alert(spaObject[splat]['url'])

  
//   spaObject[splat]['href'] = '#/' + spaObject[splat]['url']
//   Main.get(spaObject[splat]['href'], function (context) {
//     loadApp(spaObject[splat])
//   })
// }

// else{
      // var query=''
    // for(key in this.params){
    //  alert(key)
    // }
    // alert(this.params.keys());
    // 
    // alert(parameters)

      spaObject[splat]['url'] = splat
      // alert(spaObject[splat]['url'])

    
    spaObject[splat]['href'] = '#' + spaObject[splat]['url']
    Main.get(spaObject[splat]['href'], function (context) {
      loadApp(spaObject[splat])
    })
    // if (loggedIn) {
    //   //  alert('in')
    //   if (spaObject[splat]['url'] == 'login' || spaObject[splat]['url'] == 'logout') {
    //     loadMain('/' + spaObject[splat]['url'])
    //   }
      
    //   else {
        // try {
        //   app = app
          jQuery.each(Main.routes, function (verb, routes) {
            jQuery.each(routes, function (i, route) {
              allRoutes.push(Object.entries(route));
            });
          });
          jQuery.each(spaObject, function (href, Obj) {
            existingUrls.push(Obj['splat'])
            
              ;
          });

          if (spaObject[splat]['splat'] in existingUrls) {
            if (window.location.hash == spaObject[splat]['href']) {
              Main.refresh();
            }
            else {
              window.location.hash = spaObject[splat]['href'];
            }
          }

          else {
            Main.get(spaObject[splat]['href'], function (context) {
              loadSpa(spaObject[splat])
            })

            Main.routes.get.unshift(Main.routes.get.pop());
            if (window.location.hash == spaObject[splat]['href']) {
              Main.refresh();
            }
            else {
              window.location.hash = spaObject[splat]['href'];
            }
          }


        // }
        //  catch (ReferenceError) {
        //   loadApp(spaObject[splat]['splat'])
          

        // }
      // }
    // }
    // else if (spaObject[splat]['url'] == 'login') {
    //   // alert(spaObject[splat]['url'])


    //   jQuery.each(Main.routes, function (verb, routes) {
    //     jQuery.each(routes, function (i, route) {
    //       allRoutes.push(Object.entries(route));
    //     });
    //   });
    //   jQuery.each(spaObject, function (href, Obj) {
    //     // alert(href)
    //     existingUrls.push(Obj['splat'])

    //       ;
    //   });

    //   if (spaObject[splat]['splat'] in existingUrls) {
    //     if (window.location.hash == spaObject[splat]['href']) {
    //       Main.refresh();
    //     }
    //     else {
    //       window.location.hash = spaObject[splat]['href'];
    //     }
    //   }

    //   else {
    //     // newSpaUrls.push(url);

    //     Main.get(spaObject[splat]['href'], function (context) {
    //       loadMain(spaObject[splat]['url'])
    //     })

    //     Main.routes.get.unshift(Main.routes.get.pop());
    //     if (window.location.hash == spaObject[splat]['href']) {
    //       Main.refresh();
    //     }
    //     else {
    //       window.location.hash = spaObject[splat]['href'];
    //     }
    //   }


    // }
    // else {
    //   nextUrl = spaObject[splat]['href']
    //   window.location = '#/login?next=' + spaObject[splat]['url']


    //   jQuery.each(Main.routes, function (verb, routes) {
    //     jQuery.each(routes, function (i, route) {
    //       allRoutes.push(Object.entries(route));
    //     });
    //   });
    //   jQuery.each(spaObject, function (href, Obj) {
    //     // alert(href)
    //     existingUrls.push(Obj['splat'])

    //       ;
    //   });

    //   if (spaObject[splat]['splat'] in existingUrls) {
    //     if (window.location.hash == spaObject[splat]['href']) {
    //       Main.refresh();
    //     }
    //     else {
    //       window.location.hash = spaObject[splat]['href'];
    //     }
    //   }

    //   else {
    //     newSpaUrls.push(url);

    //     Main.get('#/login', function (context) {
    //       loadMain('/login')
    //     })

    //     Main.routes.get.unshift(Main.routes.get.pop());
    //     loadMain('/login')
    //   }

    // }
// }

  }


  );


}
)



function loadSpa(spaObject) {
  $.ajax({
    beforeSend: function () {
      showLoadingBar()

    },
    complete: function () {
      hideLoadingBar()
    },
    type: 'get',
    url: spaObject['url'],
    data: {
      'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
    },
    success: function (response) {
      // alert('')
      // document.title = response.title
      // app.html(response.content);
    // alert(spaObject['url'])
      if (response.login || response.signup){
        nextUrl =response.nexturl || spaObject['splat']
        // alert(nextUrl)
        app = false
        if(response.login){

        if (window.history.replaceState) {
          window.history.replaceState(window.location.hash, document.title,  '#/admin/login?next=' + nextUrl);
       }
        // window.location = '#/login?next=' + spaObject['url']
        
      }
      else if(response.signup){
        if (window.history.replaceState) {
          window.history.replaceState(window.location.hash, document.title,  '#/admin/signup?next=' + nextUrl);
       }
      }
      Main.swap('');
            document.title = response.title
        Main.$element().append(response.content)
    }
      else{

        if (response.redirecturl) {
          splat = response.redirecturl
          spaObject[splat] = {}
          spaObject[splat]['splat'] = ''
          spaObject[splat]['url'] = ''
          spaObject[splat]['href'] = ''
          spaObject[splat]['splat'] = splat
          spaObject[splat]['url'] = splat
          // alert(spaObject[splat]['url'])
    
        
        spaObject[splat]['href'] = '#' + spaObject[splat]['url']
        Main.get(spaObject[splat]['href'], function (context) {
          loadSpaRedirect(spaObject[splat])
  
        })
          Main.routes.get.unshift(Main.routes.get.pop());
      
      
          if (window.location.hash == '#' + response.redirecturl) {
      
            Main.refresh();
          }
          else {
            window.location.hash = '#' + response.redirecturl;
          }
      
        }
        else if (response.content) {
          spaObject['content'] = response.content
          spaObject['title'] = response.title
          document.title = response.title
          if (response.page) {
            $('#page').html(response.page)
          }
          else {
            $('#page').html('')
          }
          // alert('papp')
          if(app){
          app.html(response.content);
          // fetchAppContent(spaObject['splat'])
          }
          else{
            loadApp(spaObject['splat'])

          }
        }
      }
    },
    // async:   false,
    error: function (xhr, status, error) {
      alert('there was an error')
    }
  });
}

function fetchAppContent(splat) {
  $.ajax({
    beforeSend: function () {
      showLoadingBar()
    },
    complete: function () {
      hideLoadingBar()
    },
    type: 'get',
    url: spaObject[splat]['url'],
    data: {
      'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
    },
    success: function (response) {
      document.title = response.title
      app.html(response.content);

    },
    // async:   false,
    error: function (xhr, status, error) {
      alert('there was an error')
    }
  });
}
function loadApp(splat) {
  try {
      spaObject[splat]['splat']

  } catch (TypeError) {

    spaObject[splat] = {}
    spaObject[splat]['splat'] = ''
    spaObject[splat]['url'] = ''
    spaObject[splat]['href'] = ''
    spaObject[splat]['splat'] = splat

      spaObject[splat]['url'] = splat
      // alert(spaObject[splat]['url'])

    
    spaObject[splat]['href'] = '#' + spaObject[splat]['url']
    Main.get(spaObject[splat]['href'], function (context) {
      loadApp(spaObject[splat])
    })
  }
  if(app){
    fetchAppContent(splat)
  } 
  else {
    $.ajax({
      beforeSend: function () {
        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
        
      },
      type: 'get',
      url: "{% url 'admin_app' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN,
        'next':splat,// from index.html
      },
      success: function (response) {
        reloadApp(spaObject[splat],response)

      },
      // async:   false,
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  }

}

function loadMain(spaObject,response) {

      if (response.redirecturl) {
        alert(response.redirecturl)
        splat = response.redirecturl
        spaObject[splat] = {}
        spaObject[splat]['splat'] = ''
        spaObject[splat]['url'] = ''
        spaObject[splat]['href'] = ''
        spaObject[splat]['splat'] = splat
        spaObject[splat]['url'] = splat
        // alert(spaObject[splat]['url'])
  
      
      spaObject[splat]['href'] = '#' + spaObject[splat]['url']
      Main.get(spaObject[splat]['href'], function (context) {
        loadSpaRedirect(spaObject[splat])

      })
       
        Main.routes.get.unshift(Main.routes.get.pop());


        if (window.location.hash == url) {

          Main.refresh();
        }
        else {
          window.location.hash = url;
        }

      }
      else if (response.content) {
        main.html(response.content);

      
      }
}




function reloadApp(spaObject, response) {
  spa_links = $('.spa')
  if (response.login || response.signup){
    nextUrl =response.nexturl || spaObject['splat']
    // alert(nextUrl)
    app = false
    if(response.login){

    if (window.history.replaceState) {
      window.history.replaceState(window.location.hash, document.title,  '#/admin/login?next=' + nextUrl);
   }
    // window.location = '#/login?next=' + spaObject['url']
    
  }
  else if(response.signup){
    if (window.history.replaceState) {
      window.history.replaceState(window.location.hash, document.title,  '#/admin/signup?next=' + nextUrl);
   }
  }
  Main.swap('');
        document.title = response.title
    Main.$element().append(response.content)
}
  else{
    if (response.redirecturl) {
      
      splat = response.redirecturl
      spaObject[splat] = {}
      spaObject[splat]['splat'] = ''
      spaObject[splat]['url'] = ''
      spaObject[splat]['href'] = ''
      spaObject[splat]['splat'] = splat
      spaObject[splat]['url'] = splat
      // alert(spaObject[splat]['url'])

    
    spaObject[splat]['href'] = '#' + spaObject[splat]['url']
    Main.get(spaObject[splat]['href'], function (context) {
      loadSpaRedirect(spaObject[splat])

    })
      Main.routes.get.unshift(Main.routes.get.pop());
  
  
      if (window.location.hash == '#' + response.redirecturl) {
  
        Main.refresh();
      }
      else {
        window.location.hash = '#' + response.redirecturl;
      }
  
    }
    else if (response.content) {
      // spaObject['content'] = response.content
      // spaObject['title'] = response.title
      document.title = response.title
      if (response.page) {
        $('#page').html(response.page)
      }
      else {
        $('#page').html('')
      }
      main.html(response.content);
      if (window.location.hash == spaObject['href']) {
  
        Main.refresh();
      }
      else {
        window.location.hash = spaObject['href'];
      }
      fetchAppContent(spaObject['splat'])
  
    }
  }

}




Main.run('#/');


// Main.run()

