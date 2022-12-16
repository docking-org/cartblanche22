function vendorRequest(identifier, db, img, btn, hg) {
    $.ajax({
        type: 'POST',
        url: '/chooseVendor',
        data: JSON.stringify({
            'identifier': identifier,
            'db': db,
            'img': img,
            'hg': hg
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

    if (shoppingCart.inCart(identifier)) {
        shoppingCart.removeItemFromCart(identifier);
    }
    else {
        // $(btn).prop('disabled', true)

        let db = $(btn).data('db')
        let img = $(btn).data('img')
        let smile = $(btn).data('smile')
        let hg = $(btn).data('hg')
        let item = {}
        item.identifier = identifier
        item.db = db
        item.img = img
        item.supplier = []
        if (shoppingCart.addItemToCart(identifier, db, smile) === false) {

            $("input[id=" + identifier + "]").attr("checked", false);
            $("#deleteItem").attr("style", "display: none;");
            $("#addItem").attr("style", "display: inline-block");
        }
        if (hg) {
            setTimeout(function () {
                shoppingCart.addVendorToCart(identifier, db, smile, 'HG', 'HG', 10, 'mg', 0, '0', 1, true);
            },
                1000);
        }
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
function updateCartNums() {
    $("#cartCount").html(shoppingCart.countCart())
    $('#total').html(shoppingCart.totalAmountCart())
}