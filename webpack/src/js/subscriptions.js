import $ from 'jquery';

export var get_count_subscriptions = function(profile) {
    let url = `/api/v1/profiles/${profile}/subscriptions/`;
    $.get(url).done(function (data){
        $('#subscriptions').html(data.count);
    })
}

export var get_count_subscribers = function(profile) {
    let url = `/api/v1/profiles/${profile}/subscribers/`;
    $.get(url).done(function (data){
        $('#subscribers').html(data.count);
    });
}

export var get_status_subscribe = function(profile_id, subscriber_id) {
    let url = `/api/v1/profiles/${profile_id}/subscriptions/${subscriber_id}`;
    $.get(url).done(function () {
        $('#button_sub').html('Unsubscribe');
    }).fail(function () {
        $('#button_sub').html('Subscribe');
    });
    get_count_subscribers(subscriber_id);
}

export var do_subscribe = function(profile_id, subscriber_id) {
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    let url = `/api/v1/profiles/${profile_id}/subscriptions/`;
    let data = {to_user: subscriber_id, csrfmiddlewaretoken: csrf_token};
    $.post(url, data).done(function () {
        get_status_subscribe(profile_id, subscriber_id);
    });
}