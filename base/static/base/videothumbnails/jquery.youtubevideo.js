/**
 * jQuery.youtubeVideo
 * Version: 1.1.4
 * Repo: https://github.com/WahaWaher/youtubevideo-js
 * Author: Sergey Kravchenko
 * Contacts: wahawaher@gmail.com
 * License: MIT
 */

;(function($) {

	var methods = {

		init: function(options) {

			var defaults = $.extend(true, {

				layout: {
					wrap: $('<div />', { class: 'ytb-video-wrap' }),
					container: $('<div />', { class: 'ytb-video-container' }),
					iframe: $('<iframe />', { class: 'ytb-video-iframe' }),
					button: $('<div />', { class: 'ytb-video-play-button'})
						.append('<svg viewBox="0 0 68 48"><path class="ytb-video-play-button-bg" d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#212121" fill-opacity="0.8"></path><path d="M 45,24 27,14 27,34" fill="#fff"></path></svg>'),
				},

				aspectRatio: 56.25,
				cover: 'mqdefault',
				parametrs: 'autoplay=1&autohide=1',
				playEvent: 'click',
				playMode: 'block',
				type: 'video',
				api: '',
				duration: false,
				title: false,
				description: false,

				beforeInit:       function() {},
				afterInit:        function() {},
				beforeLoadIframe: function() {},
				afterLoadIframe:  function() {},
				afterLoadCover:   function() {},

			}, $.fn.youtubeVideo.defaults);

			this.each(function() {
				var $ths = $(this);

				if( $ths.data('_init') == true ) return false;

				$ths.data('defaults', defaults);
				$ths.data('options', options);

				var data = $ths.attr('data-ytb-options');
				data = eval('(' + data + ')');
				if( typeof(data) != 'object') data = {};

				$ths.data('settings', $.extend(true, {}, defaults, options, data));
				var sets = $ths.data('settings'),
					 layout = sets.layout;

				sets._videoID = getVideoID( $ths.attr('data-ytb-video') );	
					 
				// Callback: beforeInit()
				sets.beforeInit.call($ths, sets);

				createFirstMarkup();

				// Воспроизведение (событие)
				// ID для генерации уник.числа (пространство имен, обраб.)
				sets._nsid = randInt(10000000, 99999999);

				if( sets.playMode === 'button' )
					sets.playElement = sets.layout.button;
					else if( sets.playMode === 'block' ) sets.playElement = $ths;
					else sets.playElement = sets.playMode;

				if( sets.playEvent )
					sets.playElement.one(sets.playEvent+'.yv-'+sets._nsid, function() {
						methods.play.call($ths);
					})

				// Созд. разметки для блока видео
				function createFirstMarkup() {

					$ths.addClass('ytb-video');

					// Доб. контейнер
					if( layout.container ) {
						layout.container = layout.container.clone().appendTo($ths);
					}

					// Доб. кнопку воспр. в контейнер
					if( layout.button ) {
						layout.button = layout.button.clone().appendTo( sets.layout.container );
					}

					// Доб. обертку контейнер
					if( layout.wrap ) {
						layout.container.wrap( layout.wrap.clone() );
						layout.wrap = layout.container.parent();
					}

					if( sets.aspectRatio && sets.aspectRatio > 0 && sets.aspectRatio <= 100 ) {
						layout.wrap.css({
							'padding-bottom' : sets.aspectRatio+'%',
							'position' : 'relative'
						});
					}

					// Форм. айфрейм
					if( layout.iframe ) {
						layout.iframe = layout.iframe.clone();
					}

					if( sets.api ) getApiInfo();

					// ДОБ. ОБЛОЖКУ
					var coverImg = new Image();
					// Обложка (собственный URL)
					if( sets.cover && typeof(sets.cover) == 'string' && sets.cover.indexOf('http') + 1 ) {

						coverImg.src = sets.cover;
						coverImg.onload = function() {
							layout.container.css('background-image', 'url(' + sets.cover + ')');
							// Callback: afterLoadCover()
							sets.afterLoadCover.call($ths, sets);
						}

					// Обложка (строка, значения по умолчанию)
					} else if( sets.cover && typeof(sets.cover) == 'string' && sets.cover.indexOf('default') + 1 ) {

						var coverLink = 'https://i.ytimg.com/vi/' + sets._videoID + '/'+ sets.cover +'.jpg';

						coverImg.src = coverLink;
						coverImg.onload = function() {
							sets.layout.container.css('background-image', 'url('+ coverLink +')');
							// Callback: afterLoadCover()
							sets.afterLoadCover.call($ths, sets);
						}
						
					// Обложка (массив с приоритетами)
					} else if ( Array.isArray(sets.cover) && sets.api ) {

						onVideoInfoReady(function() {

							var thumbsBase, coverFinal, coverSuccess;

							// Получ. объекта с ссылками
							$(window.youtubeIDsInfo.items).each(function (key,value) {
								if( value.id == sets._videoID ) {
									thumbsBase = value.snippet.thumbnails;
									return;
								}
							});

							// Поиск по приоритетам
							$.each(sets.cover, function (key,value) {

								// Если совпадений еще не найдено
								if( coverSuccess ) return;

								// Если ссылка
								if( value.indexOf('http') + 1 ) {
									coverFinal = value;
									coverSuccess = true;
									return;
								}

								// Если стандартные значения
								var coverCurDef = value;
								$.each(thumbsBase, function (key,value) {
									if( value.url.indexOf('/'+ coverCurDef +'.jpg') + 1 ) {
										coverFinal = value.url;
										coverSuccess = true;
										return;
									}
								});

							});

							// Уст. обложки по первому совпадению
							if( coverFinal ) {
								coverImg.src = coverFinal;
								coverImg.onload = function() {
									sets.layout.container.css('background-image', 'url(' + coverFinal + ')');
									// Callback: afterLoadCover()
									sets.afterLoadCover.call($ths, sets);
								}

							}

						});

					} else if ( window.youtubeIDsInfo === false ) {
						coverImg.src = 'https://i.ytimg.com/vi/'+ sets._videoID +'/mqdefault.jpg';
						coverImg.onload = function() {
							sets.layout.container.css('background-image', 'url(' + coverImg.src + ')');
							// Callback: afterLoadCover()
							sets.afterLoadCover.call($ths, sets);
						}
						
					}

					// Доб. продолжительности видео
					if( sets.duration && sets.api && sets.type == 'video' ) {

						onVideoInfoReady(function() {

							var curKey = false,
							durationText;

							$(window.youtubeIDsInfo.items).each(function (key,value) {
								if( value.id != sets._videoID ) return;
								else {
									curKey = key;
									return false;
								}
							});

							if( curKey || curKey == 0 ) {
								durationText = formatDate(window.youtubeIDsInfo.items[curKey].contentDetails.duration);

								var durationMarkup = $('<span/>', { class: 'ytb-video-duration' })
								.append($('<span/>', { class: 'ytb-video-duration-text', text: durationText }));

								sets.layout.container.append( durationMarkup );
							}

						});

					}

					// Доб. ориг. заголовка видео
					if( sets.title && sets.api && sets.type == 'video' ) {

						onVideoInfoReady(function() {

							if( !window.youtubeIDsInfo.firstTitleCheck ) {
								$(window.youtubeIDsInfo.items).each(function (key,value) {

									var baseTitleID = value.id,
									baseTitle = value.snippet.title;

									$('[data-ytb-title-id]').each(function (key,value) {
										if( baseTitleID == $(value).attr('data-ytb-title-id') ) {
											$(this).text(baseTitle);
										}
									});

								});
								window.youtubeIDsInfo.firstTitleCheck = true;
							}

						});

					}

					// Доб. ориг. описания видео
					if( sets.description && sets.api && sets.type == 'video' ) {

						onVideoInfoReady(function() {

							if( !window.youtubeIDsInfo.firstDescrCheck ) {
								$(window.youtubeIDsInfo.items).each(function (key,value) {

									var baseIDDescr = value.id,
									baseDescr = value.snippet.description;

									$('[data-ytb-descr-id]').each(function (key,value) {
										if( baseIDDescr == $(value).attr('data-ytb-descr-id') ) {
											$(this).text(baseDescr);
										}
									});

								});
								window.youtubeIDsInfo.firstDescrCheck = true;
							}

						});

					}

				}

				// Загрузка инф. о видео
				function getApiInfo() {
					if( !sets.api || window.youtubeIDsCheck == true ) return false;
					if( window.youtubeIDsInfo ) return window.youtubeIDsInfo;

					var videoIDsArray = [],
						 videoIDs = '',
						 requestUrl;

					$('[data-ytb-video]').each(function (key,value) {
						if( videoIDs.indexOf($(value).attr('data-ytb-video')) == -1 ) {
							videoIDs += getVideoID( $(value).attr('data-ytb-video') ) + ',';
						}
					});

					videoIDs = videoIDs.substring(0, videoIDs.length - 1);
					requestUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id='+videoIDs+'&key='+sets.api+'&fields=items(id,snippet(title,description,thumbnails),contentDetails(duration))';
					
					$.ajax({
						url: requestUrl,
						type: 'GET',
						async: true,
						success: function (data) {
							window.youtubeIDsInfo = data;
						},
						error: function (data) {
							window.youtubeIDsInfo = false;
						}
					});

					window.youtubeIDsCheck = true;
					return window.youtubeIDsInfo;

				}

				// Формат времени для функции "Продолжительность видео"
				function formatDate(input) {

					var reptms = /^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/,
						 hours = 0, minutes = 0, seconds = 0, totalseconds;

					if (reptms.test(input)) {
						var matches = reptms.exec(input);
						if (matches[1]) hours = Number(matches[1]);
							if (matches[2]) minutes = Number(matches[2]);
								if (matches[3]) seconds = Number(matches[3]);
									totalseconds = hours * 3600  + minutes * 60 + seconds;
					}

					var date = new Date(null);
					date.setSeconds(totalseconds-1);

					var result = date.toISOString().substr(11, 8);

					for (var i = 0; i < 3; i++) {
						if( result.charAt(0) == '0' || result.charAt(0) == ':' )
							result = result.substr(1);
					};

					return result;
				}

				$ths.data('_init', true);

				// Callback: afterInit()
				sets.afterInit.call($ths, sets);

			});

			return $(this);

		},

		destroy: function() {

			if( !$(this).data('_init') ) return false;
			var $ths = $(this), sets = $ths.data('settings');

			if( sets.layout.playEvent )
				sets.playElement.off( sets.playEvent+'.yv-'+sets._nsid );
			sets.layout.wrap.remove();
			$ths.removeData();

			return $(this);

		},

		reinit: function(newOpts) {
			var $ths = $(this), sets = $ths.data('settings');

			var oldOpts = $ths.data('options');
			methods.destroy.call($ths);

			if( newOpts && typeof(newOpts) == 'object' )
				methods.init.call($ths, newOpts);
			else methods.init.call($ths, oldOpts);

			return $(this);

		},

		play: function() {
			var $ths = $(this), sets = $ths.data('settings'),
				 layout = sets.layout;

			// Callback: beforeLoadIframe()
			sets.beforeLoadIframe.call($ths, sets);

			var src = '';

			if( sets.type == 'video' ) {
				src = 'https://www.youtube.com/embed/' + sets._videoID;
				if( sets.parametrs ) src += '?' + sets.parametrs;
			} else if( sets.type == 'playlist' ) {
				src = 'https://www.youtube.com/embed/videoseries?list=' + sets._videoID;
			}

			layout.iframe.attr({
				src: src,
				frameborder: 0,
				allowfullscreen: ''
			});

			if( layout.wrap && sets.aspectRatio > 0 && sets.aspectRatio < 100 ) {
				iFrameReplace($ths.find('.' + sets.layout.wrap.get(0).className));
			} else {
				iFrameReplace($ths);
			}

			function iFrameReplace(appendTo) {
				// layout.container.remove();
				// layout.iframe.appendTo(appendTo).on('load', function () {

				// 	// Callback: afterLoadIframe()
				// 	sets.afterLoadIframe.call($ths, sets);

				// });
			}

			return $(this);

		},

	};

	// По выполнению к/д ajax для некотор. опций 
	function onVideoInfoReady(foo) {
		var intCnt = 0, intID = setInterval(function() {
			if( intCnt > 500 ) clearInterval(intID);

			if( window.youtubeIDsInfo ) {
				foo();
				clearInterval(intID);
			}

			intCnt++;
		}, 50);
	};

	// Генератор случайного числа
	function randInt(min, max) {
		var rand = min - 0.5 + Math.random() * (max - min + 1)
		rand = Math.round(rand);
		return rand;
	}
	// Отсеиватель ID Видо из строки (ссылка)
	function getVideoID(string) {
		if( string.match(/http/igm) )
			return string.split('?v=')[1].split('?t=')[0].split('&t=')[0];
		return string;
	}

	$.fn.youtubeVideo = function(methOrOpts) {
		if ( methods[methOrOpts] ) {
			return methods[ methOrOpts ].apply( this, Array.prototype.slice.call( arguments, 1 ));
		} else if ( typeof methOrOpts === 'object' || ! methOrOpts ) {
			methods.init.apply( this, arguments );
			return this;
		} else {
			$.error( 'Method ' +  methOrOpts + ' does not exist on jQuery.youtubeVideo' );
		}    
	};

})(jQuery);