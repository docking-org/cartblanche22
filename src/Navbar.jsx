import React, { useEffect } from "react";
import useToken from "./utils/useToken.js";
import axios from "axios";
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button, OverlayTrigger, Tooltip } from "react-bootstrap";
export default function Navigation() {
    const { token, removeToken, setToken, username } = useToken();
    const [show, setShow] = React.useState(false);
    const [register, setRegister] = React.useState(false);
    const [forgot, setForgot] = React.useState(false);
    const [inucsf, setInUCSF] = React.useState(false);
    const [form, setForm] = React.useState({
        username: "",
        password: "",
        confirmPassword: "",
        email: "",
    });

    useEffect(() => {
        //check if token is valid
        if (token) {
            axios({
                method: "get",
                url: "/verify",
                headers: { "Authorization": "Bearer " + token },
            }).then((res) => {
                console.log(res);
                if (res.data.inucsf) {
                    setInUCSF(true);
                }
            }).catch((err) => {
                console.log(err);
                removeToken();
            });
        }
    }, []);

    const handleClose = () => {
        setShow(false);
        setRegister(false);
        setForgot(false);
    }
    const handleShow = () => {
        setShow(true);
        setRegister(false);
    }
    const handleRegister = () => {
        setRegister(true);
        setShow(false);
    };
    const handleForgot = () => {
        setRegister(false);
        setShow(false);
        setForgot(true);
    };
    const handleForgotClose = () => {
        setForgot(false);
        setRegister(false);
        setShow(false);
    };

    const handleLogin = () => {
        let formData = new FormData();
        formData.append("username", document.getElementById("username").value);
        formData.append("password", document.getElementById("password").value);

        axios({
            method: "post",
            url: "/login",
            data: formData,
            headers: { "Content-Type": "multipart/form-data" },
        }).then((res) => {
            setToken(res.data.access_token, res.data.username);

            setShow(false);
            setRegister(false);
            setForgot(false);
            window.location.reload();
        }).catch((err) => {
            alert(err.response.data.msg);

        });
    };

    const handleLogout = () => {
        axios.post("/logout", {
        }).then((res) => {
            removeToken();
            window.location.reload();
        }).catch((err) => {
            console.log(err);
        });
    };

    const handleRegisterSubmit = () => {
        let formData = new FormData();
        formData.append("username", form.username);
        formData.append("password", form.password);

        formData.append("email", form.email);

        axios
            .post("/register", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            })
            .then((res) => {
                setToken(res.data.access_token, res.data.username);
                setShow(false);
                setRegister(false);
                setForgot(false);
                alert("Registration successful");
                window.location.reload();
            })
            .catch((err) => {
                alert(err.response.data.msg);
            });
    };

    const handleForgotSubmit = () => {
        let formData = new FormData();

        formData.append("email", form.email);

        axios
            .post("/forgotPassword", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            })
            .then((res) => {
                setShow(false);
                setRegister(false);
                setForgot(false);
                alert(res.data.msg);
                window.location.reload();
            })
            .catch((err) => {
                alert(err.response.data.msg);
            });
    };

    return (
        <>
            <Navbar bg="dark" expand="lg" variant="dark">
                <Container fluid>
                    <Navbar.Brand href="/">Cartblanche</Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />

                    <Navbar.Collapse>
                        <Nav className="mr-auto">
                            <Nav.Item>
                                <OverlayTrigger
                                    placement="right"
                                    delay={{ show: 250, hide: 0 }}
                                    overlay={<Tooltip id="button-tooltip-2">Smallworld : Search by whole molecule similarity based on graph-edit-distance with calculated Tanimoto coefficient</Tooltip>}
                                >
                                    <NavDropdown title="Similarity" id="basic-nav-dropdown">
                                        <NavDropdown.Item href="/similarity/sw">Public</NavDropdown.Item>

                                        {
                                            <NavDropdown.Item href="/similarity/swp">Private</NavDropdown.Item>}
                                        {inucsf &&
                                            <NavDropdown.Item href="/similarity/swc">Super Private</NavDropdown.Item>}
                                    </NavDropdown>
                                </OverlayTrigger>
                            </Nav.Item>
                            <Nav.Item>
                                <OverlayTrigger
                                    placement="left"
                                    delay={{ show: 250, hide: 0 }}
                                    overlay={<Tooltip id="button-tooltip-2">Arthor : Search by substructure or pattern (SMARTS)</Tooltip>}

                                >
                                    <NavDropdown title="Arthor" id="basic-nav-dropdown">
                                        <NavDropdown.Item href="/patterns/arthor">Public</NavDropdown.Item>
                                        <NavDropdown.Item href="/patterns/arthorp">Private</NavDropdown.Item>
                                        {inucsf &&
                                            <NavDropdown.Item href="/patterns/arthorc">Super Private</NavDropdown.Item>}
                                    </NavDropdown>
                                </OverlayTrigger>
                            </Nav.Item>
                            <Nav.Item>
                                <NavDropdown title="Lookup" id="basic-nav-dropdown">
                                    <NavDropdown.Item href="/search/zincid">By ZincId</NavDropdown.Item>
                                    <NavDropdown.Item href="/search/catitems">By Supplier</NavDropdown.Item>
                                    <NavDropdown.Item href="/search/smiles">By SMILES</NavDropdown.Item>
                                    <NavDropdown.Item href="/search/random">Download Random Molecules</NavDropdown.Item>
                                </NavDropdown>
                            </Nav.Item>
                            <Nav.Item>
                                <NavDropdown title="Tranches" id="basic-nav-dropdown">
                                    <NavDropdown.Item href="/tranches/3d">3D</NavDropdown.Item>
                                    <NavDropdown.Item href="/tranches/2d">2D</NavDropdown.Item>
                                </NavDropdown>
                            </Nav.Item>
                        </Nav>
                        <Nav className="ms-lg-auto mr-sm-auto">

                            <Nav.Item className="">
                                {token ? (
                                    <NavDropdown
                                        align="end"
                                        title={username} id="basic-nav-dropdown">
                                        {/* <NavDropdown.Item href="/account">Account</NavDropdown.Item> */}
                                        <NavDropdown.Item href="/carts">My Carts</NavDropdown.Item>
                                        <NavDropdown.Divider />
                                        <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
                                    </NavDropdown>
                                )
                                    :
                                    <Button variant="outline-primary" onClick={handleShow}>
                                        Sign In
                                    </Button>
                                }

                            </Nav.Item>
                            <Nav.Item className="">
                                <Nav.Link href="/cart">
                                    <i className="fas fa-shopping-cart"></i>
                                </Nav.Link>
                            </Nav.Item>
                            <NavDropdown align="end" title="About" id="basic-nav-dropdown">
                                        <NavDropdown.Item href="https://wiki.docking.org/index.php/Zinc22:Searching">Help</NavDropdown.Item>
                                        <NavDropdown.Item href="https://forms.gle/LZV1FCmLWxUWznVi9">Contact</NavDropdown.Item>
                                        <NavDropdown.Item href="https://cartblanche22.docking.org/stats/">Usage</NavDropdown.Item>
                                        <NavDropdown.Item href="https://wiki.docking.org/index.php/ZINC22:Credits">Acknowledgements</NavDropdown.Item>
                            </NavDropdown>
                        </Nav>
                    </Navbar.Collapse>


                </Container>
            </Navbar>
            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Sign in</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleLogin();
                        }}

                    >
                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>Username</Form.Label>

                            <Form.Control type="text" placeholder="Enter username"
                                id="username" />

                        </Form.Group>
                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>
                                Password
                            </Form.Label>
                            <Form.Control type="password"
                                id="password"
                            ></Form.Control>
                        </Form.Group>
                    </Form>
                </Modal.Body>

                <Modal.Footer>
                    <Col>
                        <Button variant="outline-primary btn-sm" onClick={handleRegister}>
                            New to Cartblanche?
                        </Button>
                    </Col>
                    <Button variant="secondary btn-sm " onClick={handleForgot}>
                        Forgot Password?
                    </Button>
                    <Button variant="primary btn-sm" onClick={handleLogin}>
                        Sign In
                    </Button>
                </Modal.Footer>
            </Modal>
            <Modal show={register} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Register</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleRegisterSubmit();
                        }}
                    >
                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>Username</Form.Label>

                            <Form.Control type="text" placeholder="Enter username"
                                onChange={(e) => { setForm({ ...form, username: e.target.value }) }}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control type="email" placeholder="Enter email"
                                onChange={(e) => { setForm({ ...form, email: e.target.value }) }}
                            />

                        </Form.Group>

                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>
                                Password
                            </Form.Label>
                            <Form.Control
                                type="password"
                                onChange={(e) => { setForm({ ...form, password: e.target.value }) }}
                            ></Form.Control>
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>
                                Confirm Password
                            </Form.Label>
                            <Form.Control type="password"

                                isInvalid={form.confirmPassword !== "" && form.password !== form.confirmPassword}

                                onChange={(e) => { setForm({ ...form, confirmPassword: e.target.value }) }}
                            ></Form.Control>
                            <Form.Control.Feedback type="invalid">
                                Passwords do not match
                            </Form.Control.Feedback>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Col>
                        <Button variant="outline-primary btn-sm" onClick={handleShow}>
                            Already have an account?
                        </Button>
                    </Col>
                    <Button variant="primary btn-sm" onClick=
                        {handleRegisterSubmit}
                    >
                        Register
                    </Button>
                </Modal.Footer>
            </Modal>
            <Modal show={forgot} onHide={handleForgotClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Forgot Password</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form onSubmit={(e) => {
                        e.preventDefault();
                        handleForgotSubmit();
                    }}>
                        <Form.Group className="mb-3" controlId="">
                            <Form.Label>Email</Form.Label>
                            <Form.Control type="email" placeholder="Enter email"
                                onChange={(e) => { setForm({ ...form, email: e.target.value }) }}
                            />
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Col>
                        <Button variant="outline-primary btn-sm" onClick={handleShow}>
                            Back to Sign In
                        </Button>
                    </Col>
                    <Button variant="primary btn-sm" onClick={handleForgotSubmit}>
                        Request Password Reset
                    </Button>
                </Modal.Footer>

            </Modal>


        </>
    );
}