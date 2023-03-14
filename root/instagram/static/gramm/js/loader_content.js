
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

    const hearth = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-heart" viewBox="0 -0.5 16 16">' +
        '<path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>' +
        '</svg>'

    const hearth_fill = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-heart-fill" viewBox="0 0 16 16">' +
        '<path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>' +
        '</svg>'

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

function getHTML(post, email) {
    return `<br>
            <div class="col-md-10 mx-auto col-lg-5" id="login_div">
                <div class="modal-content rounded-4 shadow">
                    <div class="modal-header p-5 pb-4 border-bottom-0">
                        <a href="/profiles/${post.user || profile_id}" style="color: #353535">
                            <label class="fw-bold mb-0 fs-2">${email}</label>
                        </a>
                    </div>
                    <div class="modal-body p-5 pt-0">
                        <img src="${post.image}" alt="post" class="card-img-top">
                        <div id="carouselExample" class="carousel slide">
                          <div class="carousel-inner">
                            <div class="carousel-item active">
                              <img src="${post.image}" class="d-block w-100" alt=".">
                            </div>
                            <div class="carousel-item">
                              <img src="${post.image}" class="d-block w-100" alt="...">
                            </div>
                            <div class="carousel-item">
                              <img src="${post.image}" class="d-block w-100" alt="...">
                            </div>
                          </div>
                          <button class="carousel-control-prev" type="button" data-bs-target="#carouselExample" data-bs-slide="prev">
                            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                            <span class="visually-hidden">Previous</span>
                          </button>
                          <button class="carousel-control-next" type="button" data-bs-target="#carouselExample" data-bs-slide="next">
                            <span class="carousel-control-next-icon" aria-hidden="true"></span>
                            <span class="visually-hidden">Next</span>
                          </button>
                        </div>
                        <label style="font-size: 16px; font-weight: bold">Likes: <label id="likes_count_${post.id}"></label></label>
                        <hr class="my-4">
                        <button class="btn"
                                type="button"
                                id="like_button_${post.id}"
                                onclick="do_like(${post.id})">
                        </button>
                        <script>get_count_likes(${post.id})</script>
                        <script>get_status_like(${post.id})</script>
                        <button class="btn" type="button" onclick="location.href='/posts/${post.id}/comments'">
                            <svg xmlns="http://www.w3.org/2000/svg" width="31" height="31" fill="currentColor" class="bi bi-chat" viewBox="0 1.1 16 16">
                                <path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>`
}


let page = 0;

function loadContent() {
    page += 1;
    let url_page = `${url}/?page=${page}`;
    console.log(url);
    console.log(url_page);
    $.ajax({url: url_page, type: 'GET'})
        .done(function (response, textStatus, jqXHR) {
            if (jqXHR.status === 200) {
                let posts = response['results'];
                for (let post in posts) {
                    post = posts[post];

                    if (post.user) {
                        $.get(`/api/v1/profiles/${post.user}`).done(function (data) {
                            let email = data.email;
                            let html = getHTML(post, email);
                            $("#content-container").append(html)
                        })
                    } else if (profile_id) {
                        $.get(`/api/v1/profiles/${profile_id}`).done(function (data) {
                            let email = data.email;
                            let html = getHTML(post, email);
                            $("#content-container").append(html)
                        })
                    } else {
                        let email = 1;
                        let html = getHTML(post, email);
                        $("#content-container").append(html)}
                    }
                    }}).fail(function () {
                        page -= 1;
    })}


$(window).scroll(function() {
  if($(window).scrollTop() + $(window).height() === $(document).height()) {
    loadContent();
  }
});