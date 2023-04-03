import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Container, Table, Tabs, Tab, Card, Row, Col, InputGroup, OverlayTrigger, Tooltip, Button, ButtonGroup, Dropdown, DropdownButton } from "react-bootstrap";
import axios from "axios";
import {
    useParams,
    Link,
} from "react-router-dom";

import { saveAs } from "file-saver";
import MoleculeStructure from "../RDKit/MoleculeStructure";
import Cart from "../Cart/Cart";
import { ToastContainer } from "react-toastify";
import useToken from "../utils/useToken";
import Substance404 from "../Errors/Substance404";



export default function Substance() {
    const { token } = useToken();
    const { getCart, addToCart, removeFromCart, cartSize, inCart, refreshCart } = Cart();
    const [results, setResults] = React.useState(undefined);
    const [progress, setProgress] = React.useState(0);
    const [id, setId] = React.useState(useParams().id);
    const [loading, setLoading] = React.useState(true);
    const [notFound, setNotFound] = React.useState(false);

    useEffect(() => {
        document.title = id
        if (id == undefined) {
            window.location.href = "/404";
        }
        refreshCart();
        getResult();
    }, []);

    function searchSupplier(code) {
        var bodyFormData = new FormData();
        bodyFormData.append('supplier_codes', code);
        axios({
            method: "post",
            url: "/catitems.json",
            data: bodyFormData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(response => {
                window.location.href = "/results?task=" + response.data.task;
            })

    }

    function downloadResults(format) {
        let form = new FormData();
        form.append("zinc_ids", id);
        axios({
            method: "post",
            url: "/getSubstance/" + id + "." + format,
            data: form,
            headers: {
                "Content-Type": "multipart/form-data",
                "Authorization": token ? `Bearer ${token}` : "",
            },
        })
            .then(response => {
                if (format == "json") {
                    var blob = new Blob([JSON.stringify(response.data)], { type: "text/plain;charset=utf-8" });
                    saveAs(blob, "result." + format);
                }
                else {
                    var blob = new Blob([response.data], { type: "text/plain;charset=utf-8" });
                    saveAs(blob, "result." + format);
                }
            })
    }

    function getResult() {
        axios({
            method: "get",
            url: "/getSubstance/" + id,
        })
            .then(response => {
                console.log(response.data);
                if (response.status == 200) {
                    if (!response.data.smiles) {
                        setNotFound(true);
                        setLoading(false);
                        return;
                    }
                    setResults(response.data);
                    setLoading(false);
                }

            }).catch(error => {
                setNotFound(true);
                setLoading(false);
            })
    }

    return (
        <Container className="mt-2" >
            {notFound ? <Substance404 id={id} /> : null}
            {loading ? <div className="text-center m-4">
                <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
            </div> :
                null}
            {results &&
                <Card>
                    <Card.Header>{id}</Card.Header>
                    <Card.Body>
                        <Row>
                            <Col lg={8}>
                                <Table striped bordered>
                                    <thead>
                                        <tr>
                                            {results.tranche ? <th>Tranche</th> : null}

                                            <th>Heavy Atoms</th>
                                            <th>logP</th>
                                            <th>mwt</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>

                                            {results.tranche ? <td>{results.tranche.h_num + results.tranche.p_num}</td> : null}

                                            <td>
                                                {results.tranche_details.heavy_atoms} {results.tranche ? `(${results.tranche.mwt})` : null}
                                            </td>
                                            <td>
                                                {results.tranche_details.logp} {results.tranche ? `(${results.tranche.logp})` : null}

                                            </td>
                                            <td>
                                                {results.tranche_details.mwt}
                                            </td>
                                        </tr>
                                    </tbody>
                                </Table>
                                <InputGroup>
                                    <InputGroup.Text>SMILES</InputGroup.Text>
                                    <input type="text" className="form-control"
                                        disabled
                                        value={results.smiles} />
                                </InputGroup>
                                <br />
                                <InputGroup>
                                    <InputGroup.Text>INCHI</InputGroup.Text>
                                    <input type="text" className="form-control"
                                        disabled
                                        value={results.tranche_details.inchi} />
                                </InputGroup>
                                <br />

                                <InputGroup>
                                    <InputGroup.Text>INCHI Key</InputGroup.Text>
                                    <input type="text" className="form-control"
                                        disabled
                                        value={results.tranche_details.inchi_key} />

                                </InputGroup>

                            </Col>
                            <Col lg={4}>
                                <Row>
                                    <MoleculeStructure
                                        structure={results.smiles}
                                        svgMode
                                    />
                                </Row>
                                <Row>

                                    <Col lg={{
                                        span: 5,
                                        offset: 0
                                    }}>
                                        <ButtonGroup>
                                            <Button variant="warning">
                                                Find Similar
                                            </Button>
                                            <DropdownButton as={ButtonGroup} title={<i className="fa fa-download"></i>} id="bg-nested-dropdown" variant="secondary">


                                                <Dropdown.Item onClick={() => downloadResults("json")}>JSON</Dropdown.Item>
                                                <Dropdown.Item onClick={() => downloadResults("csv")}>CSV</Dropdown.Item>
                                                <Dropdown.Item onClick={() => downloadResults("txt")}>TXT</Dropdown.Item>

                                            </DropdownButton>
                                        </ButtonGroup>
                                    </Col>


                                    <Col
                                        lg={{
                                            span: 4,
                                            offset: 3
                                        }}
                                    >
                                        {
                                            inCart(results) ?
                                                <Button variant="danger" onClick={() => removeFromCart(
                                                    results
                                                )}>Remove from Cart</Button>
                                                :
                                                <Button variant="primary" onClick={() => addToCart(
                                                    results
                                                )}>Add to Cart</Button>
                                        }
                                    </Col>
                                </Row>
                            </Col>

                        </Row>
                        <br />
                        <Row>
                            <Col>
                                <Table striped bordered>
                                    <thead>
                                        <tr>
                                            <th>Catalog Name</th>
                                            <th>Supplier code</th>
                                            <th>Pack</th>
                                            <th>Ships within</th>

                                            <OverlayTrigger
                                                key="top"
                                                placement="top"
                                                overlay={
                                                    <Tooltip id="tooltip">
                                                        All prices listed below are estimated. Please check with vendors directly to confirm the price.
                                                    </Tooltip>
                                                }
                                            >
                                                <th>
                                                    Price (USD) *
                                                </th>

                                            </OverlayTrigger>

                                        </tr>
                                    </thead>
                                    {results.catalogs.length === 0 ? <tbody><tr><td colSpan="5">No catalogs found</td></tr></tbody> :


                                        results.catalogs.map((p, index) =>
                                            <tbody>
                                                <tr>
                                                    <td>{p.catalog_name}</td>
                                                    <td>

                                                        {
                                                            p.supplier_code.includes("ZINC") ?
                                                                (<Button variant="link btn-sm"
                                                                    href={"https://zinc.docking.org/substances/" + p.supplier_code}
                                                                    rel="cartblanche">{p.supplier_code}</Button>)
                                                                :
                                                                (<Button variant="link btn-sm"

                                                                    onClick={() => searchSupplier(p.supplier_code)}
                                                                >{p.supplier_code}</Button>)


                                                        }

                                                    </td>


                                                    <td> {p.quantity} {p.unit}</td>
                                                    <td> {p.shipping} </td>
                                                    <td> {p.price} </td>
                                                </tr>
                                            </tbody>
                                        )}
                                </Table>
                            </Col>
                        </Row>
                    </Card.Body>
                </Card >
            }
            <ToastContainer></ToastContainer>
        </Container >
    )
}
