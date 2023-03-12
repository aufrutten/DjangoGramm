
function get_subscriptions(profile) {
    let url = `/api/v1/profiles/${profile}/subscriptions/`;
    $.get(url).done(function (data){
        $('#subscriptions').html(data.count);
    })

}

function get_subscribers(profile) {
    let url = `/api/v1/profiles/${profile}/subscribers/`;
    $.get(url).done(function (data){
        $('#subscribers').html(data.count);
    })


}

function get_status(profile_id, subscriber_id) {
    let url = `/api/v1/profiles/${profile_id}/subscriptions/${subscriber_id}`;
    $.get(url).done(function () {
        $('#button_sub').html('Unsubscribe');
    }).fail(function () {
        $('#button_sub').html('Subscribe');
    });
    get_subscribers(subscriber_id);
}

function do_subscribe(profile_id, subscriber_id) {
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    let url = `/api/v1/profiles/${profile_id}/subscriptions/`;
    let data = {to_user: subscriber_id, csrfmiddlewaretoken: csrf_token};
    $.post(url, data).done(function (data) {
        get_status(profile_id, subscriber_id);
    });

}