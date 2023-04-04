import React from 'react';
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button, Tab, Table, Card, Pagination, Dropdown } from "react-bootstrap";
import axios from 'axios';
import { useEffect } from 'react';
import Cart from './Cart';
import MoleculeStructure from '../RDKit/MoleculeStructure'
import { ToastContainer, toast } from 'react-toastify';
import { saveAs } from 'file-saver';
import useToken from '../utils/useToken';


export default function Checkout(props) {

    const { token, setToken } = useToken();
    const { getCart, addToCart, removeFromCart, cartSize, inCart, getTotalPrice, clearCart } = Cart();
    const [cart, setCart] = React.useState(getCart());
    const [clearModal, setClearModal] = React.useState(false);
    const [format, setFormat] = React.useState('json');
    const [downloadModal, setDownloadModal] = React.useState(false);
    const [page, setPage] = React.useState(1);
    const [perPage, setPerPage] = React.useState(20);
    const [total, setTotal] = React.useState(getCart().length);
    useEffect(() => {
        setCart(getCart());
    }, [cartSize])

    useEffect(() => {
        document.title = props.title || "";
      }, [props.title]);

    function createGoogleSheet() {
        let form = new FormData();
        form.append('cart', JSON.stringify(cart));

        const id = toast.loading("Creating Google Sheet...", {
            position: toast.POSITION.BOTTOM_LEFT,
            autoClose: 2000
        });
        axios({
            method: 'post',
            url : "/cart/createGoogleSheet",
            data: form,
        }).then((response) => {
            toast.update(id, {
                render: "Google Sheet Created",
                type: toast.TYPE.SUCCESS,
                isLoading: false,
                autoClose: 2000
            });
            console.log(response.data);
        }).catch((error) => {
            toast.update(id, {
                render: "Error Creating Google Sheet",
                type: toast.TYPE.ERROR,
                autoClose: 2000,
                isLoading: false,
            });
        });
    }


    function buildPagination() {
        let total = getCart().length;
        let pagination = [];
        //show 2 pages before and after current page
        let start = page - 2;
        let end = page + 2;
        //if current page is less than 3, show first 5 pages
        if (page < 3) {
            start = 1;
            end = 5;
        }
        //if current page is greater than total pages - 2, show last 5 pages
        if (page > Math.ceil(total / perPage) - 2) {
            start = Math.ceil(total / perPage) - 4;
            end = Math.ceil(total / perPage);
        }
        //if total pages is less than 5, show all pages
        if (Math.ceil(total / perPage) < 5) {
            start = 1;
            end = Math.ceil(total / perPage);
        }
        //if start is less than 1, set to 1
        if (start < 1) {
            start = 1;
        }
        //if end is greater than total pages, set to total pages
        if (end > Math.ceil(total / perPage)) {
            end = Math.ceil(total / perPage);
        }
        //build pagination
        for (let i = start; i <= end; i++) {
            pagination.push(
                <Pagination.Item key={i} active={i === page} onClick={() => setPage(i)}>
                    {i}
                </Pagination.Item>,
            );
        }
        return pagination;
    }

    function downloadResults(format) {
        const id = toast.loading("Saving File...", {
            position: toast.POSITION.BOTTOM_LEFT,
            autoClose: 2000
        });


        let items = cart;
        items = items.map(item => {
            return {
                "identifier": item.identifier,
                "smiles": item.smile,
                "db": item.db,
                "catalog_name": item.vendors[0] ? item.vendors[0].catalog_name : null,
                "price": item.vendors[0] ? item.vendors[0].price : null,
                "quantity": item.vendors[0] ? item.vendors[0].quantity : null,
                "shipping": item.vendors[0] ? item.vendors[0].shipping : null,
                "short_name": item.vendors[0] ? item.vendors[0].short_name : null,
                "supplier_code": item.vendors[0] ? item.vendors[0].supplier_code : null,
                "unit": item.vendors[0] ? item.vendors[0].unit : null,
                "purchase": item.vendors[0] ? item.vendors[0].purchase : null,
            }
        })
        if (format === 'json') {
            const blob = new Blob([JSON.stringify(items)], { type: format });
            saveAs(blob, "results." + format);
        } else if (format === 'csv') {
            let csv = '';
            csv += 'identifier,smiles,db,catalog_name,price,quantity,shipping,short_name,supplier_code,unit,purchase\n'
            items.forEach(item => {
                csv += item.identifier + ',' + item.smiles + ',' + item.db + ',' + item.catalog_name + ',' + item.price + ',' + item.quantity + ',' + item.shipping + ',' + item.short_name + ',' + item.supplier_code + ',' + item.unit + ',' + item.purchase + "\n"
            })
            const blob = new Blob([csv], { type: format });
            saveAs(blob, "results." + format);
        }
        else if (format === 'tsv') {
            let tsv = '';
            tsv += 'identifier\tsmiles\tdb\tcatalog_name\tprice\tquantity\tshipping\tshort_name\tsupplier_code\tunit\tpurchase\n'
            items.forEach(item => {
                tsv += item.identifier + '\t' + item.smiles + '\t' + item.db + '\t' + item.catalog_name + '\t' + item.price + '\t' + item.quantity + '\t' + item.shipping + '\t' + item.short_name + '\t' + item.supplier_code + '\t' + item.unit + '\t' + item.purchase + "\n"
            })
            const blob = new Blob([tsv], { type: format });
            saveAs(blob, "results." + format);
        }
        toast.update(id, {
            render: "File Saved",
            isLoading: false,
            type: toast.TYPE.SUCCESS,
            autoClose: 2000
        });

        return;


    }

    return (
        <Container className='mt-2'>
            <Card>
                <Card.Header>
                    <b>Checkout</b>
                </Card.Header>
                <Card.Body>
                    <Navbar className=''>
                        <Button variant="danger" onClick={() => setClearModal(true)}>Clear Cart</Button>

                        <Navbar.Collapse className="justify-content-end">
                            <Navbar.Text>
                                <Button variant="success" disabled>
                                    {getCart().length} Items
                                </Button>
                            </Navbar.Text>
                            &nbsp;
                            <Navbar.Text>
                                <Button variant="success" disabled>
                                    Total Price: ${getTotalPrice().toLocaleString()}
                                </Button>
                            </Navbar.Text>
                            &nbsp;
                            <Navbar.Text>
                                <Button onClick={() => setDownloadModal(true)}>Download</Button>
                            </Navbar.Text>
                            {/* &nbsp;
                            <Navbar.Text>
                                <Button onClick={() => 
                                    createGoogleSheet
                                }>Export to Google Sheets</Button>
                            </Navbar.Text> */}
                        </Navbar.Collapse>
                    </Navbar>

                    <Pagination className='mx-1'>
                        <Pagination.First onClick={() => setPage(1)} />
                        <Pagination.Prev onClick={() => page <= 1 ? setPage(1) : setPage(page - 1)} />
                        {buildPagination()}
                        <Pagination.Next onClick={() => page >= Math.ceil(getCart().length / perPage) ? setPage(Math.ceil(getCart().length / perPage)) : setPage(page + 1)} />
                        <Pagination.Last onClick={() => setPage(Math.ceil(getCart().length / perPage))} />

                        <Dropdown>
                            <Dropdown.Toggle variant="" id="dropdown-basic">
                                {perPage}
                            </Dropdown.Toggle>
                            <Dropdown.Menu>
                                <Dropdown.Item onClick={() => setPerPage(10)}>10</Dropdown.Item>
                                <Dropdown.Item onClick={() => setPerPage(20)}>20</Dropdown.Item>
                                <Dropdown.Item onClick={() => setPerPage(50)}>50</Dropdown.Item>
                                <Dropdown.Item onClick={() => setPerPage(100)}>100</Dropdown.Item>
                            </Dropdown.Menu>
                        </Dropdown>
                    </Pagination>


                    <div
                        style={{
                            maxHeight: "500px",
                            overflow: "scroll"
                        }}
                    >
                        <Table responsive striped bordered hover

                        >
                            <thead

                            >
                                <tr
                                    className='position-sticky top-0'>
                                    <th>
                                        No
                                    </th>
                                    <th>
                                        Image
                                    </th>
                                    <th>
                                        <h5>Identifier</h5>
                                        <h6>Database</h6>
                                    </th>

                                    <th>
                                        <h5>Catalog Name</h5>
                                        <h6>Supplier Code</h6>
                                    </th>


                                    <th>
                                        Pack Size
                                    </th>
                                    <th>Shipping</th>
                                    <th>
                                        Est. Pack Price
                                    </th>
                                    <th>
                                        Purchase Qty
                                    </th>
                                    <th>
                                        Total Price
                                    </th>
                                    <th>

                                    </th>
                                </tr>
                            </thead>
                            <tbody>

                                {cart ? cart.slice((page - 1) * perPage, page * perPage).map((item, cartIdx) => {
                                    return (
                                        <tr key={cartIdx}>
                                            <td>
                                                {cartIdx + 1}
                                            </td>
                                            <td
                                                width={100}
                                            >
                                                <MoleculeStructure
                                                    structure={item.smile}
                                                    svgMode
                                                />
                                            </td>
                                            <td>
                                                {item.identifier && item.identifier.includes("ZINC") ? (
                                                    <a href={`/substance/${item.identifier}`} target="_blank" rel="noreferrer">
                                                        {item.identifier}
                                                    </a>
                                                ) :
                                                    item.identifier}


                                                <br />
                                                {item.db}
                                            </td>
                                            {
                                                item.vendors.map((vendor, index) => {
                                                    if (vendor.assigned) {
                                                        return (
                                                            <>
                                                                <td key={index}>
                                                                    {vendor.price === 0 ? "No Vendor Available" : (
                                                                        <>
                                                                            {vendor.cat_name}
                                                                            <br />
                                                                            {vendor.supplier_code}
                                                                        </>
                                                                    )
                                                                    }
                                                                </td>
                                                                <td>
                                                                    {vendor.price === 0 ? "" : vendor.quantity + vendor.unit}

                                                                </td>
                                                                <td>
                                                                    {vendor.price === 0 ? "" : vendor.shipping}
                                                                </td>
                                                                <td>
                                                                    {vendor.price === 0 ? "" : parseFloat(vendor.price).toFixed(2)}
                                                                </td>
                                                                <td>
                                                                    {vendor.price === 0 ? "" : (
                                                                        <Form.Select size="sm">
                                                                            <option>1</option>
                                                                            <option>2</option>
                                                                            <option>3</option>
                                                                            <option>4</option>
                                                                        </Form.Select>)}
                                                                </td>
                                                                <td>
                                                                    {vendor.price === 0 ? "" :

                                                                        parseFloat(vendor.price * vendor.purchase).toFixed(2)}

                                                                </td>
                                                            </>
                                                        )
                                                    }

                                                }
                                                )
                                            }
                                            {item.vendors.length === 0 ? (<td colSpan={6}>No vendor available</td>) : null}

                                            <td>
                                                <Button
                                                    variant="danger"
                                                    size="sm"
                                                    onClick={() => removeFromCart(item)}
                                                >
                                                    <i className="fas fa-trash"></i>
                                                </Button>
                                            </td>

                                        </tr>

                                    )

                                }
                                )
                                    : null
                                }

                            </tbody>
                        </Table>
                    </div >
                </Card.Body>
            </Card>
            <Modal
                show={clearModal}
                onHide={() => {
                    setClearModal(false);
                    setDownloadModal(false);
                }}
            >
                <Modal.Header closeButton>
                    <Modal.Title>Clear Cart</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    Are you sure you want to clear the cart?
                </Modal.Body>
                <Modal.Footer>
                    <Button
                        variant="secondary"
                        onClick={() => {
                            setClearModal(false);
                        }}
                    >
                        Close
                    </Button>
                    <Button
                        variant="danger"
                        onClick={() => {
                            clearCart();
                            setClearModal(false);
                        }}
                    >
                        Clear Cart
                    </Button>
                </Modal.Footer>
            </Modal>

            <Modal
                show={downloadModal}
                onHide={() => {
                    setClearModal(false);
                    setDownloadModal(false);
                }}
            >
                <Modal.Header closeButton>
                    <Modal.Title>Download</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group>
                            <b>Note: All prices and shipping times are estimates and may not be accurate. Please contact the vendor for more information.</b>
                            <br></br>
                            <br />
                            <Form.Label>Format</Form.Label>
                            <Form.Select
                                onChange={(e) => {
                                    setFormat(e.target.value);
                                }}
                            >
                                <option value="json">JSON</option>
                                <option value="csv">CSV</option>
                                <option value="xlsx">TSV</option>
                            </Form.Select>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button
                        variant="secondary"
                        onClick={() => {
                            setDownloadModal(false);
                        }}
                    >
                        Close
                    </Button>
                    <Button
                        variant="primary"
                        onClick={() => {
                            downloadResults(format);
                            setDownloadModal(false);
                        }}
                    >
                        Download
                    </Button>
                </Modal.Footer>


            </Modal>

            <ToastContainer></ToastContainer>
        </Container >

    )
}
