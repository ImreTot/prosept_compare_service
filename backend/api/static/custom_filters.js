var $ = jQuery.noConflict();

(function ($) {
    $.fn.get_item = function (index) {
        return this[index];
    };
})(jQuery);
