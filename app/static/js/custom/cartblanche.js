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
function cartCheck(is_authenticated, cart_) {
    localStorage.setItem('checkCart', 'False')
    // if user is authenticated, localStorage cart data should match with user's database cart data
    if (localStorage.getItem('cart') == null) {
        let cart = JSON.parse(cart_)
        localStorage.setItem('cart', JSON.stringify(cart))
    }
    if (is_authenticated == 'True') {
        let dbcart = JSON.parse(cart_)
        let totalCart = JSON.parse(localStorage.getItem('cart'))
        for (let i = 0; i < dbcart.length; i++) {
            let index = totalCart.findIndex(item => item.identifier == dbcart[i].identifier)
            if (index == -1) {
                totalCart.push(dbcart[i])
            } else {
                let supplier_db = dbcart[i].supplier
                let supplier_total = totalCart[index].supplier
                for (let j = 0; j < supplier_db.length; j++) {
                    let sup_index = supplier_total.findIndex(supplier =>
                        supplier.cat_name == supplier_db[j].cat_name &&
                        supplier.supplier_code == supplier_db[j].supplier_code &&
                        supplier.quantity == supplier_db[j].quantity && supplier.unit == supplier_db[j].unit)
                    if (sup_index == -1) {
                        supplier_total.push(supplier_db[j])
                    } else {

                        supplier_total[sup_index].purchase = Math.max(supplier_db[j].purchase, supplier_total[sup_index].purchase)
                    }
                }
            }
        }
        localStorage.setItem('cart', JSON.stringify(totalCart))
        $.ajax({
            type: 'POST',
            url: '/saveCartToDb',
            data:  JSON.stringify({
                'totalCart': totalCart,
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                console.log('db saved')
            },
            error: function (data) {
                 console.log('saveCartToDb failed')
            }
        });
        $('#cartCount').html(getCartSize(totalCart))
    }
}