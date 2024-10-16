function ajaxifyDocumentUploadForm(modal) {
    $('form.document-upload', modal.body).on('submit', function() {
        var formdata = new FormData(this);

        $.ajax({
            url: this.action,
            data: formdata,
            processData: false,
            contentType: false,
            type: 'POST',
            dataType: 'text',
            success: modal.loadResponseText,
            error: function(response, textStatus, errorThrown) {
                var message = jsonData['error_message'] + '<br />' + errorThrown + ' - ' + response.status;
                $('#upload', modal.body).append(
                    '<div class="help-block help-critical">' +
                    '<strong>' + jsonData['error_label'] + ': </strong>' + message + '</div>');
            }
        });

        return false;
    });
}

DOCUMENT_CHOOSER_MODAL_ONLOAD_HANDLERS = {
    'chooser': function(modal, jsonData) {
        function ajaxifyLinks (context) {
            $('a.document-choice', context).on('click', function() {
                modal.loadUrl(this.href);
                return false;
            });

            $('.pagination a', context).on('click', function() {
                loadResults(this.href);
                return false;
            });

            $('a.upload-one-now').on('click', function(e) {
                // Set current collection ID at upload form tab
                let collectionId = $('#collection_chooser_collection_id').val();
                if (collectionId) {
                  $('#id_document-chooser-upload-collection').val(collectionId);
                }

                // Select upload form tab
                $('a[href="#upload"]').tab('show');
                e.preventDefault();
            });
        };

        var searchForm = $('form.document-search', modal.body);
        var searchUrl = searchForm.attr('action');
        var request;
        function search() {
            loadResults(searchUrl, searchForm.serialize());
            return false;
        };

        function loadResults(url, data) {
            var opts = {
                url: url,
                success: function(data, status) {
                    request = null;
                    $('#search-results').html(data);
                    ajaxifyLinks($('#search-results'));
                },
                error: function() {
                    request = null;
                }
            };
            if (data) {
                opts.data = data;
            }
            request = $.ajax(opts);
        }

        ajaxifyLinks(modal.body);
        ajaxifyDocumentUploadForm(modal);

        $('form.document-search', modal.body).on('submit', search);

        $('#id_q').on('input', function() {
            if (request) {
                request.abort();
            }
            clearTimeout($.data(this, 'timer'));
            var wait = setTimeout(search, 50);
            $(this).data('timer', wait);
        });

        $('#collection_chooser_collection_id').on('change', search);
    },
    'document_chosen': function(modal, jsonData) {
        modal.respond('documentChosen', jsonData['result']);
        modal.close();
    },
    'reshow_upload_form': function(modal, jsonData) {
        $('#upload', modal.body).html(jsonData.htmlFragment);
        ajaxifyDocumentUploadForm(modal);
    }
};
