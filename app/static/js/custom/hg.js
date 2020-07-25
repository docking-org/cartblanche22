function checkHg(smiles, modal, table, db) {
    $.ajax({
        url: "http://hg.docking.org/substances.txt",
        dataType: 'text',
        data: {"ecfp4_fp-tanimoto-40": smiles},
        success: function (data) {
            if (data.length > 0) {
                let res = data.split('\n')
                let data_ = []
                for (let i = 0; i < res.length; i++) {
                    if (res[i].length > 0) {
                        let temp = res[i].split("\t")
                        let t = {}
                        t['identifier'] = temp[0]
                        t['smiles'] = temp[1]
                        t['db'] = db
                        let base_url = 'http://sw.docking.org/depict/svg?w=%w&h=%h&smi=%s&qry=%q&cols=%c&cmap=%m'
                        let depict_url = base_url.replace("%s", encodeURIComponent(temp[1] + ' ' + temp[0]))
                            .replace("%w", 50).replace("%h", 30);
                        let bg = 'bgcolor=clear&hgstyle=outerglow'
                        t['img'] = depict_url + '&' + bg
                        let cart = JSON.parse(localStorage.getItem('cart'))
                        let index = cart.findIndex(item => item.identifier == temp[0])
                        if (index == -1) {
                            t['val'] = 'Add to Cart'
                            t['class'] = 'btn btn-info'
                        }
                        else {
                            t['val'] = 'Remove'
                            t['class'] = 'btn btn-danger'
                        }
                        data_.push(t)
                    }
                }
                showHg(data_, modal, table)
            }
        },
    })
}

function showHg(data, modal, table) {
    modal.modal('show');
    table.DataTable({
        destroy: true,
        "language": {
            "emptyTable": "No similar molecule in HG database"
        },
         "scrollX": true,
        "scrollY": "450px",
        "paging": false,
        "ordering": false,
        "info": false,
        data: data,
        columns: [
            {
                "mData": function (data) {
                        return  "<button data-hg='true' class='"+ data.class + "'" + "data-img ='"+data.img+"'"+
                            "data-db ='"+data.db+"'"+
                            "data-identifier ='"+data.identifier+"'"+
                            "onclick ='"+'toggleCart(this)'+"'"+
                            ">" + data.val + "</button>"
                    }
            },
            {
                "mData": function (data) {
                        return "<img src ='" + data.img +"' width='150px' height='90px' />"
                    }
            },

                {
                    "mData": function (data) {
                        return data.identifier;
                    }
                },
                {
                    "mData": function (data) {
                        return data.smiles;
                    }
                },

            ],
    }).columns.adjust();

}
