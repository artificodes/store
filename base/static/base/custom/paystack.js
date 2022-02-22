function buyTicketWithPaystack(amount, email, eventId, ticketName,url, number, ticketid = 'none') {

    var handler = PaystackPop.setup({
        key: 'pk_live_216c10da82414b47691d04c51b8795a967f7ed79', //put your public key here
        email: email, //put your customer's email here
        amount: amount, //amount the customer is supposed to pay
        metadata: {
            custom_fields: [
                {
                    display_name: ticketName,
                    variable_name: '',
                    value: number //customer's mobile number
                }
            ]
        },
        callback: function (response) {
            //after the transaction have been completed
            //make post call  to the server with to verify payment 
            //using transaction reference as post data
            if (response.status == 'success') {
                $.ajax({
                    beforeSend: function () {

                        $('#loader-cover').show()
                    },
                    complete: function () {
                    },
                    type: 'post',
                    url: url,
                    data: {
                        'csrfmiddlewaretoken': window.CSRF_TOKEN,
                        'reference': response.reference,
                    },
                    success: function (response) {
                        // if there are still more pages to load,
                        // add 1 to the "Load More Posts" link's page data attribute
                        // else hide the link
                        // append html to the posts div
                        //$('.uk-modal-header-title').empty()

                        //$('.uk-modal-header-title').append(link.attr('inner-html'));
                        if (response.registered) {
                            if (response.content) {
                                $('#manager-container').empty();
                                $('#manager-container').append(response.content);
                            }
                            if (response.message) {

                                $('.uk-modal-body').css({ 'background-color': 'green', 'color': 'white' })
                                UIkit.modal($('#response-modal')).show();
                                $('.modal-message').append(response.message)

                            }
                        }

                        else {
                            $('.uk-modal-body').css({ 'background-color': 'orange', 'color': 'white' })
                            UIkit.modal($('#response-modal')).show();
                            $('.modal-message').append(response.message)
                        }

                    },
                    error: function (xhr, status, error) {
                        alert('there was an error')
                    }
                });
            }


        },
        onClose: function () {
            //when the user close the payment modal
            $('.uk-modal-body').css({ 'background-color': 'orange', 'color': 'white' })
            UIkit.modal($('#response-modal')).show();
            $('.modal-message').append('Transaction canceled')
            
            
        }
    });
    handler.openIframe(); //open the paystack's payment modal
}




function payLoan(amount, email, number, name, loanurl) {
    var handler = PaystackPop.setup({
        key: 'pk_live_216c10da82414b47691d04c51b8795a967f7ed79', //put your public key here
        email: email, //put your customer's email here
        amount: amount, //amount the customer is supposed to pay
        metadata: {
            custom_fields: [
                {
                    display_name: name,
                    variable_name: name,
                    value: number //customer's mobile number
                }
            ]
        },
        callback: function (response) {
            //after the transaction have been completed
            //make post call  to the server with to verify payment 
            //using transaction reference as post data
            $.ajax({
                beforeSend: function () {
                    alert(response.reference)


                    $('#loan').append(inline_loader_small_center);


                },
                complete: function () {
                    $('#loan').children('.loading').remove()
                },
                type: 'post',
                url: loanurl,
                data: {
                    'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
                    'reference': response.reference,
                },
                success: function (response) {
                    // if there are still more pages to load,
                    // add 1 to the "Load More Posts" link's page data attribute
                    // else hide the link
                    // append html to the posts div
                    //$('.uk-modal-header-title').empty()

                    //$('.uk-modal-header-title').append(link.attr('inner-html'));
                    if (response.repaid) {
                        // alert(response.reference)
                        $('.uk-modal-body').css({ 'background-color': 'white', 'color': 'black' })
                        UIkit.modal($('#response-modal')).show();
                        $('.modal-message').append(response.message)
                        $.ajax({
                            beforeSend: function () {

                                $('#loan').append(inline_loader_small_center);

                            },
                            complete: function () {
                                $('#loan').children('.loading').remove()
                            },
                            type: 'get',
                            url: "{% url 'customer_loan_contents' %}",
                            data: {
                                'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
                            },
                            success: function (data) {
                                // if there are still more pages to load,
                                // add 1 to the "Load More Posts" link's page data attribute
                                // else hide the link
                                // append html to the posts div
                                //$('.uk-modal-header-title').empty()

                                //$('.uk-modal-header-title').append(link.attr('inner-html'));
                                $('#loan').empty()

                                $('#loan').append(data.content);


                            },
                            error: function (xhr, status, error) {
                                alert('there was an error')
                            }
                        });



                    }


                },
                error: function (xhr, status, error) {
                    alert('there was an error')
                }
            });


            // $.post("verify.php", {reference:response.reference}, function(status){
            //     if(status == "success")
            //         //successful transaction
            //         alert('Transaction was successful. You will be redirected shortly');
            //     else{//transaction failed

            //        }
            // });
        },
        onClose: function () {
            //when the user close the payment modal
            $('.modal-message').empty()
            $('.uk-modal-body').css({ 'background-color': 'orange', 'color': 'white' })
            UIkit.modal($('#response-modal')).show();
            $('.modal-message').append('Transaction canceled')
        }
    });
    handler.openIframe(); //open the paystack's payment modal
}