/*jshint esversion: 6 */
let shoppingCart = (function () {
    "use strict";
    // Private methods and properties
    let cart = [];
    let default_prices = [];
    let size = 500;

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
        localStorage.setItem("shoppingCart", JSON.stringify(cart));
        updateCartNums();
    }

    function savePrices() {
        localStorage.setItem("default_prices", JSON.stringify(default_prices));
    }

    function loadCart() {
        cart = JSON.parse(localStorage.getItem("shoppingCart"));
        if (cart === null) {
            cart = [];
            saveCart();
        }
        default_prices = JSON.parse(localStorage.getItem("default_prices"));
        if (default_prices === null) {
            localStorage.setItem('pageLoaded', false);
        }
    }

    loadCart();
    // Public methods and properties
    var obj = {};
    obj.getCart = function () {
        return cart;
    };
    obj.saveShoppingCart = function (cart_) {
        cart = cart_;
        saveCart();
    };

    obj.getPossibleVendors = function (db, catalog, supplier_codes) {
        console.log('getPossibleVendors', catalog, supplier_codes);
        let vendors = [];
        let minPrice = Number.MAX_VALUE;
        let minPriceIndex = 0;
        let curIndex = 0;
        
        if (db === 'zinc22' && catalog !== null) {
            for (let s = 0; s < catalog.length; s++) {
                console.log(catalog[s])
                let short_name = catalog[s].catalog_name.toLowerCase();
                let def_price = null;
                if (!short_name.includes('zinc')) {
                    if (short_name === 'wuxi') {
                        let supplier_code = supplier_codes[s].substring(0, 4);
                        if (['WXCD', 'WXDL'].includes(supplier_code)) {
                            def_price = default_prices[supplier_code];
                        } else {
                            def_price = default_prices[short_name];
                        }
                    } else {
                        def_price = default_prices[short_name];
                    }
                }
                if ((def_price !== undefined) && (def_price!== null) ){
                    let assigned = false;
                    let purchase = 0;
                    console.log(def_price)
                    if (def_price.price < minPrice) {
                        minPriceIndex = curIndex;
                    }
                    let vendor = new Supplier(def_price.cat_name, supplier_codes[s], def_price.price, purchase,
                                              def_price.quantity, def_price.unit, def_price.shipping, assigned);
                    vendors.push(vendor);
                    curIndex++;
                }
            }
        }
        if (vendors.length > 0) {
            vendors[minPriceIndex].assigned = true;
            vendors[minPriceIndex].purchase = 1;
        }
        return vendors;
    };

    obj.addAllItem = function (datas) {
        console.log('from addAll button ', datas.length);
        let tempCart = []
        for(let i = 0; i < datas.length; i++){
            let data = datas[i];
            if(cart.length >= size){
                alert('shopping cart size limit : ' + size);
                break;
            }
            if(!obj.inCart(data.zinc_id)){
                let db = data.hasOwnProperty('db') ? data.db : 'zinc22';
                let catalog = data.hasOwnProperty('catalogs') ? data.catalogs : [];
                let supplier_codes = data.hasOwnProperty('supplier_code') ? data.supplier_code : [];
                let smiles = data.hasOwnProperty('smiles' ) ? data.smiles : data.hitMappedSmiles;
                let vendors = obj.getPossibleVendors(db, catalog, supplier_codes);
                var item = new Item(data.zinc_id, db, smiles, vendors);
                console.log('item created', item);
                tempCart.push(item)
                cart.push(item);
                saveCart();
            }
        };
        obj.writeToDb('/addAllItem', 'POST', tempCart);
    };

    obj.deleteAllItem = function (datas) {
        console.log('from addAll button ', datas.length);
        let ids = [];
        for(let i = 0; i < datas.length; i++){
            let data = datas[i];
            let item_index = obj.getItemIndexFromCart(data.zinc_id);
            if(item_index !== -1){
                ids.push(data.zinc_id);
                cart.splice(item_index, 1);
            }
            // let data = {
            //     'identifier': identifier
            // };
            saveCart();
        }
        obj.writeToDb('/deleteMultItem', 'DELETE', ids);
    };

    obj.addItemToCart = function (identifier, db, smile, supplier=null, catalog = null) {
        if (cart.length < size) {
            let item_index = obj.getItemIndexFromCart(identifier);
            if (item_index !== -1) {
                return;
            }
            let vendors;
            if(db !== 'zinc20'){
                vendors = obj.getPossibleVendors(db, catalog, supplier);
            }
            else{
                vendors = catalog;
            }
            
            console.log("about to addItemToCart:", identifier, db, smile, vendors);
            var item = new Item(identifier, db, smile, vendors);
            cart.push(item);
            obj.writeToDb('/addItem', 'POST', item);
            saveCart();
        }
        else{
            alert('shopping cart size limit : ' + size);
        }
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
                obj.addVendorToCart(identifier, db, smile, cat_name, supplier_code, quantity, unit, price, shipping, purchase);
            }, 1000);
        }

    };

    obj.assignvendors = function (identifier, supplier, catalog) {
        let item_index = obj.getItemIndexFromCart(identifier);
        let vendors = obj.getPossibleVendors('zinc22', catalog, supplier);
        if (default_prices.length === 0) {
            default_prices = JSON.parse(localStorage.getItem("default_prices"));
        }
        cart[item_index].supplier = vendors;
        saveCart();
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
    obj.deleteAllFromCart = function () {
        obj.clearCart();
        obj.writeToDb('/clearCart', 'POST', 'clear');
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
        return totalCount;
    };

    obj.totalAmountCart = function () { // -> return total cost
        let totalCost = 0;
        for (let i in cart) {
            let suppliers = cart[i].supplier;
            for (let s in suppliers) {
                totalCost += suppliers[s].purchase * suppliers[s].price;
            }
        }
        return totalCost.toFixed(2);
    };

    obj.listCart = function () { // -> array of Items
        var cartCopy = [];
        let num = 1;
        console.log(cart);
        for (let i = 0; i < cart.length; i++) {
            let it = cart[i];
            if (it.supplier.length == 0) {
                let temp = {};
                temp.img = it.img;
                temp.smile = it.smile;
                temp.identifier = it.identifier;
                temp.cat_name = 'not assigned';
                temp.supplier_code = 'not assigned';
                temp.quantity = 0;
                temp.unit = 'g';
                temp.price = 0;
                temp.shipping = 'not assigned';
                temp.db = it.db;
                temp.purchase = 0;
                temp.total = 0;
                temp.num = num;
                temp.stereochemistry = false;
                temp.analogs = false;
                temp.salt = false;
                num += 1;
                cartCopy.push(temp);
            } else {
                for (let j = 0; j < it.supplier.length; j++) {
                    if (it.supplier[j].assigned === true) {
                        let vendor = it.supplier[j];
                        let temp = {};
                        temp.img = it.img;
                        temp.smile = it.smile;
                        temp.identifier = it.identifier;
                        temp.cat_name = vendor.cat_name;
                        temp.supplier_code = vendor.supplier_code;
                        temp.quantity = vendor.quantity;
                        temp.unit = vendor.unit;
                        temp.price = vendor.price;
                        temp.shipping = vendor.shipping;
                        temp.db = it.db;
                        temp.purchase = vendor.purchase;
                        temp.total = (parseInt(vendor.price) * parseInt(vendor.purchase)).toFixed(2);
                        temp.num = num;
                        temp.stereochemistry = false;
                        temp.analogs = false;
                        temp.salt = false;
                        num += 1;
                        cartCopy.push(temp);
                    }
                }
            }
        }
        return cartCopy;
    };
    obj.getItemIndexFromCart = function (identifier) {
        return cart.findIndex((e) => {
            return e.identifier === identifier;
        });
    };
    obj.inCart = function (identifier) {
        let i = cart.findIndex((e) => {
            return e.identifier === identifier;
        });
        if (i !== -1) {
            return true;
        }
        return false;
    };
    obj.getVendorIndexFromCart = function (identifier, cat_name, supplier_code, quantity, unit, price) {
        let item_index = obj.getItemIndexFromCart(identifier);
        return cart[item_index].supplier.findIndex((vendor) => {
            return cat_name === vendor.cat_name && supplier_code === vendor.supplier_code &&
                quantity === vendor.quantity && unit === vendor.unit && price === vendor.price;
        });
    };

    obj.loadFromDbCartData = function (data) {
        let dbcart = data.cart;
        default_prices = data.default_prices;
        savePrices();
        cart = [];
        for (let i = 0; i < dbcart.length; i++) {
            let item = dbcart[i];
            let new_sups = [];
            for (let j = 0; j < item.supplier.length; j++) {
                let s = item.supplier[j];
                new_sups.push(new Supplier(s.cat_name, s.supplier_code, s.price, s.purchase, s.quantity, s.unit, s.shipping, s.assigned));
            }
            cart.push(new Item(item.identifier, item.db, item.smile, new_sups));
        }
        saveCart();
    };
    obj.writeToDb = function (url, method, data) {
        let is_authenticated = localStorage.getItem("is_authenticated");
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
    };
    // ----------------------------
    return obj;
})();
