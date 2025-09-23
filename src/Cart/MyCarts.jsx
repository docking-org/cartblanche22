import React from "react";
import axios from "axios";
import { useEffect } from "react";
import { Container, Card, Table, Button, Modal, Form } from "react-bootstrap";
import Cart from "./Cart";
import { ToastContainer } from "react-toastify";

export default function MyCarts(props) {
    const { activateCart, createCart, deleteCart } = Cart();
    const [carts, setCarts] = React.useState([]);
    const [deleteModal, setDeleteModal] = React.useState(false);
    const [addModal, setAddModal] = React.useState(false);
    const [newCartName, setNewCartName] = React.useState("");
    const [deleteCartId, setDeleteCartId] = React.useState(null);
    useEffect(() => {
        loadCarts();
    }, [])

    useEffect(() => {
        document.title = props.title || "";
      }, [props.title]);

    function loadCarts() {
        axios({
            method: "get",
            url: "/myCarts",
            headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
        })
            .then(response => {
                setCarts(response.data);

            }).catch((err) => {
                alert('You must be logged in to view your carts.');
                window.location.href = "/";
            });
    }

    return (
        <Container className="mt-2 mb-2">
            <Card>
                <Card.Header><b>My Carts</b></Card.Header>
                <Card.Body>
                    You have <b>{carts.length}</b> carts &nbsp;
                    <Button
                        onClick={() => setAddModal(true)}
                        aria-label="Create new cart"
                    >
                        <i class="fas fa-plus"></i>
                    </Button>

                    <Table striped bordered hover
                        className="mt-2"
                    >
                        <thead>
                            <tr>
                                <th>Active</th>
                                <th>Cart Name</th>
                                <th>Cart Size</th>
                                <th>Cart Price</th>
                                <th>

                                </th>


                            </tr>
                        </thead>
                        <tbody>
                            {carts.map((cart, index) => (
                                <tr key={index}>
                                    <td>{cart.active ?
                                        <Button
                                            variant="outline-primary"
                                            aria-labelledby="Active cart"
                                        ><i class="fas fa-check"></i></Button> :
                                        <Button
                                            aria-label="Activate cart"
                                            onClick={() =>
                                                activateCart(cart.DT_RowId, cart.name).then((response) => {
                                                    loadCarts();
                                                })}


                                            variant="outline-primary"
                                        >Activate</Button>

                                    }</td>
                                    <td>{cart.name}</td>
                                    <td>{cart.qty}</td>
                                    <td>{cart.total}</td>
                                    <td
                                        onClick={() => {
                                            setDeleteCartId(cart.DT_RowId);
                                            setDeleteModal(true);
                                        }}

                                    >
                                        <i class="fas fa-trash-alt"></i>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>
            <Modal
                show={addModal}
            >
                <Modal.Header>
                    <Modal.Title>
                        <b>Create New Cart</b>
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form
                        onSubmit={(e) => {
                            e.preventDefault();
                            createCart(newCartName).then((response) => {
                                loadCarts();
                                setAddModal(false);
                                setNewCartName("");
                            })
                        }}
                    >
                        <Form.Group>
                            <Form.Label>Cart Name</Form.Label>
                            <Form.Control
                                aria-labelledby="Enter cart name"
                                onChange={(e) => setNewCartName(e.target.value)}
                                value={newCartName}
                                type="text" placeholder="Enter cart name" />
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" aria-label="Close cart">Close</Button>
                    <Button variant="primary"
                        onClick={() => {
                            createCart(newCartName).then((response) => {
                                loadCarts();
                                setAddModal(false);
                                setNewCartName("");
                            })
                        }}
                    >Create</Button>
                </Modal.Footer>
            </Modal>
            <Modal
                show={deleteModal}
            >
                <Modal.Header>
                    <Modal.Title>
                        <b>Delete Cart</b>
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    Are you sure you want to delete this cart?
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary">Close</Button>
                    <Button variant="primary"
                        aria-label="Delete cart"
                        onClick={() => {
                            deleteCart(deleteCartId).then((response) => {
                                loadCarts();
                                setDeleteModal(false);
                                setDeleteCartId(null);
                            })
                        }}
                    >Delete</Button>
                </Modal.Footer>

            </Modal>

            <ToastContainer></ToastContainer>
        </Container >





    )
}