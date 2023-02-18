const $bookSearch = $('#book-search');
const $resultsDisplay = $('#search-results-display');

let cur_page = 1;
let num_results =  0;

async function performSearch(searchTerm, page = 1) {
    $('#search-loading').show();

    searchResults = await axios.get(`/search/${searchTerm}?page=${page}`);
    $('#search-loading').hide();

    populateSearchResults(searchTerm, searchResults);
}

function populateSearchResults(searchTerm, searchResults) {
    const {data: {user_lists, results:{num_returned, total, works}}} = searchResults;

    const $resultList = $resultsDisplay.children('#search-results');
    for(let work of works) {
        $resultList.append(generateResultHTML(work, user_lists));
    }

    $resultsDisplay.find('#search-text').text(searchTerm);
    num_results += num_returned;
    $resultsDisplay.find('#search-results-count').text(`Showing ${num_results} of ${total} results`);
    if (num_results >= total) {
        $('#search-load-more').hide();
    }

    $resultsDisplay.show();
}

function generateResultHTML(workResult, userLists) {
    const $div = $('<div class="search-result"></div>')

    const coverURL = workResult['cover_url'];
    const $cover = (coverURL != null && coverURL.length > 0) ?
            $(`<img class="cover-image" src="${coverURL}-S.jpg" />`) :
            $('<span class="cover-text fa-3x text-primary"><i class="fa-solid fa-book-bookmark"></i></span>');
    
    const $title = $(`<span class="search-title">${workResult['title']} by ${workResult['author_name']}</span>`);

    $div.append($cover);
    $div.append($title);

    const list_search = $bookSearch.data('listid') != null;
    if (list_search) {
        const $addButton = $(`<a href="#" class="btn btn-outline-primary btn-sm mx-2" data-id="${workResult['olid']}" data-isbn="${workResult['isbn']}">Add to List</a>`);
        $addButton.click(addBook);
        $div.append($addButton);
    } else {
        const $addButton = $(`<a href="/notes/create?bookid=${workResult['olid']}" class="btn btn-outline-primary btn-sm mx-2">Add Note</a>`);
        $addButton.click(addNote);
        $div.append($addButton);
    }

    if ($resultsDisplay.data('global') == true) {
        createAddListDropdownHTML($div, workResult['olid'], userLists, 'btn-outline-primary btn-sm');
    }

    // if (!workResult['isbn']) {
    //     console.log(`Result ${workResult['title']} with OLID ${workResult['olid']} doesn't have an ISBN}`);
    // }

    return $div;
}

function resetSearchDisplay() {
    $resultsDisplay.children('#search-results').empty();
    $resultsDisplay.children('#search-load-more').show();
    $resultsDisplay.hide();
    cur_page = 1;
    num_results =  0;
}

function getSearchTerm(target) {
    let searchTerm = $bookSearch.children('#book-search-term').val();
    if (searchTerm == null) {
        searchTerm = $(target).data('search-term');
    }
    return searchTerm;
}

if ($bookSearch.length) {
    $bookSearch.on('submit', (evt) => {
        evt.preventDefault();

        resetSearchDisplay();

        const searchTerm = getSearchTerm(evt.target);
        performSearch(searchTerm);
    })
}

if ($('#search-load-more').length) {
    $('#search-load-more').click((evt) => {
        evt.preventDefault();

        const searchTerm = getSearchTerm(evt.target);
        cur_page += 1;
        performSearch(searchTerm, page = cur_page);
    });
}

if ($('#search-results-count').length) {
    // kludge to fix the counts
    const initialCount = $('#search-results-count').data('initial-count');
    if (initialCount != null) {
        num_results = initialCount;
    }
}