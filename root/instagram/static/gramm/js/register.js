const url_api = "/api/v1/profiles/";
const url_confirm_email = "/confirm_email/";

is_equal = function (string_one, string_two) {
    return string_one === string_two
};

password_validate = function (password, password_control){
    if (password.length < 8){
        $("#label_password")
            .html("Password isn't validate")
            .css('color', 'red');
        $("#label_another_password").css('color', 'red');
        return false;
    } else if (is_equal(password, password_control)) {
        return true;
    } else {
        $("#label_another_password")
            .html("Password isn't equal")
            .css('color', 'red');
        return false;
    }

};

$(document).ready(function () {
    $('input[name="first_name"]').click(function () {
        $('#label_first_name').css('color', 'black')});

    $('input[name="last_name"]').click(function () {
        $('#label_last_name').css('color', 'black')});

    $('input[name="birthday"]').click(function () {
        $('#label_birthday').css('color', 'black')});

    $('input[name="email"]').click(function () {
        $('#label_email').html('Email address').css('color', 'black')});

    $('input[name="password"]').click(function () {
        $('#label_password').html('Password').css('color', 'black')});

    $('input[name="another_password"]').click(function () {
        $('#label_another_password').html('Confirm password').css('color', 'black')});

    $("#SignUp").click(function () {
        let first_name = $('input[name="first_name"]').val();
        let last_name = $('input[name="last_name"]').val();
        let birthday = $('input[name="birthday"]').val();
        let email = $('input[name="email"]').val();
        let password = $('input[name="password"]').val();
        let password_control = $('input[name="another_password"]').val();

        let flag = true;

        if (first_name === ''){
            $('#label_first_name').css('color', 'red');
            flag = false;
        }
        if (last_name === ''){
            $('#label_last_name').css('color', 'red');
            flag = false;
        }
        if (birthday === ''){
            $('#label_birthday').css('color', 'red');
            flag = false;
        }
        if (email === ''){
            $('#label_email').css('color', 'red');
            flag = false;
        }

        if (password_validate(password, password_control) || flag) {
            const data = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "birthday": birthday,
                "password": password};

            $.post(url_api, data)
                .done(function(data) {
                    location.href=`${url_confirm_email}${data['email']}`;
                })
                .fail(function(xhr, status, error) {
                    const response = xhr.responseJSON;
                    console.log(response);
                    if (response.email){
                        $('#label_email').html(response.email).css('color', 'red');}
                });
        }
    });
})