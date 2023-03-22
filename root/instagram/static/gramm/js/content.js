
let post = 0;

loadContent = function() {
    post += 1;
    let url_post = `/posts/${post}`;
    $.ajax({url: url_post, type: 'GET'}).done(function (response, textStatus, jqXHR){
        $("#content-container").append(response);
    }).fail(function () {
        post -= 1
    })
}

$(window).scroll(function() {
  if($(window).scrollTop() + $(window).height() === $(document).height()) {
    loadContent();
  }
});