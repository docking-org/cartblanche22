let length = 1000;

function loadData(url) {
    url = url.concat(length, '&draw=0');
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            populateDataTable(response.data)
        },
        error: function (xhr) {
            alert("Not found!")
        }
    });
}

function populateDataTable(data) {
    console.log("populating data table ...");
    //clear the table before populating it with more data
    $('#example').DataTable().clear();
    console.log(data)
    $.each(data, function (i, item) {
        $('#example').dataTable().fnAddData([
            item[0].id,
            item[0].mf,
            item[0].mw,
        ])
    });
}
