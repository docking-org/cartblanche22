function toggle_nav(formid) {
    var form = $('#' + formid);
    if (form.css('display') === 'none') {
        form.css('display', 'block');
    } else {
        form.css('display', 'none');
    }
}