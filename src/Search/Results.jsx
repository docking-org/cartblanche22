import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Container, Table, Tabs, Tab, Card, Button, Toast, Accordion, Form } from "react-bootstrap";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from "axios";
import SubstanceTable from "./Components/SubstanceTable";
import ProgressBar from 'react-bootstrap/ProgressBar';
import './search.css';
import { saveAs } from "file-saver";
import Cart from "../Cart/Cart";
import { useRef } from "react";

import NoResults from "../Errors/NoResults";
export default function Results(props) {
    const childRef = useRef();
    const { getCart, addToCart, removeFromCart, cartSize, inCart } = Cart();
    const [results, setResults] = React.useState([]);
    const [progress, setProgress] = React.useState(0);
    const [task, setTask] = React.useState(window.location.search.split("=")[1]);
    const [currentTab, setCurrentTab] = React.useState("zinc22");
    const [inUCSF, setInUCSF] = React.useState(false);
    const [load, setLoad] = React.useState(false);
    const [submission, setSubmission] = React.useState(undefined);
    const [logs, setLogs] = React.useState(undefined);
    const [noResults, setNoResults] = React.useState(false);
    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);

    function downloadAll(format) {
        axios({
            method: "get",
            url: "/search/result/" + task + "." + format,
        })
            .then(response => {
                var blob = new Blob([response.data], { type: "text/plain;charset=utf-8" });
                saveAs(blob, "result." + format);
            })
    }

    function getResult() {
        axios({
            method: "get",
            url: "/search/result/" + window.location.search.split("=")[1],
        })
            .then(response => {
                if (response.data.status === "SUCCESS") {

                    console.log(response.data);
                    setResults(response.data.result);

                    if (response.data.result.zinc22.length > 0) {
                        setCurrentTab("zinc22");
                    }
                    else if (response.data.result.zinc20 && (response.data.result.zinc20.length > 0)) {
                        setCurrentTab("zinc20");
                    }
                    else {
                        setNoResults(true);
                    }
                    setSubmission(response.data.submission);
                    setLogs(response.data.result.logs);
                    setInUCSF(response.data.inUCSF);
                }
                else {

                    if (response.data.progress * 100 < 1) {
                        setProgress(100);
                    }
                    else {
                        setProgress(Math.round(response.data.progress * 100, 2));
                    }

                    setTimeout(getResult, 500);
                }

            })
    }

    function allInCart(func = null) {
        let allInCart = true;
        if (results.zinc20) {
            results.zinc20.forEach(item => {

                item['inCart'] = inCart(item);

                if (!inCart(item)) {
                    allInCart = false;
                }

            })

        }
        if (results.zinc22) {
            results.zinc22.forEach(item => {
                item['inCart'] = inCart(item);

                if (!inCart(item)) {
                    allInCart = false;
                }
            })

        }


        return allInCart;
    }

    useEffect(() => {
        getResult();

    }, []);

    useEffect(() => {
        //
    }, [load]);

    function addMol(mol) {
        addToCart(mol);

        allInCart();
    }

    function removeMol(mol) {
        removeFromCart(mol);
        allInCart();
    }

    function showLoadingToast() {
        toast(
            <div className='d-flex justify-content-center'>
                <div className='spinner-border text-primary' role='status'>
                    <span className='sr-only'>Loading...</span>
                </div>
            </div>
            , {

                position: "bottom-left",

                autoClose: false,
            });
    }

    return (
        <>
            {noResults &&
                <NoResults
                    submission={submission}
                />}
            {!noResults &&
                <Container className="my-2 page-wrapper" fluid>

                    {progress > 0 && progress < 100 &&
                        !results.zinc22 && !results.zinc20 &&
                        <div
                            style={{ 'marginTop': '35vh' }}
                            className="justify-content-center align-items-center"

                        >
                            <ProgressBar key="progress" animated now={progress} label={`${progress}%`} />
                        </div>
                    }

                    {

                        (progress >= 100 || progress < 5) &&
                        !results.zinc22 && !results.zinc20 &&
                        <div
                            style={{ 'marginTop': '35vh' }}
                            className="justify-content-center align-items-center"

                        >
                            <ProgressBar key="loading" animated now={progress} label={`Searching...`} />
                        </div>
                    }

                    <Card>

                        <Tabs
                            id="results-tab"
                            activeKey={currentTab}

                            onSelect={
                                (key, event) => setCurrentTab(key)
                            }
                        >


                            {results.zinc22 && results.zinc22.length > 0 &&
                                <Tab eventKey="zinc22" title="ZINC22 Results"
                                    key={"zinc22"}


                                >
                                    <SubstanceTable
                                        ref={childRef}
                                        molecules={results.zinc22}
                                        load={load}
                                        addMol={addMol}
                                        removeMol={removeMol}
                                        task={task}
                                    />
                                </Tab>
                            }


                            {results.zinc20 && results.zinc20.length > 0 &&
                                <Tab eventKey="zinc20" title="ZINC20 Results"
                                    key="zinc20"
                                    onSelect={
                                        (key, event) => setCurrentTab(key)
                                    }

                                >
                                    <SubstanceTable
                                        molecules={results.zinc20}
                                        ref={childRef}
                                        load={load}
                                        addMol={addMol}
                                        removeMol={removeMol}
                                        task={task}
                                    />
                                </Tab>
                            }
                            {
                                (results.zinc20 || results.zinc22) &&

                                <Tab

                                    title={
                                        !allInCart() ?

                                            (<div size="sm"
                                                onClick={async () => {
                                                    let send = [];
                                                    if (results.zinc20) {
                                                        send = send.concat(results.zinc20);
                                                    }
                                                    if (results.zinc22) {
                                                        send = send.concat(results.zinc22);
                                                    }
                                                    addToCart(send)
                                                }}
                                            >
                                                <div className="bg-primary rounded text-white p-2" size="sm">Add all to cart</div>

                                            </div>)
                                            :
                                            (<div size="sm"
                                                onClick={async () => {
                                                    let send = [];
                                                    if (results.zinc20) {
                                                        send = send.concat(results.zinc20);
                                                    }
                                                    if (results.zinc22) {
                                                        send = send.concat(results.zinc22);
                                                    }
                                                    removeFromCart(send)
                                                }
                                                }
                                            >
                                                <div className="bg-danger rounded text-white p-2" size="sm">Remove all from cart</div>
                                            </div>)
                                    }
                                    key={"download"}
                                    tabClassName="add-to-cart"
                                >
                                </Tab>
                            }
                        </Tabs>



                    </Card >

                    <br />
                    {submission &&
                        <Accordion className="bottom-0 start-0 "
                            style={{ width: '100%' }}
                        >
                            <Accordion.Item eventKey="0">
                                <Accordion.Header>Original Submission ({submission.length})</Accordion.Header>
                                <Accordion.Body>
                                    <Form.Control as='textarea' rows={6}
                                        editable="false"
                                        disabled={true}
                                        value={submission.join('\n')}
                                    />
                                </Accordion.Body>
                            </Accordion.Item>
                            {inUCSF &&
                                <Accordion.Item eventKey="1">
                                    <Accordion.Header>Search Logs ({logs.length})</Accordion.Header>
                                    <Accordion.Body>
                                        <Form.Control as='textarea' rows={6}
                                            editable="false"
                                            disabled={true}
                                            value={logs.join('\n')}
                                        />
                                    </Accordion.Body>
                                </Accordion.Item>
                            }
                        </Accordion>
                    }
                </Container >
            }
            <ToastContainer />
        </>

    )
}
