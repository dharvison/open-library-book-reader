const $bookListBooks = $('#booklist-books');

async function addBook(evt) {
    const workId = $(evt.target).data('id');
    const isbn = $(evt.target).data('isbn');
    const listId = $bookSearch.data('listid');
    const result = await axios.post(`/lists/${listId}/add`, {workId: workId, isbn: isbn});
    
    if (result.data['err'] != null) {
        const {err, type} = result.data;
        console.log(err, type);
        displayFlashMessage(err, type);
    } else {
        addToBooklist(result.data);
    }
}

function addToBooklist(book) {
    if ($bookListBooks) {
        $bookListBooks.children('#empty-list-msg').hide();
        const $div = $('<div class="list-book"></div')
        const $cover = (book.cover_url != null && book.cover_url.length > 0) ?
            $(`<img class="cover-image" src="${book.cover_url}-S.jpg" />`) :
            $('<span class="cover-text fa-3x"><i class="fa-solid fa-book-bookmark"></i></span>');
        const $title = $(`<span class="book-title"><a href="/books/${book.olid}">${book.title}</a> by ${book.author} <a href="#" class="link-danger" data-id="${book.olid}" title="Remove"><i class="fa-regular fa-circle-xmark"></i></span>`);
        $div.append($cover);
        $div.append($title);
        $bookListBooks.append($div);
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
        $link.closest(".list-book").remove();
    }
}

async function addNote(evt) {
    const workId = $(evt.target).data('id');
    const isbn = $(evt.target).data('isbn');
    const result = await axios.post(`/notes/create`, {workId: workId, isbn: isbn});
    
    if (result.data['err'] != null) {
        const {err, type} = result.data;
        console.log(err, type);
        displayFlashMessage(err, type);
    } else {
        addToBooklist(result.data);
    }
}

async function addBookToList(evt) {
    const $result = $(evt.target);
    const listId = $result.data('listid');
    const workId = $result.closest('.add-list').data('olid');

    const result = await axios.post(`/lists/${listId}/add`, {workId: workId, isbn: null});
    
    if (result.data['err'] != null) {
        const {err, type} = result.data;
        console.log(err, type);
        displayFlashMessage(err, type);
    } else {
        displayFlashMessage(`Added ${result.data.title} to <a href="/lists/${listId}">list</a>`, 'success');
    }
}

if ($bookListBooks) {
    $bookListBooks.on('click', '.fa-circle-xmark', removeBook);
}

if ($('.add-list')) {
    $('.add-list').on('click', '.add-existing', addBookToList);
}