var spa_links = $('.spa')
var spaObject = {}


  var contentObject = {}
  var loader = "<div class=' m-0 uk-position-center loader'> <i class='icon circle notch loading large text-light'></i> </div>"
  var inlineLoader = "<div class=' m-0 uk-position-center loader'> <i class='icon circle notch loading big text-light'></i> </div>"
  function formatCurrency(number) {
    var finalValue = Number(String(number)).toFixed(2)
    if (finalValue == 'NaN') {
      return 0.00

    }
    else {
      var finalValueList = finalValue.split('.')
      var firstdigits = String(number)
      var finalValueNew = []
      counter = 0
      for (let i = firstdigits.length - 1; i >= 0; i--) {
        if (counter % 3 == 0 && firstdigits.length != 3 && counter != 0) {
          finalValueNew.push(firstdigits[i] + ',')
        }
        else {
          finalValueNew.push(firstdigits[i])
        }
        counter++
      }
      return finalValueNew.reverse().join('')

    }
  }

  function addVariationToCart(quantity, productid,variationid,button) {

    $.ajax({
      beforeSend: function () {

        button.append(inlineLoader)
      },
      complete: function () {
        button.find('.loader').remove()
      },
      type: 'post',
      url: "{% url 'customer_add_variation_to_cart' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
        'quantity': quantity,
        'productid': productid,
        'variationid':variationid
      },
      success: function (response) {


        // if (response.notification) {
        //   notify(response.notification)


        // }
        // if(response.loadcontent){
            
        //     loadContent(response.reload_url,'#'+response.container)
        // }

        dispatchResponse(response)
      },
    });

  }

  function addToCart(quantity, productid) {
    $.ajax({
      beforeSend: function () {

        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      type: 'post',
      url: "{% url 'customer_update_cart' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
        'quantity': quantity,
        'productid': productid
      },
      success: function (response) {


        if (response.success_alert) {
          notify(response.success_alert)


        }


      },
    });

  }

  
  // function addVariationToCart(quantity, productid,variationid,button,url) {
  //   $.ajax({
  //     beforeSend: function () {

  //       button.append(loader)
  //     },
  //     complete: function () {
  //       button.find('.loader').remove()
  //     },
  //     type: 'post',
  //     url: url,
  //     data: {
  //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //       'quantity': quantity,
  //       'productid': productid,
  //       'variationid':variationid
  //     },
  //     success: function (response) {


  //       if (response.notification) {
  //         notify(response.notification)


  //       }
  //       if(response.loadcontent){
            
  //           loadContent($('#'+response.container))
  //       }

  //     },
  //   });

  // }

  
  // function addToCart(quantity, productid,url) {
  //   $.ajax({
  //     beforeSend: function () {

  //       showLoadingBar()
  //     },
  //     complete: function () {
  //       hideLoadingBar()
  //     },
  //     type: 'post',
  //     url: url,
  //     data: {
  //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //       'quantity': quantity,
  //       'productid': productid
  //     },
  //     success: function (response) {


  //       if (response.success_alert) {
  //         notify(response.success_alert)


  //       }
  //       if(response.loadcontent){
            
  //         loadContent($('#'+response.container))
  //     }

  //     },
  //   });

  // }

  function dispatchResponse(response){
  closeModal()
  if(response.loadcontent){

    loadContent(response.containers)
}
if (response.modal_message) {
  messageModal(response.modal_message, response.heading)

}
if (response.updatecontent) {
  $(updateable).removeClass('uk-animation-fade')

  $(updateable).addClass('uk-animation-fade')
  $(updateable).empty()
  $(updateable).append(response.updatecontent)
}

if (response.full_modal) {
  fullcontentModal(response.full_modal, response.heading)

}


if (response.notification) {
  notify(response.notification)

}

if (response.modal_content) {
  contentModal(response.modal_content, response.heading)

}
if (response.message) {
  UIkit.notification.closeAll()
  UIkit.notification(response.message)
}
if (response.logout) {
  setTimeout(logout, 5000)
}
if (response.content){
 el.replaceWith(response.content)
}

if (response.redirecturl){
function callRedirect(){
          redirect(response.redirecturl)
        }
        setTimeout(callRedirect,5000)
}

  if(response.reload){
    Main.refresh();
  }
}

  function fadeSuccess() {
    $('#success-alert').fadeToggle()
  }
  
  function notify(message){
    $('#success-alert-inner').empty().append(message)
            $('#success-alert').fadeToggle()
            $('#success-alert').show()
            setTimeout(fadeSuccess, 3000)
  }


  // function loadContent(url, el) {
  //   $.ajax({
  //     beforeSend: function () {
  //       //  alert(contentElement.attr('id'))
  //     },
  //     complete: function () {
  //     },
  //     type: 'get',
  //     url: url,
  //     data: {
  //       'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //     },
  //     success: function (response) {

  //       if (response.content) {
  //         $(el).empty()

  //         $(el).append(response.content);
  //       }


  //     },
  //     error: function (xhr, status, error) {
  //       //   alert('there was an error')
  //     }
  //   });

  // }

  function loadCurrentContent(currentElement){
    $.ajax({
      beforeSend: function () {
          // contentElement.append(inlineLoader)
        },
        complete: function () {
          // contentElement.remove('.loading')
        },
      type: 'get',
      url: currentElement.attr('contenturl'),
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {

        if (response.content) {
          currentElement.empty()

          currentElement.append(response.content);
          currentElement.attr('loaded', '1')
          currentElement.removeClass('load-content')
          updateLinks()
        }

        contentObject[currentElement.attr('identifier')] = {}
        contentObject[currentElement.attr('identifier')]['body'] = response.content


      },
      error: function (xhr, status, error) {
        //   alert('there was an error')
      }
    });
  }
  
  function loadContent(contentElement){
  // if (contentObject[contentElement.attr('identifier')] && contentElement.attr('id')) {
  //   contentElement.empty();
  //   contentElement.append(contentObject[contentElement.attr('identifier')]['body']);
  // }
  // else {
    if(contentElement.length >1){
      for (let i=0;i<contentElement.length;i++) {
        var currentElement = $('#'+contentElement[i])
        loadCurrentContent(currentElement)
     
      
      }
    }
    else{
      var contentElement = $(contentElement)
    
        loadCurrentContent(contentElement)
    }

  

  

  // }

}



  function updateLinks(){
    spa_links = $('.spa')
    for (let index = 0; index < spa_links.length; index++) {
    if($(spa_links[index]).attr('href').startsWith('#')){

  }
  else{
  $(spa_links[index]).attr('href', '#' + $(spa_links[index]).attr('href'))

  }
      }
      }
      
  
function updatePage(){
  updateLinks()
}

function updateElement(el,content){
  updateable = $('#'+el)
  updateable.removeClass('uk-animation-fade')

  updateable.addClass('uk-animation-fade')
  updateable.empty()
  updateable.append(content)
}


  function redirect(url){
    if (window.location.hash == url) {
           
      Main.refresh();
    }
    else {
      window.location.hash = url;
    }
  }


  function appendLoader(el){
    el.append(inlineLoader)
  }
  function removeLoader(el){
    el.remove('.loading')
  }

   $('.load-content').beacon({
     enteronce:true,
     onenter: function (el) {
       var contentElement = $(el)
      loadContent(contentElement)
     }
   });


  var navigationList = []
  var navigationObject = {}

  function closeModal() {

    try {
      


      UIkit.modal($('.uk-open')).hide();

    } catch (TypeError) {

    }
  }


  {
    (function ($) {
      $('.modal-close').on('click', function () {
        setTimeout( UIkit.modal($('.content-modal.uk-open')).hide,350)            //
        

        

      })
    }
      (jQuery))
  };
  function showLoadingBar() {
  
    $('#body-loader').show()
    try {
      clearInterval(intervalObject_1);

    } catch (ReferenceError) {

    }

    $('#progress-container').show()
    try {
      clearInterval(intervalObject_1);

    } catch (ReferenceError) {

    }
    pageStatus = null;
    progress = null;
    animationInterval = 33;
    function updateProgress() {
      if (progress == null) {
        progress = 1;
      }

      progress = progress + 1;
      if (progress >= 0 && progress <= 30) {

        animationInterval += 1;
        $('#progress').progress({
          percent: progress
        });
      }
      else if (progress > 30 && progress <= 60) {
        animationInterval += 2;
        $('#progress').progress({
          percent: progress
        });
      }
      else if (progress > 60 && progress <= 80) {
        $('.progress').addClass('bg-darker')

        animationInterval += 3;
        $('#progress').progress({
          percent: progress
        });
      }
      else if (progress > 80 && progress <= 90) {
        $('.progress').addClass('bg-darker')

        animationInterval += 4;
        $('#progress').progress({
          percent: progress
        });
      }
      else if (progress > 90 && progress <= 95) {
        animationInterval += 80;
        $('#progress').progress({
          percent: progress
        });
      }
      else if (progress > 95 && progress <= 99) {
        animationInterval += 150;
        // document.getElementById("pageLoader").innerHTML = progress;
      }
      else if (progress <= 100) {
        $('#progress').progress({
          percent: progress
        });
      }
      setTimeout(updateProgress, animationInterval);

    }
    intervalObject_1 = setInterval(function () {
      element = document.querySelector("body");

      if (element != undefined) {
        clearInterval(intervalObject_1);

        updateProgress();
      }
    }, 50);
  }

  function hideLoadingBar() {
    $('#body-loader').hide()

    clearInterval(intervalObject_1);
    progress = 100
    $('#progress').progress({
      percent: progress
    });
    $('#progress-container').hide()
    $('.progress').addClass('bg-yello')

    progress = 0
  }


  {
    (function ($) { //Most read async
      $('.coming-soon').on('click', function (event) {

        notificationModal('Coming Soon')


      });
    }(jQuery))
  };

  {
    (function ($) { //Most read async
      $('.signout').on('click', function (event) {
        var link = $(this);

        $.ajax({
          beforeSend: function () {
            showLoadingBar()
          },
          complete: function () {
            hideLoadingBar()

          },
          type: 'get',
          url: link.attr('contenturl'),
          data: {
            'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
          },
          success: function (response) {

            if (response.url) {
              window.location = response.url

            }
            else {
              window.location = ' '
            }
          },
          error: function (xhr, status, error) {
            alert('there was an error')
          }
        });


      });
    }(jQuery))
  };

  {
    (function ($) {
      $('.hide-content').on('click', function () {

        var button = $(this);
        $(button.attr('content')).removeClass('uk-animation-fade')
        $(button.attr('content')).addClass('uk-animation-fade')
        $(button.attr('content')).hide()

      });
    }(jQuery))
  };

  {
    (function ($) {
      $('.main-content-redirect').on('click', function () {

        var link = $(this);

        $.ajax({
          beforeSend: function () {

            showLoadingBar()
          },
          complete: function () {
            hideLoadingBar()
          },
          type: 'get',
          url: link.attr('contenturl'),
          data: {
            'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
          },
          success: function (response) {
            // if there are still more pages to load,
            // add 1 to the "Load More Posts" link's page data attribute
            // else hide the link
            // append html to the posts div
            //$('.content-modal-header-title').empty()

            //$('.content-modal-header-title').append(link.attr('inner-html'));
            if (response.content) {
              window.location - '#top'
              $('#tab-header').empty()
              $('#tab-header').append(response.header);
              $('#inner-container').empty();
              $('#inner-container').append(response.content);

            }

            if (response.message) {
              $('#notification-modal-inner').empty()
              $('#notification-modal-inner').append(response.message)
              $('.content-modal-body').css({ 'background-color': 'white', 'color': 'black' })
              UIkit.modal($('#notification-modal')).show();
            }


          },
        });
      });
    }(jQuery))
  };


  {
    (function ($) {
      $('.remove').on('click', function () {

        var link = $(this);

        $.ajax({
          beforeSend: function () {

            showLoadingBar()
          },
          complete: function () {
            hideLoadingBar()
          },
          type: 'get',
          url: link.attr('contenturl'),
          data: {
            'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
          },
          success: function (response) {


            if (response.message) {
              $('#confirm-modal-inner').empty()
              $('#confirm-modal-inner').append(response.message)

              UIkit.modal($('#confirm-modal')).show();
            }
            if (response.removeurl) {
              $('#yes').attr('contenturl', response.removeurl)
              $('#yes').attr('target', link.attr('target'))
            }




          },
        });
      });
    }(jQuery))
  };

  {
    (function ($) {
      $('#yes').on('click', function () {

        var link = $(this);

        $.ajax({
          beforeSend: function () {

            showLoadingBar()
          },
          complete: function () {
            hideLoadingBar()
          },
          type: 'post',
          url: link.attr('contenturl'),
          data: {
            'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
          },
          success: function (response) {
            hideLoadingBar()

          dispatchResponse(response)


          },
        });
      });
    }(jQuery))
  };


  {
    (function ($) {
      $('.content-btn').on('click', function (event) {
        event.preventDefault()
        // UIkit.offcanvas($('#offcanvas-content')).show();
        var link = $(this);
        requestContentModal(link.attr('contenturl'), 'get')
      })
    }(jQuery))
  }


  function requestContentModal(el,contentUrl, action = 'post', updateable = '') {

    $.ajax({
      beforeSend: function () {
        // if(el){
        // el.append(loader)
        // }
      },
      complete: function () {
        // if(el){
        // el.find('.loader').remove()
        // }

      },
      type: action,
      url: contentUrl,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
dispatchResponse(response)
      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  }

//   function requestContentModal(el,contentUrl, action = 'post', updateable = '') {

//     $.ajax({
//       beforeSend: function () {
//         if(el){
//         el.append(loader)
//         }
//       },
//       complete: function () {
//         if(el){
//         el.find('.loader').remove()
//         }

//       },
//       type: action,
//       url: contentUrl,
//       data: {
//         'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
//       },
//       success: function (response) {
// dispatchResponse(response)
//       },
//       error: function (xhr, status, error) {
//         alert('there was an error')
//       }
//     });
//   }


  function contentModal(body, heading) {
    $('.content-modal-body').css({ 'background-color': 'white', 'color': 'black' })
    $('#content-modal-body').empty()
    $('.content-modal-header').empty()
    $('#content-modal-body').append(body)
    $('.content-modal-header').append(heading)

    UIkit.modal($('#content-modal')).show();
  }

  function messageModal(body) {
    $('.content-modal-body').css({ 'background-color': 'white', 'color': 'black' })
    $('#message-modal-body').empty()
    // $('#message-modal-header').empty()
    $('#message-modal-body').append(body)
    // $('#message-modal-header').append(heading)

    UIkit.modal($('#message-modal')).show();
  }

  function notificationModal(body) {
    $('.content-modal-body').css({ 'background-color': 'white', 'color': 'black' })
    $('#notification-box-body').empty()
    // $('#message-modal-header').empty()
    $('#notification-box-body').append(body)
    // $('#message-modal-header').append(heading)
    UIkit.modal($('#notification-box')).show();
    setTimeout(() => UIkit.modal($('#notification-box')).hide(), 3000)
  }

  function fullcontentModal(body, heading) {
    $('.content-modal-body').css({ 'background-color': 'white', 'color': 'black' })
    $('#full-content-modal-body').empty()
    $('#full-content-modal-header').empty()
    $('#full-content-modal-body').append(body)
    $('#full-content-modal-header').append(heading)

    UIkit.modal($('#full-content-modal')).show();
  }

  function logout() {
    $.ajax({

      beforeSend: function () {

        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      type: 'get',
      url: "{% url 'admin_logout' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
        window.location = '{% url 'admin_login' %}'
        loggedOut = true
      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  };
  var loggedOut = false

  jQuery(window).resize(function () {
    if (jQuery(window).width() < 992) {
      UIkit.offcanvas($('#offcanvas-nav-primary')).hide();
      $('#major').css('margin-left', '0px')
      $('.content-modal').addClass('uk-modal-full')
      $('.content-modal .uk-modal-dialog').removeClass('uk-margin-auto-vertical')
      $('.content-modal .uk-modal-dialog').removeClass('rounded-sm')
      $('.content-modal').addClass('bg-white')
      $('.mobile').removeClass('hide')
    }
    else {
      UIkit.offcanvas($('#offcanvas-nav-primary')).hide();
    
      // $('#major').css('margin-left', $('.uk-offcanvas-bar').css('width'))
      $('.content-modal').removeClass('uk-modal-full')
      $('.content-modal .uk-modal-dialog').addClass('uk-margin-auto-vertical')
      $('.content-modal .uk-modal-dialog').addClass('rounded-sm')
      $('.content-modal').removeClass('bg-white')
      $('.desktop').addClass('hide')

    }
  });

