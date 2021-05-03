function timeoutCheck(is_authenticated, cart_) {
    let timeout = localStorage.getItem('timeout');
    if (new Date(timeout) < new Date() && is_authenticated == 'False') {
        let cart = JSON.parse(cart_)
        localStorage.setItem('cart', JSON.stringify(cart))
        $('#cartCount').html('0')
    }
    update()
}

function update() {
    console.log('updating timeout')
    var oneday = new Date();
    oneday.setHours(oneday.getHours() + 24); //one day from now
    // oneday.setMinutes(oneday.getMinutes() + 1); //one day from now
    localStorage.setItem('timeout', oneday)
}


//used
//sync authenticated users cart data in database with localStorage cart data
function cartCheck(is_authenticated) {
    localStorage.setItem('checkCart', 'False');
    $.ajax({
            type: 'POST',
            url: '/saveCartToDbTest',
            data:  JSON.stringify({
                'totalCart': shoppingCart.getCart(),
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                console.log(result);
                shoppingCart.dbCart(result);
            },
            error: function (data) {
                 console.log('saveCartToDb failed')
            }
        });
    // if user is authenticated, localStorage cart data should match with user's database cart data
    // if (localStorage.getItem('cart') == null) {
    //     let cart = JSON.parse(cart_)
    //     localStorage.setItem('cart', JSON.stringify(cart))
    // }
    // if (is_authenticated == 'True') {
    //     console.log(cart_)
    //     let dbcart = JSON.parse(cart_);
    //     console.log(dbcart)
    //     // let totalCart = JSON.parse(localStorage.getItem('cart'))
    //     let totalCart = shoppingCart.getCart();
    //     for (let i = 0; i < dbcart.length; i++) {
    //         let item = dbcart[i];
    //         if (shoppingCart.inCart(item.identifier)){
    //             let suppliers = item.supplier;
    //             for(let s = 0; s < suppliers.length; s++){
    //                 let sup = suppliers[s];
    //                 if(!shoppingCart.inVendor(item.identifier, sup.cat_name, sup.supplier_code, sup.quantity, sup.unit, sup.price)){
    //                     shoppingCart.addVendorToCart(item.identifier, sup.cat_name, sup.supplier_code,sup.price,sup.purchase, sup.quantity, sup.unit, sup.shipping);
    //                 }
    //                 else{
    //                     shoppingCart.updatePurchaseAmount(item.identifier, sup.cat_name, sup.supplier_code, sup.quantity, sup.unit, sup.price, sup.purchase);
    //                 }
    //             }
    //         }
    //         else{
    //             shoppingCart.addItemToCart(item.identifier, item.db, item.smile);
    //         }
    //     }
    //     // localStorage.setItem('cart', JSON.stringify(totalCart))
    //     // $.ajax({
    //     //     type: 'POST',
    //     //     url: '/saveCartToDb',
    //     //     data:  JSON.stringify({
    //     //         'totalCart': shoppingCart.getCart(),
    //     //     }),
    //     //     contentType: "application/json; charset=utf-8",
    //     //     dataType: "json",
    //     //     success: function (result) {
    //     //         console.log('db saved')
    //     //     },
    //     //     error: function (data) {
    //     //          console.log('saveCartToDb failed')
    //     //     }
    //     // });
    //     $('#cartCount').html(getCartSize(totalCart))
    // }
}