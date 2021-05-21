
function getVendors(bool, identifier, db) {
    let data = [];
    $.ajax({
        type: "GET",
        url: "/getVendors/" + identifier + "/" + db,
        async: bool,
        success: function (res) {
            data = res.vendors;
        },
        error: function (err) {
            return 'failed to get vendors'
        }
    });
    return data;
}

function cartToArray() {
    let cart = JSON.parse(localStorage.getItem('cart'))
    let data = []
    let num = 1
    for (let i = 0; i < cart.length; i++) {
        let item = cart[i]
        if (item.supplier.length == 0) {
            let temp = {}
            temp['img'] = item['img']
            temp['identifier'] = item['identifier']
            temp['cat_name'] = 'not assigned'
            temp['supplier_code'] = 'not assigned'
            temp['quantity'] = 0
            temp['unit'] = 'g'
            temp['price'] = 0
            temp['shipping'] = 'not assigned'
            temp['db'] = item['db']
            temp['purchase'] = 0
            temp['total'] = 0
            temp['num'] = num
            temp['stereochemistry'] = false
            temp['analogs'] = false
            temp['salt'] = false
            num += 1
            data.push(temp)
        }

        for (let j = 0; j < item['supplier'].length; j++) {
            let vendor = item['supplier'][j]
            let temp = {}
            temp['img'] = item['img']
            temp['identifier'] = item['identifier']
            temp['cat_name'] = vendor['cat_name']
            temp['supplier_code'] = vendor['supplier_code']
            temp['quantity'] = vendor['quantity']
            temp['unit'] = vendor['unit']
            temp['price'] = vendor['price']
            temp['shipping'] = vendor['shipping']
            temp['db'] = item['db']
            temp['purchase'] = vendor['purchase']
            temp['total'] = vendor['price'] * vendor['purchase']
            temp['num'] = num
            temp['stereochemistry'] = false
            temp['analogs'] = false
            temp['salt'] = false
            num += 1
            // temp.push(item['img'])
            // temp.push(item['identifier'])
            // temp.push(item['db'])
            // temp.push(vendor['cat_name'])
            // temp.push(vendor['supplier_code'])
            // temp.push(vendor['quantity'] + vendor['unit'])
            // temp.push(vendor['price'])
            // temp.push(vendor['shipping'])
            data.push(temp)
        }
    }
    // console.log(data)
    return data;
}

function updatePurchaseAmount(data, new_purchase) {
    let cart = JSON.parse(localStorage.getItem('cart'))
    // console.log(data)
    for (let i = 0; i < cart.length; i++) {
        if (cart[i]['identifier'] == data['identifier']) {
            for (let j = 0; j < cart[i]['supplier'].length; j++) {
                let vendor = cart[i]['supplier'][j]
                // console.log(vendor)
                if (data['cat_name'] == vendor['cat_name'] && data['supplier_code'] == vendor['supplier_code'] &&
                    data['quantity'] == vendor['quantity'] && data['unit'] == vendor['unit'] &&
                    data['price'] == vendor['price']) {
                    // console.log('olson')
                    vendor['purchase'] = new_purchase
                    data['total'] = (data['price'] * new_purchase).toFixed(2)
                    data['purchase'] = new_purchase
                    // console.log(data)
                    localStorage.setItem('cart', JSON.stringify(cart))
                    $.ajax({
                        type: "PUT",
                        url: '/updateVendor',
                        data: JSON.stringify(data),
                        contentType: "application/json",
                        dataType: 'json',
                        success: (res) => {
                        },
                        error: (res) => {
                            alert(res)
                        }
                    });
                    break;
                }
            }
            break;
        }
    }
    return data;
}

function addVendorToCart(identifier, db, img, vendor) {
    console.log
    data = {
        'identifier': identifier,
        'img': img,
        'db': db,
        'vendor': vendor
    }
    $.ajax({
        type: "POST",
        url: '/addVendor',
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: (res) => {
            console.log(res)
        },
        error: (res) => {
            alert(res)
        }
    });

}

function deleteVendorFromCart(identifier, cat_name, supplier_code, quantity, unit, price) {
    console.log('calling deleteVendorFromCart')
    let cart = JSON.parse(localStorage.getItem('cart'))
    let i = cart.findIndex(obj => obj.identifier == identifier)
    let supplier = cart[i].supplier
    if (supplier.length <= 1) {
        cart.splice(i, 1)
    } else {
        let s = supplier.findIndex(obj => obj.cat_name == cat_name && obj.supplier_code == supplier_code &&
            obj.unit == unit && obj.quantity == quantity && obj.price == price)
        cart[i]['supplier'].splice(s, 1)
    }
    localStorage.setItem('cart', JSON.stringify(cart))
    data = {
        'identifier': identifier,
        'cat_name': cat_name,
        'supplier_code': supplier_code,
        'quantity': quantity,
        'unit': unit,
        'price': price
    }
    // console.log(data)
    $.ajax({
        type: "POST",
        url: '/deleteVendor',
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: (res) => {
            console.log(res)
        },
        error: (res) => {
            alert(res)
        }
    });
}

function deleteVendor(data) {
    let cart = JSON.parse(localStorage.getItem('cart'))
    // console.log(data)

    for (let i = 0; i < cart.length; i++) {
        if (cart[i]['identifier'] == data['identifier']) {
            if (cart[i].supplier.length == 0) {
                console.log(cart)
                cart.splice(i, 1)
                localStorage.setItem('cart', JSON.stringify(cart))
                // console.log(cart)
                $.ajax({
                    type: "POST",
                    url: '/deleteVendor',
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    dataType: 'json',
                    success: (res) => {
                        console.log("deleting vendor from db")
                    },
                    error: (res) => {
                        alert(res)
                    }
                });
            } else {
                for (let j = 0; j < cart[i]['supplier'].length; j++) {
                    let vendor = cart[i]['supplier'][j]
                    // console.log(vendor)
                    if (data['cat_name'] == vendor['cat_name'] && data['supplier_code'] == vendor['supplier_code'] && data['quantity'] == vendor['quantity'] && data['unit'] == vendor['unit'] && data['price'] == vendor['price']) {
                        // console.log('olson')
                        cart[i]['supplier'].splice(j, 1)
                        localStorage.setItem('cart', JSON.stringify(cart))
                        $.ajax({
                            type: "POST",
                            url: '/deleteVendor',
                            data: JSON.stringify(data),
                            contentType: "application/json",
                            dataType: 'json',
                            success: (res) => {
                                console.log("deleting vendor from db")
                            },
                            error: (res) => {
                                alert(res)
                            }
                        });
                        break;
                    }
                }
            }
            break;
        }
    }
}