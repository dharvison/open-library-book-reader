
function displayFlashMessage(message, category) {
    $('#flash-container').append(
        `<div class="alert alert-${category} alert-dismissible fade show">
        ${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`);
}

function createBookHTML(book) {
    const title = book.title;
    const author = book.author_name;
    // const cover_i = book.cover_i;
    const cover_key = book.cover_edition_key;
    const lending_olid = book.lending_edition_s;

    const $cardDiv = $(`<div class="card" data-olid=${lending_olid}></div>`);
    // $cardDiv.append($(`<img class="card-img-top" src="https://covers.openlibrary.org/b/id/${cover_i}-M.jpg" alt="Book cover">`));
    $cardDiv.append($(`<img class="card-img-top" src="https://covers.openlibrary.org/b/olid/${cover_key}-M.jpg" alt="Book cover">`));

    const $cardBody = $(`<div class="card-body"><h4 class="card-title">${title}</h5><h5 class="card-subtitle">by ${author}</h5>`);
    $cardBody.append($(`<a href="/notes/create?bookid=${lending_olid}" class="btn btn-outline-primary btn-sm ml-2">Add Note</a>`));
    $cardDiv.append($cardBody);


    const $bookDiv = $(`<div class="col-xl-3 col-md-4 col-sm-6 col-12 my-2"></div>`);
    $bookDiv.append($cardDiv);

    return $bookDiv;
}


async function loadTrending() {
    $('#search-loading').show();
    trendingBooks = await axios.get(`/trending`);
    for (book of trendingBooks.data) {
        $trending.append(createBookHTML(book));
    }
    $('#search-loading').hide();
}


const $trending = $('#trending-books')
if ($trending.length) {
    loadTrending();
}