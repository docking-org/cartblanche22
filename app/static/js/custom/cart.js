function vendorRequest(identifier, db, img, btn, hg) {
    $.ajax({
            type: 'POST',
            url: '/chooseVendor',
            data: JSON.stringify({
                'identifier': identifier,
                'db': db,
                'img': img,
                'hg':hg
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                let assigned = result.assigned
                result = result.vendor
                if (assigned) {
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
function toggleCart(btn) {
    localStorage.setItem('cartCheck', true)
    // let cart = JSON.parse(localStorage.getItem('cart'))
    let identifier = $(btn).data('identifier')
    if (btn.getAttribute('class') == 'btn btn-info') {
        // $(btn).prop('disabled', true)
        $(btn).html('Remove')
        $(btn).attr('class', 'btn btn-danger')
        let db = $(btn).data('db')
        let img = $(btn).data('img')
        let smile = $(btn).data('smile')
        let hg = $(btn).data('hg')
        let item = {}
        item.identifier = identifier
        item.db = db
        item.img = img
        item.supplier = []
        shoppingCart.addItemToCart(identifier, db, smile);
        if(hg) {
            setTimeout(function(){
                shoppingCart.addVendorToCart(identifier, db, smile,'HG', 'HG', 10, 'mg', 0, '0', 1, true); },
                1000);
        }
        // vendorRequest(identifier, db, img, btn, $(btn).data('hg'))
        // cart.push(item)
        // localStorage.setItem('cart', JSON.stringify(cart))
        // let count = parseInt($('#cartCount').html()) + 1


    }
    else {
        // $(btn).prop('disabled', true)
        // for (i = 0; i < cart.length; i++) {
        //     if (cart[i].identifier == $(btn).data('identifier')) {
        //         cart.splice(i, 1)
        //     }
        // }
        // localStorage.setItem('cart', JSON.stringify(cart))
        // $(btn).html('Add To Cart')
        // $(btn).attr('class', 'btn btn-info')
        // $('#cartCount').html(getCartSize(cart))
        // if (localStorage.getItem('is_authenticated') === 'True') {
        //     $.ajax({
        //         url: '/deleteItem/' + $(btn).data('identifier'),
        //         type: 'DELETE',
        //         success: function (result) {
        //         }
        //     });
        // }
        shoppingCart.removeItemFromCart(identifier);
          $(btn).html('Add To Cart')
        $(btn).attr('class', 'btn btn-info')
        // $(btn).prop('disabled', false)

    }
    $('#cartCount').html(shoppingCart.countCart());
    return false;
}

// function chooseVendor(identifier, db, cart) {
//     console.log('autochoosing vendor')
//     $.ajax({
//         type: 'POST',
//         url: '/chooseVendor',
//         data: JSON.stringify({
//             'identifier': identifier,
//             'db': db
//         }),
//         contentType: "application/json; charset=utf-8",
//         dataType: "json",
//         success: function (result) {
//             console.log("printing chosen vendor")
//             console.log(result)
//             let vendor = {
//                 'cat_name': result['cat_name'],
//                 'price': result['price'],
//                 'purchase': result['purchase'],
//                 'quantity': result['quantity'],
//                 'shipping': result['shipping'],
//                 'supplier_code': result['supplier_code'],
//                 'unit': result['unit']
//             }
//             let item = {
//                 'identifier': identifier,
//                 'db': db,
//                 'img': img,
//                 'supplier': [vendor]
//             }
//             let cart = JSON.parse(localStorage.getItem('cart'))
//             cart.push(item)
//             localStorage.setItem(JSON.stringify(cart))
//         },
//         error: function (data) {
//             alert(data);
//         }
//     });
// }
function getCartSize(cart_) {
    console.log('getCartSize');
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
function updateCartNums(){
    $("#cartCount").html(shoppingCart.countCart())
    $('#total').html(shoppingCart.totalAmountCart())
}