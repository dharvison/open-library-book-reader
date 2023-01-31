$bookSearch = $('#book-search');
$resultsDisplay = $('#search-results-display');

if($bookSearch) {

    async function performSearch(searchTerm) {
        searchResults = await axios.get(`/search/${searchTerm}`)
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
                $('<span class="cover-text"><i class="fa-solid fa-book-bookmark"></i></span>'); // TODO build links to OL for books and authors?
        
        $title = $(`<span class="search-title">${workResult['title']} by ${workResult['author_name']}</span>`);
        
        $addButton = $(`<button class="btn btn-outline-primary btn-sm mx-2 add-book" type="button" data-id="${workResult['lending_edition_s']}">Add to List</a>`);
        $addButton.click(addBook);

        $div.append($cover);
        $div.append($title);
        $div.append($addButton);

        return $div;
    }

    $bookSearch.on('submit', (evt) => {
        evt.preventDefault();

        const searchTerm = $bookSearch.children('#book-search-term').val();
        performSearch(searchTerm);
    })

    async function addBook(evt) {
        const workId = $(evt.target).data('id');
        const listId = $bookSearch.data('listid');
        const result = await axios.post(`/lists/${listId}/add`, {workId: workId});
        console.log(result);
        updateBooklist(result);
    }

    function updateBooklist(book) {
        // TODO book will contain the data to add a <li> to the list!
        console.log($('#booklist-books'));
        book['title'] = 'Sample Title!';

        const $bookListBooks = $('#booklist-books');
        $bookListBooks.children('#empty-list-msg').hide();
        if ($bookListBooks) {
            $bookListBooks.append($(`<li><a href="#">${book.title}</a></li>`))
        }
    }
}