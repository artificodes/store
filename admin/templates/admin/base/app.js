var spa_links = $('.spa')






for (let index = 0; index < spa_links.length; index++) {

  spaObject['#' + $(spa_links[index]).attr('href')] = {}
  spaObject['#' + $(spa_links[index]).attr('href')]['url'] = $(spa_links[index]).attr('href')
  if($(spa_links[index]).attr('href').startsWith('#')){

  }
  else{
  $(spa_links[index]).attr('href', '#' + $(spa_links[index]).attr('href'))

  }
}
{% if request.user.is_authenticated %}
// Application.run();

{% else %}
// Application.run('#/login');
{% endif %}


