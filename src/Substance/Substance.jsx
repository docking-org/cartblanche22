import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import {
  Container,
  Table,
  Tabs,
  Tab,
  Card,
  Row,
  Col,
  InputGroup,
  OverlayTrigger,
  Tooltip,
  Button,
  ButtonGroup,
  Dropdown,
  DropdownButton,
} from "react-bootstrap";
import axios from "axios";
import { useParams, Link } from "react-router-dom";

import { saveAs } from "file-saver";
import MoleculeStructure from "../RDKit/MoleculeStructure";
import Cart from "../Cart/Cart";
import { ToastContainer } from "react-toastify";
import useToken from "../utils/useToken";
import Substance404 from "../Errors/Substance404";

export default function Substance() {
  const { token } = useToken();
  const { getCart, addToCart, removeFromCart, cartSize, inCart, refreshCart } =
    Cart();
  const [results, setResults] = React.useState(undefined);
  const [progress, setProgress] = React.useState(0);
  const [id, setId] = React.useState(useParams().id);
  const [loading, setLoading] = React.useState(true);
  const [notFound, setNotFound] = React.useState(false);
  const [zinc20, setZinc20] = React.useState(false);

  useEffect(() => {
    document.title = id;
    if (id == undefined) {
      window.location.href = "/404";
    }
    refreshCart();
    getResult();
  }, []);

  useEffect(() => {
    if (results) {
      results.catalogs.map((catalog) => {
        if (catalog.supplier_code.includes("ZINC")) {
          setZinc20(true);
        }
      });
    }
  }, [results]);

  function searchSupplier(code) {
    var bodyFormData = new FormData();
    bodyFormData.append("supplier_codes", code);
    axios({
      method: "post",
      url: "/catitems.json",
      data: bodyFormData,
      headers: { "Content-Type": "multipart/form-data" },
    }).then((response) => {
      window.location.href = "/results?task=" + response.data.task;
    });
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
        Authorization: token ? `Bearer ${token}` : "",
      },
    }).then((response) => {
      if (format == "json") {
        var blob = new Blob([JSON.stringify(response.data)], {
          type: "text/plain;charset=utf-8",
        });
        saveAs(blob, "result." + format);
      } else {
        var blob = new Blob([response.data], {
          type: "text/plain;charset=utf-8",
        });
        saveAs(blob, "result." + format);
      }
    });
  }

  function getResult() {
    axios({
      method: "get",
      url: "/getSubstance/" + id,
    })
      .then((response) => {
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
      })
      .catch((error) => {
        setNotFound(true);
        setLoading(false);
      });
  }

  function isZinc20() {
    if (id) {
      let tempid = id.toUpperCase();
      if (!tempid.match(/ZINC[a-z]/i)) {
        return true;
      } else {
        return false;
      }
    }
  }

  return (
    <Container className="mt-2">
      {notFound ? <Substance404 id={id} /> : null}
      {loading ? (
        <div className="text-center m-4">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      ) : null}
      {results && (
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
                      {results.tranche ? (
                        <td>{results.tranche.h_num + results.tranche.p_num}</td>
                      ) : null}

                      <td>
                        {results.tranche_details.heavy_atoms}{" "}
                        {results.tranche ? `(${results.tranche.mwt})` : null}
                      </td>
                      <td>
                        {results.tranche_details.logp}{" "}
                        {results.tranche ? `(${results.tranche.logp})` : null}
                      </td>
                      <td>{results.tranche_details.mwt}</td>
                    </tr>
                  </tbody>
                </Table>
                <InputGroup className="mb-1">
                  <InputGroup.Text>SMILES</InputGroup.Text>
                  <input
                    type="text"
                    className="form-control"
                    disabled
                    value={results.smiles}
                  />

                  <Button
                    variant="outline-secondary"
                    onClick={() =>
                      navigator.clipboard.writeText(results.smiles)
                    }
                  >
                    <i className="fa fa-clipboard"></i>
                  </Button>
                </InputGroup>

                <InputGroup className="mb-1">
                  <InputGroup.Text>InChI</InputGroup.Text>
                  <input
                    type="text"
                    className="form-control"
                    disabled
                    value={results.tranche_details.inchi}
                  />

                  <Button
                    variant="outline-secondary"
                    onClick={() =>
                      navigator.clipboard.writeText(
                        results.tranche_details.inchi
                      )
                    }
                  >
                    <i className="fa fa-clipboard"></i>
                  </Button>
                </InputGroup>

                <InputGroup className="mb-1">
                  <InputGroup.Text>InChIKey</InputGroup.Text>
                  <input
                    type="text"
                    className="form-control"
                    disabled
                    value={results.tranche_details.inchikey}
                  />

                  <Button
                    variant="outline-secondary"
                    onClick={() =>
                      navigator.clipboard.writeText(
                        results.tranche_details.inchikey
                      )
                    }
                  >
                    <i className="fa fa-clipboard"></i>
                  </Button>
                </InputGroup>
                {isZinc20() && (
                  <Button
                    variant="outline-primary"
                    href={`https://zinc.docking.org/substances/${id}`}
                  >
                    View Molecule In ZINC20
                  </Button>
                )}
              </Col>
              <Col lg={4}>
                <Row>
                  <MoleculeStructure structure={results.smiles} svgMode />
                </Row>
                <Row>
                  <Col
                    lg={{
                      span: 6,
                      offset: 0,
                    }}
                  >
                    <DropdownButton
                      as={ButtonGroup}
                      title={"Find Similar"}
                      id="bg-nested-dropdown"
                      variant="secondary"
                    >
                      <Dropdown.Item
                        variant="warning"
                        href={
                          "/similarity/sw?smiles=" +
                          encodeURIComponent(results.smiles)
                        }
                      >
                        <div>Smallworld</div>
                      </Dropdown.Item>
                      <Dropdown.Item
                        variant="warning"
                        href={
                          "https://ab3.docking.org/search?smiles=" +
                          encodeURIComponent(results.smiles)
                        }
                      >
                        <div>Analog By Building Block</div>
                      </Dropdown.Item>
                    </DropdownButton>
                  </Col>

                  <Col
                    lg={{
                      span: 6,
                    }}
                  >
                    <div style={{ float: "right" }}>
                      <ButtonGroup>
                        {inCart(results) ? (
                          <Button
                            variant="danger"
                            onClick={() => removeFromCart(results)}
                          >
                            <div>Remove from Cart</div>
                          </Button>
                        ) : (
                          <Button
                            variant="primary"
                            onClick={() => addToCart(results)}
                          >
                            <div>Add to Cart</div>
                          </Button>
                        )}

                        <DropdownButton
                          as={ButtonGroup}
                          title={<i className="fa fa-download"></i>}
                          id="bg-nested-dropdown"
                          variant="secondary"
                        >
                          <Dropdown.Item
                            onClick={() => downloadResults("json")}
                          >
                            JSON
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => downloadResults("csv")}>
                            CSV
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => downloadResults("txt")}>
                            TXT
                          </Dropdown.Item>
                        </DropdownButton>
                      </ButtonGroup>
                    </div>
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
                            All prices listed below are estimated. Please check
                            with vendors directly to confirm the price.
                          </Tooltip>
                        }
                      >
                        <th>Price (USD) *</th>
                      </OverlayTrigger>
                    </tr>
                  </thead>
                  {results.catalogs.length === 0 ? (
                    <tbody>
                      <tr>
                        <td colSpan="5">No catalogs found</td>
                      </tr>
                    </tbody>
                  ) : (
                    results.catalogs.map((p, index) => (
                      <tbody>
                        <tr>
                          <td>{p.catalog_name}</td>
                          <td>
                            {p.supplier_code.includes("ZINC") ? (
                              <Button
                                variant="link btn-sm"
                                href={
                                  "https://zinc.docking.org/substances/" +
                                  p.supplier_code
                                }
                                rel="cartblanche"
                              >
                                {p.supplier_code}
                              </Button>
                            ) : isZinc20() ? (
                              <Button
                                variant="link btn-sm"
                                href={String(p.url).replace(
                                  "%%s",
                                  p.supplier_code
                                )}
                              >
                                {p.supplier_code}
                              </Button>
                            ) : (
                              <Button
                                variant="link btn-sm"
                                onClick={() => searchSupplier(p.supplier_code)}
                              >
                                {p.supplier_code}
                              </Button>
                            )}
                          </td>

                          <td>
                            {" "}
                            {p.quantity} {p.unit}
                          </td>
                          <td> {p.shipping} </td>
                          <td> {p.price} </td>
                        </tr>
                      </tbody>
                    ))
                  )}
                </Table>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}
      <ToastContainer></ToastContainer>
    </Container>
  );
}
