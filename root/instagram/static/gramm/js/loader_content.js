
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

    const hearth = '<i width="30" height="30" fill="currentColor" class="bi bi-heart" viewBox="0 -0.5 16 16"></i>'

    const hearth_fill = '<i width="30" height="30" fill="currentColor" class="bi bi-heart-fill" viewBox="0 0 16 16"></i>'

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
                        <a class="btn" onclick="/posts/${post.id}/comments/">
                            <i width="31" height="31" fill="currentColor" class="bi bi-chat" viewBox="0 1.1 16 16"></i>
                        </a>
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