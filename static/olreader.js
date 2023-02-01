const $bookListBooks = $('#booklist-books');
const $bookSearch = $('#book-search');
const $resultsDisplay = $('#search-results-display');

function displayFlashMessage(message, category) {
    $('#flash-container').append(
        `<div class="alert alert-${category} alert-dismissible fade show">
        ${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`);
}

async function performSearch(searchTerm) {
    $resultsDisplay.hide();
    $('#search-loading').show();

    searchResults = await axios.get(`/search/${searchTerm}`)
    $('#search-loading').hide();

    populateSearchResults(searchTerm, searchResults);
}

function populateSearchResults(searchTerm, searchResults) {
    const {data: {num_returned, total, works}} = searchResults;

    $resultList = $resultsDisplay.children('#search-results');
    $resultList.empty();
    for(work of works) {
        $resultList.append(generateResultHTML(work));
    }

    $resultsDisplay.find('#search-text').text(searchTerm);
    $resultsDisplay.children('#search-results-count').text(`Loaded ${num_returned} of ${total} total results`);
    $resultsDisplay.show();
}

function generateResultHTML(workResult) {
    $div = $('<div class="search-result"></div')

    coverURL = workResult['cover_url'];
    $cover = (coverURL != null && coverURL.length > 0) ?
            $(`<img class="cover-image" src="${coverURL}" />`) :
            $('<span class="cover-text fa-3x"><i class="fa-solid fa-book-bookmark"></i></span>'); // TODO build links to OL for books and authors?
    
    $title = $(`<span class="search-title">${workResult['title']} by ${workResult['author_name']}</span>`);
    
    $addButton = $(`<button class="btn btn-outline-primary btn-sm mx-2 add-book" type="button" data-id="${workResult['key']}">Add to List</a>`);
    $addButton.click(addBook);

    $div.append($cover);
    $div.append($title);
    $div.append($addButton);

    return $div;
}

async function addBook(evt) {
    const workId = $(evt.target).data('id');
    const listId = $bookSearch.data('listid');
    const result = await axios.post(`/lists/${listId}/add`, {workId: workId});
    console.log(result.data);
    if (result.data['err'] != null) {
        const {err, type} = result.data;
        console.log(err, type);
        displayFlashMessage(err, type);
    } else {
        addToBooklist(result.data);
    }
}

function addToBooklist(book) {
    $bookListBooks.children('#empty-list-msg').hide();
    if ($bookListBooks) {
        $bookListBooks.append($(`<li><a href="/books/${book.olid}">${book.title}</a> by ${book.author} <a href="#" class="link-danger" data-id=${book.olid}><i class="fa-regular fa-circle-xmark"></i></a></li>`))
    }
}

async function removeBook(evt) {
    const $link = $(evt.target).parent();
    const workId = $link.data('id');
    const listId = $bookListBooks.data('listid');
    const result = await axios.post(`/lists/${listId}/remove`, {workId: workId});
    
    if (result.data['err'] != null) {
        const {err, type} = result.data;
        console.log(err, type);
        displayFlashMessage(err, type);
    } else {
        $link.parent().remove();
    }
}

if ($bookListBooks) {
    $bookListBooks.on('click', '.fa-circle-xmark', removeBook);
}

if($bookSearch) {
    $bookSearch.on('submit', (evt) => {
        evt.preventDefault();

        const searchTerm = $bookSearch.children('#book-search-term').val();
        performSearch(searchTerm);
    })
}