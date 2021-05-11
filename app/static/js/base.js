let shoppingCart = (function () {
    // Private methods and properties
    let cart = [];

    function Item(identifier, db, smile, supplier) {
        this.identifier = identifier;
        this.db = db;
        this.smile = smile;
        this.img = "https://sw.docking.org/depict/svg?w=50&h=30h&smi=" + encodeURIComponent(smile) + "&qry=%q&cols=%c&cmap=%m&bgcolor=clear&hgstyle=outerglow";
        this.supplier = supplier;
    }

    function Supplier(cat_name, supplier_code, price, purchase, quantity, unit, shipping) {
        this.cat_name = cat_name;
        this.supplier_code = supplier_code;
        this.price = price;
        this.purchase = purchase;
        this.quantity = quantity;
        this.unit = unit;
        this.shipping = shipping;
    }

    function saveCart() {
        localStorage.setItem("shoppingCart", JSON.stringify(cart));
    }

    function loadCart() {
        cart = JSON.parse(localStorage.getItem("shoppingCart"));
        if (cart === null) {
            cart = [];
            saveCart();
        }
    }

    loadCart();

    // Public methods and properties
    var obj = {};

    obj.getCart = function () {
        console.log('getting cart');
        return cart;
    };

    obj.saveShoppingCart = function (cart_) {
        cart = cart_;
        saveCart();
    };

    obj.addItemToCart = function (identifier, db, smile) {
        let item_index = obj.getItemIndexFromCart(identifier);
        if (item_index !== -1) {
            return;
        }
        console.log("about to addItemToCart:", identifier, db, smile);
        var item = new Item(identifier, db, smile, []);
        cart.push(item);
        obj.writeToDb('/addItem', 'POST', item);
        saveCart();
    };

    obj.addVendorToCart = function (identifier, db, smile, cat_name, supplier_code, quantity, unit, price, shipping, purchase) {
        let sup = new Supplier(cat_name, supplier_code, price, purchase, quantity, unit, shipping);
        let item_index = obj.getItemIndexFromCart(identifier);
        if (item_index !== -1) {
            let supplier_index = obj.getVendorIndexFromCart(identifier, cat_name, supplier_code, quantity, unit, price);
            if (supplier_index === -1) {
                cart[item_index].supplier.push(sup);
                saveCart();
                let data = {
                    'identifier': identifier,
                    'sup': sup,
                };
                obj.writeToDb('/addVendorTest', 'POST', data);
            }
        } else {
            //add item
            obj.addItemToCart(identifier, db, smile);
            setTimeout(function () {
                obj.addVendorToCart(identifier, db, smile, cat_name, supplier_code, quantity, unit, price, shipping, purchase)
            }, 1000);
        }

    };

    obj.removeItemFromCart = function (identifier) { // Removes one item
        let item_index = obj.getItemIndexFromCart(identifier);
        cart.splice(item_index, 1);
        let data = {
            'identifier': identifier
        };
        saveCart();
        obj.writeToDb('/deleteItemTest', 'DELETE', data);
    };
    obj.removeVendorFromCart = function (identifier, cat_name, supplier_code, quantity, unit, price) {
        let item_index = obj.getItemIndexFromCart(identifier);
        if (cart[item_index].supplier.length <= 1) {
            obj.removeItemFromCart(identifier);
        } else {
            let supplier_index = obj.getVendorIndexFromCart(identifier, cat_name, supplier_code, quantity, unit, price);
            cart[item_index].supplier.splice(supplier_index, 1);
            saveCart();
            let data = {
                'identifier': identifier,
                'cat_name': cat_name,
                'supplier_code': supplier_code,
                'price': price,
                'quantity': quantity,
                'unit': unit
            };
            obj.writeToDb('/deleteVendorTest', 'POST', data);
        }
    };

    obj.updatePurchaseAmount = function (identifier, cat_name, supplier_code, quantity, unit, price, new_purchase) {
        let item_index = obj.getItemIndexFromCart(identifier);
        if (item_index !== -1) {
            let supplier_index = obj.getVendorIndexFromCart(identifier, cat_name, supplier_code, quantity, unit, price);
            cart[item_index].supplier[supplier_index].purchase = new_purchase;
            let data = {
                'identifier': identifier,
                'cat_name': cat_name,
                'supplier_code': supplier_code,
                'price': price,
                'quantity': quantity,
                'unit': unit,
                'purchase': new_purchase
            };
            saveCart();
            obj.writeToDb('/updateVendorTest', 'POST', data);
        }
    };


    obj.clearCart = function () {
        cart = [];
        saveCart();
    };


    obj.countCart = function () { // -> return total count
        var totalCount = 0;
        for (let i = 0; i < cart.length; i++) {
            let suppliers = cart[i].supplier;
            if (suppliers.length > 0) {
                for (let s = 0; s < suppliers.length; s++) {
                    totalCount += parseInt(suppliers[s].purchase);
                }
            } else {
                totalCount += 1;
            }

        }
        console.log('from countCart function:', totalCount)
        return totalCount;
    };

    obj.totalAmountCart = function () { // -> return total cost
        var totalCost = 0;
        for (var i in cart) {
            let suppliers = cart[i].supplier;
            for (let s in suppliers) {
                totalCost += suppliers[s].purchase * suppliers[s].price;
            }
        }
        return totalCost.toFixed(2);
    };

    obj.listCart = function () { // -> array of Items
        var cartCopy = [];
        console.log("Listing cart");
        let num = 1;
        for (let i = 0; i < cart.length; i++) {
            let it = cart[i];
            if (it.supplier.length == 0) {
                let temp = {}
                temp['img'] = it['img']
                temp['smile'] = it['smile']
                temp['identifier'] = it['identifier']
                temp['cat_name'] = 'not assigned'
                temp['supplier_code'] = 'not assigned'
                temp['quantity'] = 0
                temp['unit'] = 'g'
                temp['price'] = 0
                temp['shipping'] = 'not assigned'
                temp['db'] = it['db']
                temp['purchase'] = 0
                temp['total'] = 0
                temp['num'] = num
                temp['stereochemistry'] = false
                temp['analogs'] = false
                temp['salt'] = false
                num += 1
                cartCopy.push(temp)
            } else {
                for (let j = 0; j < it.supplier.length; j++) {
                    let vendor = it['supplier'][j]
                    let temp = {}
                    temp['img'] = it['img']
                    temp['smile'] = it['smile']
                    temp['identifier'] = it['identifier']
                    temp['cat_name'] = vendor['cat_name']
                    temp['supplier_code'] = vendor['supplier_code']
                    temp['quantity'] = vendor['quantity']
                    temp['unit'] = vendor['unit']
                    temp['price'] = vendor['price']
                    temp['shipping'] = vendor['shipping']
                    temp['db'] = it['db']
                    temp['purchase'] = vendor['purchase']
                    temp['total'] = (vendor['price'] * vendor['purchase']).toFixed(2);
                    temp['num'] = num
                    temp['stereochemistry'] = false
                    temp['analogs'] = false
                    temp['salt'] = false
                    num += 1
                    cartCopy.push(temp)
                }
            }
        }
        return cartCopy;
    };
    obj.getItemIndexFromCart = function (identifier) {
        return cart.findIndex((e) => {
            return e.identifier == identifier;
        });
    }
    obj.inCart = function (identifier) {
        let i = cart.findIndex((e) => {
            return e.identifier == identifier;
        });
        if (i !== -1) {
            return true
        }
        return false
    }
    obj.getVendorIndexFromCart = function (identifier, cat_name, supplier_code, quantity, unit, price) {
        let item_index = obj.getItemIndexFromCart(identifier)
        return cart[item_index].supplier.findIndex((vendor) => {
            return cat_name == vendor['cat_name'] && supplier_code == vendor['supplier_code'] &&
                quantity == vendor['quantity'] && unit == vendor['unit'] && price == vendor['price']
        })
    }
    obj.inVendor = function (identifier, cat_name, supplier_code, quantity, unit, price) {
        for (let i = 0; i < cart.length; i++) {
            if (cart[i].identifier == identifier) {
                for (let j = 0; j < cart[i].supplier.length; j++) {
                    let vendor = cart[i].supplier[j]
                    if (cat_name == vendor['cat_name'] && supplier_code == vendor['supplier_code'] &&
                        quantity == vendor['quantity'] && unit == vendor['unit'] && price == vendor['price']) {
                        return true;
                    }
                }

            }
        }
        return false;
    }
    obj.loadFromDbCartData = function (dbcart) {
        cart = []
        for (let i = 0; i < dbcart.length; i++) {
            item = dbcart[i]
            let new_sups = []
            for (let j = 0; j < item.supplier.length; j++) {
                s = item.supplier[j]
                new_sups.push(new Supplier(s.cat_name, s.supplier_code, s.price, s.purchase, s.quantity, s.unit, s.shipping))
            }
            cart.push(new Item(item.identifier, item.db, item.smile, new_sups))
        }
        saveCart()
    }
    obj.writeToDb = function (url, method, data) {
        is_authenticated = localStorage.getItem("is_authenticated");
        if (is_authenticated === 'True') {
            $.ajax({
                url: url,
                type: method,
                data: JSON.stringify(
                    {'data': data,}
                ),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (result) {
                    console.log(result);
                },
                error: function (result) {
                    console.log(result);
                },
            });
        }
    }
    // ----------------------------
    return obj;
})();
