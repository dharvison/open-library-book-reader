const $bookSearch = $('#book-search');
const $resultsDisplay = $('#search-results-display');

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

    const coverURL = workResult['cover_url'];
    const $cover = (coverURL != null && coverURL.length > 0) ?
            $(`<img class="cover-image" src="${coverURL}" />`) :
            $('<span class="cover-text fa-3x"><i class="fa-solid fa-book-bookmark"></i></span>');
    
    const $title = $(`<span class="search-title">${workResult['title']} by ${workResult['author_name']}</span>`);
    const $addButton = $(`<button class="btn btn-outline-primary btn-sm mx-2 add-book" type="button" data-id="${workResult['key']}" data-isbn="${workResult['isbn']}">Add to List</a>`);
    $addButton.click(addBook);

    if (!workResult['isbn']) {
        console.log(`Result ${workResult['title']} with OLID ${workResult['key']} doesn't have an ISBN}`);
    }

    $div.append($cover);
    $div.append($title);
    $div.append($addButton);

    return $div;
}

if($bookSearch) {
    $bookSearch.on('submit', (evt) => {
        evt.preventDefault();

        const searchTerm = $bookSearch.children('#book-search-term').val();
        performSearch(searchTerm);
    })
}
