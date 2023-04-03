import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Card, Container, Table } from "react-bootstrap";
import axios from "axios";
import useToken from "../utils/useToken";

export default function SupplierSearch() {
    const [input, setInput] = React.useState("");
    const { token } = useToken();
    function getMolecules() {
        var bodyFormData = new FormData();
        bodyFormData.append('supplier_codes', input);

        var file = document.getElementById("supplierfile").files[0];
        if (file) {
            bodyFormData.append('supplier_codes', file);
        }
        axios({
            method: "post",
            url: "/catitems.json",
            data: bodyFormData,
            headers: {
                "Content-Type": "multipart/form-data",
                "Authorization": token ? `Bearer ${token}` : "",
            },
        })
            .then(response => {
                window.location.href = "/results?task=" + response.data.task;
            })
    }

    function loadTestData() {
        setInput("s_240690__16499450__15795350\ns_240690__16499450__17311340\ns_22__9598818__14482412\n");
    }

    return (
        <Container className="mt-2 mb-2">
            <Card>
                <Card.Header><b>Search by supplier codes, one per line</b></Card.Header>

                <Card.Body>
                    <form id="data" onSubmit={(e) => e.preventDefault()}>
                        <div class="form-group">
                            <textarea id="supplierTextarea" class="form-control" rows="6" cols="20"
                                value={input} onChange={e => setInput(e.target.value)}
                                placeholder="Supplier Codes" name="supplierTextarea"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="supplierfile">OR Upload a File (.txt only):</label>
                            <input type="file" id="supplierfile" name="supplierfile"
                                class="form-control" accept=".txt" />
                        </div>
                        <button id="searchSupplierBtn" type="submit" class="btn btn-info m-1"
                            onClick={getMolecules}
                        >Search</button>
                        <button id="testData" class="btn btn-secondary m-1"
                            onClick={loadTestData}
                        >Load Test Data</button>
                    </form>
                </Card.Body>
            </Card>

            <Card className="mt-2">
                <Card.Header>
                    <b>CURL commands for searching by supplier code</b>

                </Card.Header>
                <Card.Body>
                    <p>Example: <code>curl https://cartblanche22.docking.org/smiles.txt -F smiles-in=@smiles.txt -F dist=4 -F adist=4</code></p>

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
                                <th class="col-md-3">Parameters</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>To specify return format</td>
                                <td><code>curl https://cartblanche22.docking.org/catitems<i>.txt</i></code></td>
                                <td><ul>
                                    <li>.txt</li>
                                    <li>.csv</li>
                                    <li>.json</li>
                                </ul></td>
                            </tr>
                            <tr>
                                <td>To add search value</td>
                                <td> <code>-F supplier_code-in=<i>@sup.txt</i></code></td>
                                <td>.txt file with list of supplier codes</td>
                            </tr>
                        </tbody>
                    </Table>
                    <p>If you want to learn more about search, please go to <a href="http://wiki.docking.org/index.php/Zinc22:Searching"
                        target="_blank"> Zinc22 documentation on wiki
                        page</a></p>
                </Card.Body>
            </Card>
        </Container >
    );

}
