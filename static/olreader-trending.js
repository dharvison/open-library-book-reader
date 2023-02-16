function createBookHTML(book, userLists) {
    const title = book.title;
    const author = book.author_name;
    // const cover_i = book.cover_i;
    const cover_key = book.cover_edition_key;
    const lending_olid = book.lending_edition_s ? book.lending_edition_s : book.cover_edition_key;

    const $cardDiv = $(`<div class="card" data-olid=${lending_olid}></div>`);
    if (cover_key != null) {
        $cardDiv.append($(`<img class="card-img-top" src="https://covers.openlibrary.org/b/olid/${cover_key}-M.jpg" alt="Book cover">`));
    } else {
        $cardDiv.append($('<img class="card-img-top" src="/static/images/blank_cover-M.webp" alt="Blank cover">'))
    }

    const $cardBody = $(`<div class="card-body"><h4 class="card-title">${title}</h5><h5 class="card-subtitle">by ${author}</h5>`);
    $cardDiv.append($cardBody);

    const $buttonList = $('<ul class="list-group list-group-flush"></ul>');
    $buttonList.append(createAddListDropdown(lending_olid, userLists));
    $buttonList.append(trendingButtonHTML(`/notes/create?bookid=${lending_olid}`, 'Add Note', 'primary', false));
    $buttonList.append(trendingButtonHTML(`https://openlibrary.org/works/${lending_olid}`, 'View on OpenLibrary.org', 'secondary', true));
    $cardDiv.append($buttonList);

    const $bookDiv = $(`<div class="col-xl-3 col-md-4 col-sm-6 col-12 my-2"></div>`);
    $bookDiv.append($cardDiv);

    return $bookDiv;
}

function trendingButtonHTML(href, text, btnStyle, targetBlank) {
    return $(`<li class="list-group-item"><div class="d-grid gap-2 col-10 mx-auto"><a href="${href}" class="btn btn-${btnStyle} ml-1" ${targetBlank ? 'target="_blank"' : ''}>${text}</a></div></li>`);
}

function createAddListDropdown(olid, userLists) {
    const $listDiv = $('<div class="d-grid gap-2 col-10 mx-auto"></div');
    $listDiv.append($(`<a href="#" id="toggle-${olid}" class="btn btn-primary dropdown-toggle ml-1" role="button" data-bs-toggle="dropdown" aria-expanded="false">Add to List</a>`));

    const $dropdown = $(`<ul class="dropdown-menu add-list" aria-labelledby="toggle-${olid}" data-olid="${olid}"></ul>`);
    $dropdown.append($(`<li><a class="dropdown-item" href="/lists/create?bookid=${olid}">Create New List</a></li>`));
    if (userLists != null && userLists.length > 0) {
        $dropdown.append($('<li><hr class="dropdown-divider"></li>'));
    }
    for (bl of userLists) {
        const $list = $(`<li><a class="dropdown-item add-existing" data-listid="${bl.listId}" href="#">${bl.listTitle}</a></li>`);
        $list.click(addBookToList);
        $dropdown.append($list);
    }
    $listDiv.append($dropdown);

    const $listGroup = $('<li class="list-group-item"></li>');
    $listGroup.append($listDiv);
    return $listGroup;
}


async function loadTrending(type, $trendingDiv) {
    $trendingDiv.find('#search-loading').show();
    trendingBooks = await axios.get(`/trending/fetch?type=${type}`);
    userLists = trendingBooks.data.user_lists;
    for (book of trendingBooks.data.trending_books) {
        $trendingDiv.append(createBookHTML(book, userLists));
    }
    $trendingDiv.find('#search-loading').hide();
}

if ($('#trending-recent').length) {
    loadTrending('recent', $('#trending-recent'));
}

if ($('#trending-new').length) {
    loadTrending('new', $('#trending-new'));
}

if ($('#trending-popular').length) {
    loadTrending('popular', $('#trending-popular'));
}