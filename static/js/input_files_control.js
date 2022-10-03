function delete_file(file_name){
    console.log(document.getElementById('file_' + file_name).style.backgroundColor)
    if (document.getElementById('file_' + file_name).style.backgroundColor === 'red'){
        document.getElementById('file_' + file_name).style.backgroundColor = 'white';
        document.getElementById('checkbox_' + file_name).checked = true;
    } else {
        document.getElementById('file_' + file_name).style.backgroundColor = 'red';
        document.getElementById('checkbox_' + file_name).checked = false;
    }
}

$(document).ready(function() {

    $(".main_input_file").change(function() {

        console.log('next')
        console.log($(this).get(0).files)
        var files_html_ = '<div class="post-file">'

        for (var i = 0; i < $(this).get(0).files.length; ++i) {
            files_html_ += `<a><img src="/static/images/icons/`+file_format($(this).get(0).files[i].name)+
                `.png" width="40px" height="40px" alt="">`+$(this).get(0).files[i].name+`</a>`
        }

        document.getElementById('file_list').innerHTML = files_html_ + '</div>'
    });
});