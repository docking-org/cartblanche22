import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Card, Container, Row, Table, Col } from "react-bootstrap";
import axios from "axios";
import { saveAs } from "file-saver";
import Modal from 'react-bootstrap/Modal';
import { ToastContainer, toast } from 'react-toastify'; 

export default function RandomSearch(props) {
    const [loading, setLoading] = React.useState(false);
    const [jobid, setJobid] = React.useState("");
    const [id, setId] = React.useState("");
    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);

    function getMolecules() {
        var bodyFormData = new FormData();
        bodyFormData.append('count', document.getElementById("amountformat").value);
        bodyFormData.append('subset', document.getElementById("subset").value);
        const toast_id = toast.loading("Downloading...", {
            position: toast.POSITION.BOTTOM_LEFT,
            autoClose: false,
            progress: 0,

        });
        
        //request opens modal with loading spinner
        
        axios({
            method: "post",
            url: "/substance/random." + document.getElementById("format").value,
            data: bodyFormData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(response => {
                //download response as file with format, close modal
                
                setJobid(response.data.task);
                setTimeout(checkStatus(response.data.task, toast_id), 1000);
                // var blob = new Blob([response.data], { type: "text/plain;charset=utf-8" });
                // saveAs(blob, "random." + document.getElementById("format").value);
            })

    }

    function checkStatus(jobid, id) {
        axios({
            method: "get",
            url: "/substance/random/" + jobid + "." + document.getElementById("format").value,  
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(response => {
                if (response.data.status === "SUCCESS") {
                    //close modal, download file
                    
                    toast.update(id, {
                        render: "Done!",
                        type: toast.TYPE.SUCCESS,
                        autoClose: 2000,
                        progress: 100,
                        isLoading: false,
                    });
                    console.log(id)
                    var blob = new Blob([response.data.result], { type: "text/plain;charset=utf-8" });
                    saveAs(blob, "random." + document.getElementById("format").value);
                }
                else if(response.data.status === "PROGRESS"){
                    toast.update(id, {
                        render: "Downloading...",
                        type: toast.TYPE.INFO,
                        autoClose: false,
                        isLoading: false,
                        progress: response.data.progress,
                    });
                    setTimeout(checkStatus(jobid, id), 1000);
                }

                else if (response.data.status === "FAILURE") {
                    //close modal, download file
                    setLoading(false);
                    toast.update(id, {
                        render: "Error!",
                        type: toast.TYPE.ERROR,
                        autoClose: 2000,
                        isLoading: false,
                    });
                }
                else {
                    //check again
                    setTimeout(checkStatus(jobid, id), 1000);
                }
            })
    }

    return (
        <Container className="mt-2 mb-2">
            <Card>
                <Card.Header role="heading" aria-level="1"><b>Download Random Molecules</b></Card.Header>

                <Card.Body>
                    <form id='data' class="form-inline">
                        <div class="form-group">
                            <label for="fname">Subset: &nbsp;</label>
                            <select name="subset" class="btn btn-info" id="subset" aria-labelledby="Select subset">
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
                                    <input name="amount" class="form-control" id="amountformat" aria-labelledby="Input number of molecules"></input>
                                </Col>
                            </Row>


                            <br />
                            <label for="fname">Output Format: &nbsp;</label>

                            <select name="format" class="btn btn-info" id="format" aria-labelledby="Select output format">
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

            <Card className="mt-2" role="heading" aria-level="1">
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
                    <p>If you want to learn more about search, please go to <a href="https://wiki.docking.org/index.php/Zinc22:Searching"
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
            <ToastContainer />
        </Container >
        
    );

}
