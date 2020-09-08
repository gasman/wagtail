function createPageChooser(id, pageTypes, openAtParentId, canChooseRoot, userPerms) {
    var chooserElement = $('#' + id + '-chooser');
    var pageTitle = chooserElement.find('.title');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    var currentState = null;
    if (input.val()) {
        currentState = {
            'id': input.val(),
            'parentId': openAtParentId,
            'title': pageTitle.text(),
            'editUrl': editLink.attr('href')
        };
    }

    function setState(state) {
        if (state) {
            input.val(state.id);
            openAtParentId = state.parentId;
            pageTitle.text(state.adminTitle);
            chooserElement.removeClass('blank');
            editLink.attr('href', state.editUrl);
        } else {
            input.val('');
            openAtParentId = null;
            chooserElement.addClass('blank');
        }

        currentState = state;
    }

    $('.action-choose', chooserElement).on('click', function() {
        var initialUrl = chooserElement.data('chooserUrl');
        if (openAtParentId) {
            initialUrl += openAtParentId + '/';
        }

        var urlParams = {page_type: pageTypes.join(',')};
        if (canChooseRoot) {
            urlParams.can_choose_root = 'true';
        }
        if (userPerms) {
            urlParams.user_perms = userPerms;
        }

        ModalWorkflow({
            url: initialUrl,
            urlParams: urlParams,
            onload: PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
            responses: {
                pageChosen: setState
            }
        });
    });

    $('.action-clear', chooserElement).on('click', function() {setState(null)});

    return {
        'setState': setState,
        'getState': function() {return currentState;},
        'getValue': function() {return input.val();}
    };
}
