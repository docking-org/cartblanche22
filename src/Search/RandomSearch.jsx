import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Card, Container, Row, Table, Col } from "react-bootstrap";
import axios from "axios";
import { saveAs } from "file-saver";
import Modal from 'react-bootstrap/Modal';

export default function RandomSearch(props) {
    const [loading, setLoading] = React.useState(false);

    useEffect(() => {
        document.title = props.title || "";
      }, [props.title]);

    function getMolecules() {
        var bodyFormData = new FormData();
        bodyFormData.append('count', document.getElementById("amountformat").value);
        bodyFormData.append('subset', document.getElementById("subset").value);

        //request opens modal with loading spinner
        setLoading(true);

        axios({
            method: "post",
            url: "/substance/random." + document.getElementById("format").value,
            data: bodyFormData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(response => {
                //download response as file with format, close modal
                setLoading(false);
                var blob = new Blob([response.data], { type: "text/plain;charset=utf-8" });
                saveAs(blob, "random." + document.getElementById("format").value);
            })
    }


    return (
        <Container className="mt-2 mb-2">
            <Card>
                <Card.Header><b>Search by supplier codes, one per line</b></Card.Header>

                <Card.Body>
                    <form id='data' class="form-inline">
                        <div class="form-group">
                            <label for="fname">Subset: &nbsp;</label>
                            <select name="subset" class="btn btn-info" id="subset">
                                <option value="none" id="subset-none" selected>
                                    None
                                </option>
                                <option value="lead-like" id="subset-lead-like">
                                    Lead-like
                                </option>
                            </select>
                            <br /><br />


                            <Row>

                                <Col sm={12} lg={3}>
                                    <label for="fname">Number of molecules: &nbsp;</label>
                                    <input name="amount" class="form-control" id="amountformat" ></input>
                                </Col>
                            </Row>


                            <br />
                            <label for="fname">Output Format: &nbsp;</label>

                            <select name="format" class="btn btn-info" id="format">
                                <option value="txt" id="format-txt" selected>
                                    .txt
                                </option>
                                <option value="csv" id="format-csv">
                                    .csv
                                </option>
                                <option value="json" id="format-json">
                                    .json
                                </option>
                            </select>
                            <br />
                            <br />
                            <button class="btn btn-primary" type="submit"
                                onClick={

                                    (e) => {
                                        e.preventDefault();
                                        getMolecules();
                                    }

                                }
                            >
                                <i class="glyphicon glyphicon-download-alt"></i>
                                Download
                            </button>
                        </div>
                    </form>
                </Card.Body>
            </Card>

            <Card className="mt-2">
                <Card.Header><b>CURL commands for dowloading random molecules</b></Card.Header>
                <Card.Body>

                    <p>Example:
                        <code> curl https://cartblanche22.docking.org/substance/random.txt -F count=100 -F subset='lead-like'</code>
                    </p>

                    <p>
                        - Results can be formatted in the desired file format.
                        <br />
                        - All available molecule data is returned.

                    </p>
                    <Table bordered striped hover>
                        <thead>
                            <tr>
                                <th class="col-md-4">Description</th>
                                <th class="col-md-5">Attributes</th>
                                <th class="col-md-3">Possible fields</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>To specify return format</td>
                                <td><code>curl https://cartblanche22.docking.org/substances<i>.txt</i></code></td>
                                <td>
                                    <ul>
                                        <li>.txt</li>
                                        <li>.csv</li>
                                        <li>.json</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>To specify the number of molecules returned</td>
                                <td> <code>-F count=100<i></i></code></td>
                                <td>
                                    <ul>
                                        <li>Any integer under 300,000</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>To specify subset
                                    <br />

                                    <small>If no subset is defined, the batch will be retrieved from all available molecules.</small>
                                </td>
                                <td>
                                    <code>-F subset=<i>'lead-like'</i></code>
                                </td>
                                <td>
                                    <ul>
                                        <li>lead-like</li>
                                    </ul>
                                </td>
                            </tr>
                        </tbody>
                    </Table>
                    <p>If you want to learn more about search, please go to <a href="http://wiki.docking.org/index.php/Zinc22:Searching"
                        target="_blank"> Zinc22 documentation on wiki
                        page</a></p>
                </Card.Body>
            </Card>

            <Modal show={loading}>
                <Modal.Header closeButton>
                    <Modal.Title>Downloading...</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div className="d-flex justify-content-center">
                        <div className="spinner-border" role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                </Modal.Body>
            </Modal>
        </Container >
    );

}
