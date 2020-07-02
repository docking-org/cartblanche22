function toggleCart(btn) {
    let cart = JSON.parse(localStorage.getItem('cart'))
    if (btn.getAttribute('class') == 'btn btn-info') {
        let identifier = btn.id
        let db = btn.getAttribute('db')
        let img = btn.getAttribute('img')
        let item = {
            'identifier': identifier,
            'db': db,
            'img': img,
            'supplier': [],
            'hg' : false,
        }
        cart.push(item)
        localStorage.setItem('cart', JSON.stringify(cart))
        let count = parseInt($('#cartCount').html()) + 1
        $('#cartCount').html(count)
        $(btn).html('Remove')
        $(btn).attr('class', 'btn btn-danger')
        $(btn).prop('disabled', true)
        $.ajax({
            type: 'POST',
            url: '/chooseVendor',
            data: JSON.stringify({
                'identifier': identifier,
                'db': db,
                'img': img
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                let assigned = result.assigned
                result = result.vendor
                if (assigned) {
                    console.log('iishee orood bn')
                    let vendor = {
                        'cat_name': result['cat_name'],
                        'price': result['price'],
                        'purchase': result['purchase'],
                        'quantity': result['quantity'],
                        'shipping': result['shipping'],
                        'supplier_code': result['supplier_code'],
                        'unit': result['unit']
                    }
                    let item = {
                        'identifier': identifier,
                        'db': db,
                        'img': img,
                        'supplier': [vendor]
                    }
                    let cart = JSON.parse(localStorage.getItem('cart'))
                    for (let i = 0; i < cart.length; i++) {
                        if (cart[i].identifier == identifier) {
                            console.log('deleting---' + cart[i])
                            cart.splice(i, 1)
                        }
                    }
                    cart.push(item)
                    localStorage.setItem('cart', JSON.stringify(cart))

                }

                $(btn).prop('disabled', false)
            },
            error: function (data) {
                alert(data);
            }
        });
    }
    else {
        $(btn).prop('disabled', true)
        for (i = 0; i < cart.length; i++) {
            if (cart[i].identifier == btn.id) {
                cart.splice(i, 1)
            }
        }
        localStorage.setItem('cart', JSON.stringify(cart))
        $(btn).html('Add To Cart')
        $(btn).attr('class', 'btn btn-info')
        $('#cartCount').html(getCartSize(cart))
        if (localStorage.getItem('is_authenticated') === 'True') {
            $.ajax({
                url: '/deleteItem/' + btn.id,
                type: 'DELETE',
                success: function (result) {
                }
            });
        }

        $(btn).prop('disabled', false)

    }
    return false;
}

function chooseVendor(identifier, db, cart) {
    console.log('autochoosing vendor')
    $.ajax({
        type: 'POST',
        url: '/chooseVendor',
        data: JSON.stringify({
            'identifier': identifier,
            'db': db
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (result) {
            console.log("printing chosen vendor")
            console.log(result)
            let vendor = {
                'cat_name': result['cat_name'],
                'price': result['price'],
                'purchase': result['purchase'],
                'quantity': result['quantity'],
                'shipping': result['shipping'],
                'supplier_code': result['supplier_code'],
                'unit': result['unit']
            }
            let item = {
                'identifier': identifier,
                'db': db,
                'img': img,
                'supplier': [vendor]
            }
            let cart = JSON.parse(localStorage.getItem('cart'))
            cart.push(item)
            localStorage.setItem(JSON.stringify(cart))
        },
        error: function (data) {
            alert(data);
        }
    });
}
function getCartSize(cart_) {
    // let cart = JSON.parse(localStorage.getItem('cart'))
    let count = 0
    for (let i = 0; i < cart_.length; i++) {
        count += cart_[i]['supplier'].length
        if (cart_[i].supplier.length == 0) {
            count += 1
        }
    }
    return count;
}