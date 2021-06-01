function timeoutCheck(is_authenticated) {
    let timeout = localStorage.getItem('timeout');
    if (new Date(timeout) < new Date() && is_authenticated === 'False') {
        shoppingCart.saveShoppingCart([]);
        updateCartNums();
    }
    update();
}


function update() {
    var oneday = new Date();
    oneday.setHours(oneday.getHours() + 24); //one day from now
    // oneday.setMinutes(oneday.getMinutes() + 1); //one day from now
    localStorage.setItem('timeout', oneday);
}


//sync authenticated users cart data in database with localStorage cart data
function loadCartFromDb() {
    $.ajax({
        type: 'POST',
        url: '/saveCartToDbTest',
        data: JSON.stringify({
            'totalCart': shoppingCart.getCart(),
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (result) {
            shoppingCart.loadFromDbCartData(result);

            updateCartNums();
            console.log('loaded dbcart to local cart succesfully');
        },
        error: function (data) {
            console.log('saveCartToDb failed');
        }
    });
}

function loadApplication() {
    let isLoaded = localStorage.getItem('pageLoaded')
    if (isLoaded === null || isLoaded == 'False' || isLoaded === 'false') {
        console.log('loading');
        $.ajax({
            type: "GET",
            url: "/loadApplication",
            success: function (data) {
                localStorage.setItem('pageLoaded', true)
                localStorage.setItem('default_prices', JSON.stringify(data));
            }
        });
    }
}
