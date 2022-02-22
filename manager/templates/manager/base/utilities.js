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

  
  function addVariationToCart(quantity, productid,variationid,button,url) {
    $.ajax({
      beforeSend: function () {

        button.append(loader)
      },
      complete: function () {
        button.find('.loader').remove()
      },
      type: 'post',
      url: url,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
        'quantity': quantity,
        'productid': productid,
        'variationid':variationid
      },
      success: function (response) {


        if (response.notification) {
          notify(response.notification)


        }
        if(response.loadcontent){
            
            loadContent($('#'+response.container))
        }

      },
    });

  }

  
  function addToCart(quantity, productid,url) {
    $.ajax({
      beforeSend: function () {

        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      type: 'post',
      url: url,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
        'quantity': quantity,
        'productid': productid
      },
      success: function (response) {


        if (response.success_alert) {
          notify(response.success_alert)


        }
        if(response.loadcontent){
            
          loadContent($('#'+response.container))
      }

      },
    });

  }

  function dispatchResponse(response){
  closeModal()
  if (response.redirecturl){
    function callRedirect(){
              redirect(response.redirecturl)
            }
            setTimeout(callRedirect,3000)
   }
  if (response.modal_message) {
    messageModal(response.modal_message, response.heading)

  }
  if(response.updatecontent){
    updateElement(response.container, response.updatecontent)
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

  
  function loadContent(contentElement){
  // if (contentObject[contentElement.attr('identifier')] && contentElement.attr('id')) {
  //   contentElement.empty();
  //   contentElement.append(contentObject[contentElement.attr('identifier')]['body']);
  // }
  // else {
   
  
  
  $.ajax({
      beforeSend: function () {
          contentElement.append(inlineLoader)
        },
        complete: function () {
          contentElement.remove('.loading')
        },
      type: 'get',
      url: contentElement.attr('contenturl'),
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {

        if (response.content) {
          contentElement.empty()

          contentElement.append(response.content);
          contentElement.attr('loaded', '1')
          contentElement.removeClass('load-content')
          updateLinks()
        }

        contentObject[contentElement.attr('identifier')] = {}
        contentObject[contentElement.attr('identifier')]['body'] = response.content


      },
      error: function (xhr, status, error) {
        //   alert('there was an error')
      }
    });
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
 
 



  // if ("{{message}}" != '') {
  //   notificationModal('{{message}}')

  // }

  var navigationList = []
  var navigationObject = {}
  //   $(window).load(function(){
  //   $('body').backDetect(function(){
  //     alert("Look forward to the future, not the past!");
  //   });
  // });
  //   $(window).on("navigate", function (event, data) {
  //   var direction = data.state.direction;
  //   if (direction == 'back') {
  //     alert('back')
  //     $.ajax({
  //             beforeSend: function () {

  //               showLoadingBar()
  //             },
  //             complete: function () {
  //               hideLoadingBar()

  //             },
  //             type: 'get',
  //             url: navigationList[-1],
  //             data: {
  //               'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
  //             },
  //             success: function (response) {
  //               // if there are still more pages to load,
  //               // add 1 to the "Load More Posts" link's page data attribute
  //               // else hide the link
  //               // append html to the posts div
  //               //$('.content-modal-header-title').empty()

  //               //$('.content-modal-header-title').append(link.attr('inner-html'));
  //               if (response.content) {
  //                 navigationList.pop()
  //                 $('#tabcontent').removeClass('uk-animation-fade')

  //           $('#tabcontent').addClass('uk-animation-fade')
  //           $('#tabcontent').empty()
  //           $('.tab-pane').hide()
  //           $('#tabcontent').show()
  //               }


  //             },
  //             error: function (xhr, status, error) {
  //               alert('there was an error')
  //             }
  //           });

  //   }
  //   if (direction == 'forward') {
  //     // do something else
  //   }
  // }(jQuery));

//   $('.uk-modal').on('beforehide', function () {
//     $('.content-modal').removeClass('custom-modal-slide-bottom')

// $('.content-modal').addClass('custom-modal-slide-top')
//   })

  function closeModal() {

    try {
      $('.content-modal').removeClass('custom-modal-slide-bottom')

$('.content-modal').addClass('custom-modal-slide-top')
      UIkit.modal($('.uk-open')).hide();

    } catch (TypeError) {

    }
  }


  {
    (function ($) {
      $('.modal-close').on('click', function () {
        setTimeout( UIkit.modal($('.content-modal.uk-open')).hide,350)            //
        $('.content-modal').removeClass('custom-modal-slide-bottom')

        $('.content-modal').addClass('custom-modal-slide-top')

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

            if (response.content) {
              window.location = '#top'
              UIkit.modal($('#confirm-modal')).hide();

              $(link.attr('target')).empty()
              $(link.attr('target')).append(response.content);

            }

            if (response.message) {
              $('#confirm-modal-inner').append(response.message)

            }


          },
        });
      });
    }(jQuery))
  };

  function requestTabContent(contentUrl, action = 'post') {
    var link = $(this);
    $.ajax({
      beforeSend: function () {
        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()
      },
      type: action,
      url: contentUrl,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {

        if (response.content) {
          $('#tabcontent').removeClass('uk-animation-fade')

          $('#tabcontent').addClass('uk-animation-fade')
          $('#tabcontent').empty()
          $('#tabcontent').append(response.content)

        }
        if (response.modal_message) {
          messageModal(response.modal_message)

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

      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  }


  function requestDynamicContent(contentUrl, action = 'post',dynamicEl) {
    $.ajax({
      beforeSend: function () {

        showLoadingBar()
      },
      complete: function () {
        hideLoadingBar()

      },
      type: action,
      url: contentUrl,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
        if (response.content) {
          $(dynamicEl).removeClass('uk-animation-fade')

          $(dynamicEl).addClass('uk-animation-fade')
          $(dynamicEl).empty()
          $(dynamicEl).append(response.content)
          $(dynamicEl+'-container').show()


        }

      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  }

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

  function requestContentModal(contentUrl, action = 'post', updateable = '') {
   

    $.ajax({
      beforeSend: function () {
        $('.content-modal').removeClass('custom-modal-slide-top')

        $('.content-modal').addClass('custom-modal-slide-bottom')
        showLoadingBar()
      },
      complete: function () {       

        hideLoadingBar()

      },
      type: action,
      url: contentUrl,
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
          dispatchResponse(response)
        // UIkit.modal($('.content-modal.uk-open')).hide();

        // $('.content-modal.uk-close').removeClass('uk-transition-slide-bottom')

      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  }

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
      url: "{% url 'account_logout' %}",
      data: {
        'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
      },
      success: function (response) {
        window.location = '{% url 'account_login' %}'
        loggedOut = true
      },
      error: function (xhr, status, error) {
        alert('there was an error')
      }
    });
  };
  var loggedOut = false

  // $('#offcanvas-nav-primary').on('beforehide', function () {
  //   // alert('hidden')
  //   $('#major').css('transition-duration','0.5s')
  //   $('#major').css('transform-origin','left')

  //   $('#major').css('transition-timing-function','0.5s','cubic-bezier(0.175, 0.885, 0.32, 1.275)')
  //   // $('#major').css('transform', "translateX(" + '-' + $('.uk-offcanvas-bar').css('width') + ')')
  //     $('#major').css('margin-left', '0px')
   
  // });

  // $('#offcanvas-nav-primary').on('beforeshow', function () {
  //   $('#major').css('transition-duration','0.5s')
  //   $('#major').css('transform-origin','right')
  //   $('#major').css('transition-timing-function','cubic-bezier(0.175, 0.885, 0.32, 1.275)')
  //   if (jQuery(window).width() < 600) {
  //     $('#major').css('margin-left', '0px')
  //   }
  //   else {
  //     $('#major').css('margin-left', $('.uk-offcanvas-bar').css('width'))
  //   }
  //   // $('#major').css('transform', "translateX(" + $('.uk-offcanvas-bar').css('width') + ')')

  // });

  // jQuery(document).ready(function () {
  //   if (jQuery(window).width() < 600) {
  //     UIkit.offcanvas($('#offcanvas-nav-primary')).hide();
  //     $('#major').css('margin-left', '0px')
  //     $('.content-modal').addClass('uk-modal-full')
  //     $('.content-modal .uk-modal-dialog').removeClass('uk-margin-auto-vertical')
  //     $('.content-modal .uk-modal-dialog').removeClass('rounded-sm')
  //     $('.content-modal').addClass('bg-white')
  //     $('.mobile-el').removeClass('hide')
  //     $('.desktop-el').addClass('hide')

  //   }
  //   else {
  //     UIkit.offcanvas($('#offcanvas-nav-primary')).show();
  //     $('#major').css('margin-left', $('.uk-offcanvas-bar').css('width'))
  //     $('.content-modal').removeClass('uk-modal-full')
  //     $('.content-modal .uk-modal-dialog').addClass('uk-margin-auto-vertical')
  //     $('.content-modal .uk-modal-dialog').addClass('rounded-sm')
  //     $('.content-modal').removeClass('bg-white')
  //     $('.desktop-el').removeClass('hide')
  //     $('.mobile-el').addClass('hide')

  //   }
  // });


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

