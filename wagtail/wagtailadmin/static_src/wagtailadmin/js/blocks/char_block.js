(function($) {
    window.CharBlock = function(opts) {
        return function(elementPrefix, instanceOpts) {
            if (instanceOpts && instanceOpts.sequence && instanceOpts.sequence.canCloneMembers) {
                var $input = $('#' + elementPrefix);
                $input.keypress(function(event) {
                    if (event.which == 13) {
                        event.preventDefault();
                        instanceOpts.sequence.cloneMemberAfter(instanceOpts.sequenceMember);
                    }
                });
            }
        };
    };
})(jQuery);
