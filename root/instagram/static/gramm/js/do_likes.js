
function get_count_likes(post_id) {
    let url = `/api/v1/posts/${post_id}/likes/`;
    let label_count_like = `#likes_count_${post_id}`
    $.get(url).done(function (data){
        $(label_count_like).html(data.count);
    })
}

function get_status_like(post_id) {
    let url = `/api/v1/profiles/${request_user_id}/likes/${post_id}/`;
    let button_like = `#like_button_${post_id}`

    const hearth = '<i class="bi bi-heart"></i>'
    const hearth_fill = '<i class="bi bi-heart-fill"></i>'

    $.get(url).done(function () {
        $(button_like).html(hearth_fill).css('color', 'red');
    }).fail(function (){
        $(button_like).html(hearth).css('color', 'black');
    });

    get_count_likes(post_id);
}

function do_like(post_id) {
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    let url = `/api/v1/posts/${post_id}/likes/`;
    let data = {csrfmiddlewaretoken: csrf_token};
    $.post(url, data).done(function (data) {
        console.log(data);
        get_status_like(post_id)
    });
}
