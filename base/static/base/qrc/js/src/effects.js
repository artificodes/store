$(document).ready(function () {

	// Webcam.attach('#example');

	// $('#button').click(function () {
	// 	take_snapshot();
	// });

	// setInterval(take_snapshot,100)
	// qrcode.callback = showInfo;

});

function take_snapshot() {
	Webcam.snap(function (dataUrl) {
		qrCodeDecoder(dataUrl);
	});
}

// decode the img
function qrCodeDecoder(dataUrl) {
	qrcode.decode(dataUrl);
}

// show info from qr code
function showInfo(qrresult) {
	// $("#qr-data").text(data);
	if (eventid == qrresult){
		clearInterval(qrCodeInterval)
	$.ajax({
		 beforeSend: function () {
			clearInterval(qrCodeInterval)
			Webcam.reset()
			$('#loader-cover').show()
		},
		// complete: function () {
		// },
		type: 'get',
		url: eventVerificationUrl,
		data: {
			'csrfmiddlewaretoken': window.CSRF_TOKEN, // from index.html
			'eventid': eventid,
		},
		success: function (response) {
			// if there are still more pages to load,
			// add 1 to the "Load More Posts" link's page data attribute
			// else hide the link
			// append html to the posts div
			//$('.uk-modal-header-title').empty()

			//$('.uk-modal-header-title').append(link.attr('inner-html'));
	
			if (response.content) {
				$('#tab-header').empty()
				$('#tab-header').append(response.header);
				$('#inner-container').empty();
				$('#inner-container').append(response.content);
				$('#loader-cover').hide()
			}

			if (response.message) {
				window.location = "#top"
				$('#loader-cover').hide()
				$("#qr-data").empty()
				$("#qr-data").append(response.message);
			}

			if (response.attended) {
			}



		},
		error: function (xhr, status, error) {
			alert('there was an error')
		}
	});
	}


}
