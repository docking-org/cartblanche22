import React from 'react';
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button } from "react-bootstrap";
import axios from 'axios';
import { useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import useToken from '../utils/useToken';
export default function Cart(props) {
    const { token } = useToken();

    const [cart, setCart] = React.useState([]);

    const [id, setId] = React.useState("");
    const [maxSize, setMaxSize] = React.useState(300);
    const [cartLoaded, setLoaded] = React.useState(false);

    function cartItem(identifier, db, smiles, vendor) {
        this.identifier = identifier;
        this.smile = smiles;
        this.db = db;
        this.vendors = vendor;
    }

    useEffect(() => {

        refreshCart();
    }, [])

    // useEffect(() => {
    //     document.title = props.title || "";
    //   }, [props.title]);

    function refreshCart() {

        if (!token) {
            let localCart = JSON.parse(localStorage.getItem("localCart"));
            if (localCart) {
                setCart(localCart);
            }

            setLoaded(true);
            return;
        }

        return axios({
            method: "get",
            url: "/cart/getCart",
            headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
        })
            .then(response => {
                console.log(response);
                setCart(response.data.items);
                setLoaded(true);
            })

    }

    function clearCart() {
        if (!token) {
            localStorage.removeItem("localCart");
            setCart([]);
            return;
        }
        else {
            return axios({
                method: "post",
                url: "/clearCart",
                headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
            })
                .then(response => {
                    console.log(response);
                    refreshCart();
                })
        }

        // return axios({
        //     method: "delete",
        //     url: "/cart",
        //     headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
        // })
        //     .then(response => {
        //         console.log(response);
        //         setCart([]);
        //     })
    }

    function activateCart(id, name) {
        let form = new FormData();
        form.append("id", id);
        let tst = toastLoading("Activating cart");
        return axios({
            method: "post",
            url: "/cart/activate",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form
        }).then(response => {
            console.log(response);
            toast200(tst, `Cart '${name}' activated`);
            refreshCart();
        })
    }


    function getCart() {
        return cart;
    }

    function getTotalPrice() {
        let total = 0;
        console.log(cart);
        for (let i = 0; i < cart.length; i++) {
            if (cart[i].vendors[0]) {
                total += cart[i].vendors[0].price * cart[i].vendors[0].purchase;
            }
        }
        console.log(total);
        return total;
    }

    function findAndAdd(id, db = null, smiles = null) {
        let form = new FormData();
        form.append("identifier", id);
        console.log(db)
        if (db) {
            form.append("db", db);
        }
        if (smiles) {
            form.append("smiles", smiles);
        }
        let tst = toastLoading("Adding to cart");

        if (!token) {
            let localCart = JSON.parse(localStorage.getItem("localCart"));
            if (!localCart) {
                localCart = [];
            }
            return axios({
                method: "post",
                url: "/cart/getPurchasability",
                headers: {
                    "Content-Type": "multipart/form-data"
                },
                data: form,
            }).then(response => {
                console.log(response);
                if (response.status === 200) {
                    addToCart(response.data, tst);

                    refreshCart();
                }
                else {
                    toastError(tst, "Failed to add item to cart.");
                }
            });

        }

        return axios({
            method: "post",
            url: "/cart/findAndAdd",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form,
        }).then(response => {
            refreshCart();
            setLoaded(true);
            if (response.status === 200) {
                toast200(tst, response.data.msg);
            }
            else if (response.status === 207) {
                toast207(tst, response.data.msg);
            }
            else {
                toastError(tst, response.data.msg);
            }
        })
    }

    function addToCart(items, id = null) {


        if (!(items instanceof Array)) {
            items = [items];
        }

        if (items.length > maxSize || cart.length + items.length > maxSize) {
            alert("Maximum cart size (300) exceeded. Consider downloading the results instead.");
            return;
        }

        if (!id) {
            id = toastLoading("Adding to cart");
        }


        if (!token) {
            let missing = 0;
            let localCart = JSON.parse(localStorage.getItem("localCart"));
            if (!localCart) {
                localCart = [];
            }

            for (let i = 0; i < items.length; i++) {
                let vendors = items[i].catalogs;
                let bestVendor = null;
                let lowestPrice = 9999999
                if (vendors) {
                    for (let j = 0; j < vendors.length; j++) {
                        if (vendors[j].price < lowestPrice) {
                            lowestPrice = vendors[j].price;
                            bestVendor = vendors[j];
                        }
                    }
                }
                if (bestVendor) {
                    bestVendor.purchase = 1;
                    bestVendor.assigned = true;
                    bestVendor.cat_name = bestVendor.catalog_name;
                }
                else {
                    missing++;
                }


                let newItem = {
                    identifier: items[i].identifier || items[i].zinc_id,
                    db: items[i].db,
                    smile: items[i].smiles,
                    vendors: bestVendor ? [bestVendor] : []
                }

                if (!inCart(newItem)) {
                    localCart.push(newItem);
                }

            }

            localStorage.setItem("localCart", JSON.stringify(localCart));

            if (missing > 0) {
                toast207(id, `Successfully added ${items.length} item(s) to cart. ${missing} item(s) were not found in any catalog.`);
            }
            else {
                toast200(id, "Successfully added " + items.length + " item(s) to cart.");
            }
            refreshCart();
            return;
        }

        let form = new FormData();

        form.append("items", JSON.stringify(items));

        return axios({
            method: "post",
            url: "/cart/addItems",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form,
        }).then(response => {
            refreshCart();
            setLoaded(true);
            if (response.status === 200) {
                toast200(id, response.data.msg);
            }
            else if (response.status === 207) {
                toast207(id, response.data.msg);
            }
            else {
                toastError(id, response.data.msg);
            }
        })
    }

    function removeFromCart(items) {
        let id = toastLoading("Removing from cart");

        if (!(items instanceof Array)) {
            items = [items];
        }

        if (!token) {
            let localCart = JSON.parse(localStorage.getItem("localCart"));
            if (!localCart) {
                localCart = [];
            }
            for (let i = 0; i < items.length; i++) {
                for (let j = 0; j < localCart.length; j++) {
                    let id = items[i].identifier || items[i].zinc_id || items[i];
                    if (localCart[j].identifier === id) {
                        localCart.splice(j, 1);
                    }
                }
            }

            localStorage.setItem("localCart", JSON.stringify(localCart));
            toast200(id, "Successfully removed " + items.length + " item(s) from cart.");
            refreshCart();
            return;
        }

        let form = new FormData();


        form.append("items", JSON.stringify(items));



        return axios({
            method: "post",
            url: "/cart/removeItem",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form
        })
            .then(response => {
                refreshCart();
                setLoaded(true);
                if (response.status === 200) {
                    toast200(id, response.data.msg);
                }
                else if (response.status === 207) {
                    toast207(id, response.data.msg);
                }
                else {
                    toastError(id, response.data.msg);
                }
            })
    }

    function cartSize() {
        return cart.length;
    }



    function changeQuantity(item, quantity) {
        axios({
            method: "post",
            url: "/cart/changeQuantity",
            headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
            data: {
                item: item,
                quantity: quantity
            }
        })
            .then(response => {
                console.log(response);
            })
    }


    function inCart(item) {

        let inside = false;

        let itemid = item.identifier || item.zinc_id || item;


        for (let i = 0; i < cart.length; i++) {
            let id = cart[i].identifier;

            if (itemid === id) {
                inside = true;

                if (!cart[i].vendors[0] || cart[i].vendors[0].price === 0) {
                    //items that do not have vendor info are sorta in the cart
                    inside = "sorta";
                }
            }
        }
        return inside;
    }

    function createCart(name) {
        let id = toastLoading("Creating cart");
        let form = new FormData();
        form.append("name", name);

        return axios({
            method: "post",
            url: "/cart/create",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form
        })
            .then(response => {
                if (response.status === 200) {
                    toast200(id, response.data.msg);
                }
                else if (response.status === 207) {
                    toast207(id, response.data.msg);
                }
                else {
                    toastError(id, response.data.msg);
                }
            }
            )

    }

    function deleteCart(id) {
        let toastid = toastLoading("Deleting cart");
        let form = new FormData();
        form.append("id", id);
        return axios({
            method: "post",
            url: "/cart/delete",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "multipart/form-data"
            },
            data: form
        })
            .then(response => {
                if (response.status === 200) {
                    toast200(toastid, response.data.msg);
                }
                else if (response.status === 207) {
                    toast207(toastid, response.data.msg);
                }
                else {
                    toastError(toastid, response.data.msg);
                }
            }
            )
    }




    function toastLoading(msg) {
        const id = toast.loading(msg, {
            position: toast.POSITION.BOTTOM_LEFT,
            autoClose: 2000
        });
        return id;
    }


    function toast200(id, msg) {
        toast.update(id, {
            render: msg,
            type: toast.TYPE.SUCCESS,
            autoClose: 1500,
            isLoading: false
        });
    }

    function toast207(id, msg) {
        toast.update(id, {
            render: msg,
            type: toast.TYPE.WARNING,
            autoClose: 2000,
            isLoading: false,
        });
    }

    function toastError(id, msg) {
        toast.update(id, {
            render: msg,
            type: toast.TYPE.ERROR,
            autoClose: 2000,
            isLoading: false
        });
    }


    return {
        getCart,
        addToCart,
        refreshCart,
        removeFromCart,
        cartSize,
        inCart,
        changeQuantity,
        cartLoaded,
        getTotalPrice,
        findAndAdd,
        clearCart,
        activateCart,
        createCart,
        deleteCart,
        toastLoading,
        toast200,
        toast207,
        toastError
    }


}