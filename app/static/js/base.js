let shoppingCart = (function () {
    // Private methods and properties
    let cart = [];

    // function Item(name, price, count) {
    //     this.name = name;
    //     this.price = price;
    //     this.count = count;
    // }

    function Item(identifier, db, smile) {
        this.identifier = identifier;
        this.db = db;
        this.smile = smile;
        this.supplier = [];
    }
    
    function Supplier(cat_name,supplier_code, price, purchase, quantity, unit, shipping) {
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
            cart = []
        }
    }

    loadCart();

    // Public methods and properties
    var obj = {};

    obj.addItemToCart = function (identifier, db, smile) {
        for (var i in cart) {
            if (cart[i].identifier === identifier) {
                return;
            }
        }
        console.log("addItemToCart:", identifier, db, smile);
        var item = new Item(identifier,db, smile);
        cart.push(item);
        saveCart();
    };

    obj.addVendorToCart = function(identifier, cat_name,supplier_code, price, purchase, quantity, unit, shipping) {
        let sup = new Supplier(cat_name,supplier_code, price, purchase, quantity, unit, shipping);
        for (var i in cart) {
            if (cart[i].identifier === identifier) {
                for (let s in cart[i].supplier){
                    if (s.cat_name === cat_name && s.supplier_code === supplier_code && s.price === price &&
                        s.quantity === quantity && s.unit === unit){
                        cart[i].supplier[s].purchase ++;
                        saveCart();
                        return;
                    }
                }
                cart[i].supplier.push(sup);
                saveCart();
                return;
            }
        }
    };

    // obj.setCountForItem = function (name, count) {
    //     for (var i in cart) {
    //         if (cart[i].name === name) {
    //             cart[i].count = count;
    //             break;
    //         }
    //     }
    //     saveCart();
    // };


    obj.removeItemFromCart = function (identifier) { // Removes one item
        for (var i in cart) {
            if (cart[i].identifier === identifier) { // "3" === 3 false
                cart.splice(i, 1);
                break;
            }
        }
        saveCart();
    };


    // obj.removeItemFromCartAll = function (name) { // removes all item name
    //     for (var i in cart) {
    //         if (cart[i].name === name) {
    //             cart.splice(i, 1);
    //             break;
    //         }
    //     }
    //     saveCart();
    // };


    obj.clearCart = function () {
        cart = [];
        saveCart();
    };


    obj.countCart = function () { // -> return total count
        var totalCount = 0;
        for (var i in cart) {
            let suppliers = cart[i].supplier;
            for (let s in suppliers){
                totalCount += suppliers[s].purchase;
            }
        }
        return totalCount;
    };

    obj.totalCart = function () { // -> return total cost
        var totalCost = 0;
        for (var i in cart) {
            let suppliers = cart[i].supplier;
            for (let s in suppliers){
                totalCost += suppliers[s].purchase * suppliers[s].price;
            }
        }
        return totalCost.toFixed(2);
    };

    obj.listCart = function () { // -> array of Items
        var cartCopy = [];
        console.log("Listing cart");
        console.log(cart);
        for (var i in cart) {
            let it = cart[i];
        if (it.supplier.length == 0) {
            let temp = {}
            temp['img'] = it['img']
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
            cartCopy.push(temp)
        }

        for (let j = 0; j < it['supplier'].length; j++) {
            let vendor = it['supplier'][j]
            let temp = {}
            temp['img'] = it['img']
            temp['identifier'] = it['identifier']
            temp['cat_name'] = vendor['cat_name']
            temp['supplier_code'] = vendor['supplier_code']
            temp['quantity'] = vendor['quantity']
            temp['unit'] = vendor['unit']
            temp['price'] = vendor['price']
            temp['shipping'] = vendor['shipping']
            temp['db'] = it['db']
            temp['purchase'] = vendor['purchase']
            temp['total'] =(vendor['price'] * vendor['purchase']).toFixed(2);
            temp['num'] = num
            temp['stereochemistry'] = false
            temp['analogs'] = false
            temp['salt'] = false
            cartCopy.push(temp)
        }
        return cartCopy;
    }};

    // ----------------------------
    return obj;
})();