
function displayFlashMessage(message, category) {
    $('#flash-container').append(
        `<div class="alert alert-${category} alert-dismissible fade show">
        ${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`);
}

function displayErrMsg(err, type) {
    console.log(err, type);
    displayFlashMessage(err, type);
}

function createAddListDropdownHTML($container, olid, userLists, btnStyle='btn-primary') {
    $container.append($(`<a href="#" id="toggle-${olid}" class="btn ${btnStyle} dropdown-toggle ml-1" role="button" data-bs-toggle="dropdown" aria-expanded="false">Add to List</a>`));

    const $dropdown = $(`<ul class="dropdown-menu add-list" aria-labelledby="toggle-${olid}" data-olid="${olid}"></ul>`);

    if ($('#createListModal').length) {
        const createModelButton = $(`<li><a class="dropdown-item create-list" data-bs-toggle="modal" data-bs-target="#createListModal">Create New List</a></li>`);
        $dropdown.append(createModelButton);
    } else {
        $dropdown.append($(`<li><a class="dropdown-item" href="/lists/create?bookid=${olid}">Create New List</a></li>`));
    }
    if (userLists != null && userLists.length > 0) {
        $dropdown.append($('<li><hr class="dropdown-divider"></li>'));
    }
    for (bl of userLists) {
        const $list = $(`<li><a class="dropdown-item add-existing" data-listid="${bl.listId}" href="#">${bl.listTitle}</a></li>`);
        $list.click(addBookToList);
        $dropdown.append($list);
    }
    $container.append($dropdown);
}
