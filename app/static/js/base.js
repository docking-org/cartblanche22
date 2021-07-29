let shoppingCart = (function () {
    // Private methods and properties
    let cart = [];
    let default_prices = [];

    function Item(identifier, db, smile, supplier) {
        this.identifier = identifier;
        this.db = db;
        this.smile = smile;
        this.img = "https://sw.docking.org/depict/svg?w=50&h=30h&smi=" + encodeURIComponent(smile) + "&qry=%q&cols=%c&cmap=%m&bgcolor=clear&hgstyle=outerglow";
        this.supplier = supplier;
    }

    function Supplier(cat_name, supplier_code, price, purchase, quantity, unit, shipping, assigned) {
        this.cat_name = cat_name;
        this.supplier_code = supplier_code;
        this.price = price;
        this.purchase = purchase;
        this.quantity = quantity;
        this.unit = unit;
        this.shipping = shipping;
        this.assigned = assigned;
    }

    function saveCart() {
        console.log('save');
        localStorage.setItem("shoppingCart", JSON.stringify(cart));
        updateCartNums();
    }

    function savePrices() {
        console.log('saving prices', default_prices)
        localStorage.setItem("default_prices", JSON.stringify(default_prices));

    }

    function loadCart() {
        cart = JSON.parse(localStorage.getItem("shoppingCart"));
        if (cart === null) {
            cart = [];
            saveCart();
        }
        default_prices = JSON.parse(localStorage.getItem("default_prices"));
        if(default_prices === null){
            localStorage.setItem('pageLoaded', false);
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

    obj.addItemToCart = function (identifier, db, smile, supplier = null, catalog = null) {
        let item_index = obj.getItemIndexFromCart(identifier);
        if (item_index !== -1) {
            return;
        }
        let vendors = [];
        console.log(default_prices)
        if (db === 'zinc22' && catalog !== null) {
            console.log('catalog', catalog);
            console.log('supplier', supplier);
            for (let s = 0; s < catalog.length; s++) {
                let sup = catalog[s].catalog_name;
                console.log('sup', sup)
                let def_price = null;
                if (sup.toLowerCase().includes('mcule')) {
                    def_price = default_prices['mcule'];
                } else if (sup.toLowerCase().includes('wuxi')) {
                    def_price = default_prices['wuxi'];

                } else if (sup.toLowerCase().includes('m')) {
                    def_price = default_prices['Enamine_M'];
                } else if (sup.toLowerCase().includes('s')) {
                    def_price = default_prices['Enamine_S'];
                } else {
                    def_price = default_prices['mcule'];
                }
                console.log(def_price)
                if (def_price !== null) {
                    let assigned = false
                    let purchase = 0
                    if (s === 0) {
                        assigned = true
                        purchase = 1
                    }
                    let vendor = new Supplier(def_price.cat_name, supplier[s], def_price.price, purchase, def_price.quantity, def_price.unit, def_price.shipping, assigned)
                    console.log('supplier created', vendor)
                    vendors.push(vendor)
                }
            }
        }
        console.log("about to addItemToCart:", identifier, db, smile, vendors);
        var item = new Item(identifier, db, smile, vendors);
        cart.push(item);
        obj.writeToDb('/addItem', 'POST', item);
        saveCart();
    };

    obj.addVendorToCart = function (identifier, db, smile, cat_name, supplier_code, quantity, unit, price, shipping, purchase, assigned = false) {
        let sup = new Supplier(cat_name, supplier_code, price, purchase, quantity, unit, shipping, assigned);
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

    obj.assignvendors = function (identifier, supplier) {
        let item_index = obj.getItemIndexFromCart(identifier);
        let vendors = [];
        console.log(default_prices)
        if(default_prices.length === 0){
            default_prices = JSON.parse(localStorage.getItem("default_prices"))
        }
        for (let s = 0; s < supplier.length; s++) {
            let sup = supplier[s];
            let def_price = null;
            if (sup.toLowerCase().includes('mcule')) {
                def_price = default_prices['mcule'];
            } else if (sup.toLowerCase().includes('wuxi')) {
                def_price = default_prices['wuxi'];

            } else if (sup.toLowerCase().includes('m_')) {
                def_price = default_prices['Enamine_M'];
            } else if (sup.toLowerCase().includes('s_')) {
                def_price = default_prices['Enamine_S'];
            } else {
                def_price = default_prices['mcule'];
            }
            console.log(def_price)
            if (def_price !== null) {
                let assigned = false
                let purchase = 0
                if (s === 0) {
                    assigned = true
                    purchase = 1
                }
                let vendor = new Supplier(def_price.cat_name, supplier[s], def_price.price, purchase, def_price.quantity, def_price.unit, def_price.shipping, assigned)
                console.log('supplier created', vendor)
                vendors.push(vendor)
            }

        }
        cart[item_index].supplier = vendors
        saveCart();
    }

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
        console.log("Listing cart", cart);
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
                    if (it.supplier[j].assigned === true) {
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
                        temp['total'] = (parseInt(vendor['price']) * parseInt(vendor['purchase'])).toFixed(2);
                        temp['num'] = num
                        temp['stereochemistry'] = false
                        temp['analogs'] = false
                        temp['salt'] = false
                        num += 1
                        cartCopy.push(temp)
                    }
                }
            }
        }
        console.log(cartCopy)
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
    obj.loadFromDbCartData = function (data) {
        let dbcart = data.cart
        default_prices = data.default_prices
        console.log('dbcart', dbcart)
        savePrices()
        cart = []
        for (let i = 0; i < dbcart.length; i++) {
            item = dbcart[i]
            let new_sups = []
            for (let j = 0; j < item.supplier.length; j++) {
                s = item.supplier[j]
                new_sups.push(new Supplier(s.cat_name, s.supplier_code, s.price, s.purchase, s.quantity, s.unit, s.shipping, s.assigned))
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
