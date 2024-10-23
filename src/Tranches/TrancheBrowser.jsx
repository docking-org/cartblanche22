import React from 'react';
import { useEffect } from 'react';
import { Container, Navbar, Table, Col, Row, Nav, Form, Dropdown, Button, Modal } from 'react-bootstrap';
import DropdownMenu from 'react-bootstrap/esm/DropdownMenu';
import DropdownToggle from 'react-bootstrap/esm/DropdownToggle';
import NavbarToggle from 'react-bootstrap/esm/NavbarToggle';
import './tranches.css';
import TrancheTable from './TrancheTable';
import axios from 'axios';
import { useLocation, useParams } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import Cart from '../Cart/Cart';

export default function TrancheBrowser(props) {
    const { toastLoading, toast200, toastError } = Cart();
    const ref = React.useRef();
    const [activeCharges, setActiveCharges] = React.useState([]);
    const [activeSubset, setActiveSubset] = React.useState("all");
    const [activeGenerations, setActiveGenerations] = React.useState([]);
    const [total, setTotal] = React.useState(0);
    const [colSums, setColSums] = React.useState([]);
    const [trancheString, setTrancheString] = React.useState("");
    const [generations, setGenerations] = React.useState([]);
    const [tranches, setTranches] = React.useState(undefined);
    const [charges, setCharges] = React.useState([]);
    const [subsets, setSubsets] = React.useState([]);
    const [axes, setAxes] = React.useState([]);
    const [table, setTable] = React.useState([]);
    const [bigNumbers, setBigNumbers] = React.useState(false);
    const [filteredTranches, setFilteredTranches] = React.useState([]);
    const [downloadModal, setDownloadModal] = React.useState(false);

    const [selectedFormat, setSelectedFormat] = React.useState("");
    const [downloadFormat, setDownloadFormat] = React.useState("");
    const [downloadFormats, setDownloadFormats] = React.useState([]);
    const [downloadMethod, setDownloadMethod] = React.useState("");
    const [downloadMethods, setDownloadMethods] = React.useState([]);
    const [url, setUrl] = React.useState(useParams().tranches);

    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);

    useEffect(() => {
        fetch(`/tranches/get${url}`).then(res => res.json()).then(data => {
            console.log(data);

            setAxes(data.axes);
            setSubsets(data.subsets);
            setTranches(data.tranches);
            if (data.charges) {
                setCharges(data.charges);
                setActiveCharges(Object.keys(data.charges));
            }
            if (data.generations) {
                setGenerations(data.generations);
                setActiveGenerations(Object.keys(data.generations));
            }
            setDownloadFormats(data.formats);
            //Changing the default format to SMILES -2D
            //Changing the default format to DOCK38 -3D
            const smilesKey = Object.keys(data.formats).find(key => key.toUpperCase() === 'SMILES');
            const dock38Key = Object.keys(data.formats).find(key => key.toUpperCase() === 'DOCK38');
            if (dock38Key) {
                setDownloadFormat(dock38Key);
            } else if (smilesKey) {
                console.log("Setting default format to:", smilesKey);
            setDownloadFormat(smilesKey);
            } else {
                console.log("SMILES format not found, defaulting to:", Object.keys(data.formats)[0]);
                setDownloadFormat(Object.keys(data.formats)[0]);
            }
            setDownloadMethods(data.methods);
            //setDownloadFormat(Object.keys(data.formats)[1]);
            setDownloadMethod(Object.keys(data.methods)[0]);
            setFilteredTranches(data.tranches);
            setGenerations(data.generations);
            setActiveGenerations(data.generations);
        });

    }, []);


    useEffect(() => {
        if (tranches) {
            chooseSubset(activeSubset);
        }
    }, [activeCharges, activeGenerations]);


    function chooseSubset(subset) {
        console.log(subset)
        let t = [];
        if (subset === "all") {
            tranches.map(tranche => {
                if (activeCharges.length !== 0) {
                    if (activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation'])) {
                        tranche['chosen'] = true;

                    }
                }
                else if (charges.length === 0) {
                    tranche['chosen'] = true;

                } else {
                    tranche['chosen'] = false;

                }
                if ((activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation'])) || charges.length === 0) {
                    t.push(tranche);
                }
            });

            setActiveSubset("all")
        }
        else if (subset === "none") {
            tranches.map(tranche => {
                tranche['chosen'] = false;
                if (activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation']) || charges.length === 0) {
                    t.push(tranche);
                }
            });
            setActiveSubset("none");
        }
        else {
            setActiveSubset(subset);
            let minCol = subsets[subset][0][0] - 3;
            let maxCol = subsets[subset][0][1] - 3;
            let minRow = subsets[subset][1][0] - 3;
            let maxRow = subsets[subset][1][1] - 3;

            tranches.map(tranche => {
                let row = axes[0].indexOf(tranche['h_num']);
                let col = axes[1].indexOf(tranche['p_num']);

                if (col >= minCol
                    && col <= maxCol
                    && row >= minRow
                    && row < maxRow
                ) {
                    if (activeCharges.length !== 0) {
                        if (activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation'])) {
                            tranche['chosen'] = true;

                        }
                    }
                    else if (charges.length === 0) {
                        tranche['chosen'] = true;

                    } else {
                        tranche['chosen'] = false;

                    }
                    if (activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation']) || charges.length === 0) {
                        t.push(tranche);
                    }
                }
                else {
                    tranche['chosen'] = false;
                    if (activeCharges.includes(tranche['charge']) && activeGenerations.includes(tranche['generation']) || charges.length === 0) {
                        t.push(tranche);
                    }
                }

            });

        }
        setFilteredTranches(t);
        if (ref.current) {
            ref.current.refreshTable()
        }

    }

    function getTrancheString() {
        if (!ref.current) {
            return "";
        }
        //New code
        let t = ref.current.getCurrentTranches();
        console.log("Unsorted tranches:", t);

        // Sort the tranches
        t.sort((a, b) => {
            if (a.h_num < b.h_num) return -1;
            if (a.h_num > b.h_num) return 1;
        });

        console.log("Sorted tranches:", t);

        let trancheString = t.map(tranche => 
            (tranche.generation !== '-' ? tranche.generation : "") +
            tranche.h_num + tranche.p_num +
            (tranche.charge !== '-' ? tranche.charge : "")
        ).join(" ");

        setTrancheString(trancheString);
        //old code
        // let t = ref.current.getCurrentTranches();
        // console.log("Tranches:", t);
        // let trancheString = "";

        
        // t.map(tranche => trancheString +=
        //     (tranche['generation'] !== '-' ? tranche['generation'] : "") +
        //     tranche['h_num'] + tranche['p_num'] +
        //     (tranche['charge'] !== '-' ? tranche['charge'] : "") + " ");

        // setTrancheString(trancheString);
    }

    function downloadTranches() {
        let form = new FormData();
        form.append("format", downloadFormats[downloadFormat]);
        form.append("method", downloadMethods[downloadMethod]);
        form.append("tranches", trancheString);
        let toast = toastLoading("Downloading tranches...");

        let i = axios({
            method: "post",
            url: `/tranches/${url}/download`,
            data: form,
            headers: {
                "Content-Type": "multipart/form-data"
            }
        }
        ).then(res => {
            console.log(res.data);
            let blob = new Blob([res.data.data], { type: res.data.format });
            let link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = res.data.filename;
            link.click();
            toast200(toast, "Done!");
            setDownloadModal(false);
            setDownloadFormat(Object.keys(downloadFormats)[0]);
            setDownloadMethod(Object.keys(downloadMethods)[0]);
        });
    }

    return (
        <Container fluid
            className='mt-1 page-wrapper'

        >
            {
                !tranches &&
                <div className="d-flex mt-5 justify-content-center h-100">
                    <div className="spinner-border" role="status">
                        <span className="sr-only">Loading...</span>
                    </div>
                </div>
            }
            {tranches &&
                <>
                    {/* 
                         a navbar that says heavy atom count in  the middle, and generation on the far right
                         */}
                    <Navbar
                        className="top-bar"
                    >
                        <Container
                            fluid
                        >

                            <Navbar.Toggle aria-controls="basic-navbar-nav" />

                            <Navbar.Collapse>
                                <Nav className="">
                                    {generations &&
                                        <Dropdown
                                            align="start"
                                        >
                                            <DropdownToggle variant="outline-dark"
                                            >
                                                Layers
                                            </DropdownToggle>
                                            <DropdownMenu>
                                                <Dropdown.Item
                                                    onClick={() => setActiveGenerations(generations)}
                                                >
                                                    all
                                                </Dropdown.Item>
                                                <Dropdown.Item
                                                    onClick={() => setActiveGenerations([])}
                                                >
                                                    none
                                                </Dropdown.Item>
                                                <Dropdown.Divider />

                                                {generations.map(generation => {
                                                    return (
                                                        <Dropdown.Item
                                                            key={generation}
                                                            active={activeGenerations.includes(generation)}
                                                            onClick={() => {
                                                                if (activeGenerations.includes(generation)) {
                                                                    setActiveGenerations(activeGenerations.filter(g => g !== generation));
                                                                }
                                                                else {
                                                                    setActiveGenerations([...activeGenerations, generation]);
                                                                }
                                                            }}
                                                        >
                                                            {generation}
                                                        </Dropdown.Item>
                                                    )
                                                }
                                                )}


                                            </DropdownMenu>
                                        </Dropdown>
                                    }
                                </Nav>
                                <Nav className="mx-auto">
                                    <Nav.Item className="title-text">
                                        Heavy Atom Count
                                    </Nav.Item>
                                </Nav>
                                <Nav className="">

                                    <Form.Check
                                        type="switch"
                                        id="custom-switch"
                                        label=""
                                        checked={bigNumbers}
                                        onChange={() => setBigNumbers(!bigNumbers)}
                                        className="my-auto"
                                    />
                                    {subsets &&
                                        <Dropdown
                                            align="end"
                                            className='mx-1'
                                        >
                                            <DropdownToggle variant="outline-dark"
                                            >
                                                <i className="fas fa-layer-group"></i>
                                            </DropdownToggle>
                                            <DropdownMenu>
                                                <Dropdown.Item
                                                    onClick={() => chooseSubset("all")}
                                                >
                                                    all
                                                </Dropdown.Item>
                                                <Dropdown.Item
                                                    onClick={() => chooseSubset("none")}
                                                >
                                                    none
                                                </Dropdown.Item>
                                                <Dropdown.Divider />
                                                {Object.keys(subsets).map(subset => {
                                                    return (
                                                        <Dropdown.Item
                                                            key={subset}
                                                            active={activeSubset === subset}
                                                            onClick={() => chooseSubset(subset)}
                                                        >
                                                            {subset}
                                                        </Dropdown.Item>
                                                    )
                                                }
                                                )}
                                            </DropdownMenu>
                                        </Dropdown>
                                    }
                                    {Object.keys(charges).length > 0 &&
                                        <Dropdown
                                            align="end"
                                            className='mx-1'
                                        >
                                            <DropdownToggle variant="outline-dark"
                                            >
                                                Charge
                                            </DropdownToggle>
                                            <DropdownMenu>
                                                <Dropdown.Item
                                                    onClick={() => setActiveCharges(Object.keys(charges))}
                                                >
                                                    all
                                                </Dropdown.Item>
                                                <Dropdown.Item
                                                    onClick={() => setActiveCharges([])}
                                                >
                                                    none
                                                </Dropdown.Item>
                                                <Dropdown.Divider />
                                                {Object.keys(charges).map(charge => {
                                                    return (
                                                        <Dropdown.Item
                                                            active={activeCharges.includes(charge)}
                                                            key={charge}
                                                            onClick={() => {
                                                                if (activeCharges.includes(charge)) {
                                                                    setActiveCharges(activeCharges.filter(c => c !== charge));
                                                                }
                                                                else {
                                                                    setActiveCharges([...activeCharges, charge]);
                                                                }
                                                            }}
                                                        >
                                                            {charges[charge]}
                                                        </Dropdown.Item>
                                                    )
                                                }
                                                )}

                                            </DropdownMenu>
                                        </Dropdown>
                                    }
                                    <Nav.Item className="">
                                        <Button variant="outline-dark"
                                            onClick={() => setDownloadModal(true)}
                                        >
                                            <i className="fas fa-download"></i>
                                        </Button>
                                    </Nav.Item>

                                </Nav>
                            </Navbar.Collapse>
                        </Container>

                    </Navbar>

                    <TrancheTable
                        tranches={filteredTranches}
                        axes={axes}
                        bigNumbers={bigNumbers}
                        table={table}
                        ref={ref}

                    ></TrancheTable>
                </>
            }

            <Modal
                show={downloadModal}
                onHide={() => setDownloadModal(false)}
                onShow={() => {
                    getTrancheString();
                    console.log("Modal was opened with:", Object.keys(downloadFormats));
                    
                }}
            >
                <Modal.Header
                    closeButton

                >
                    <Modal.Title>Download</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group controlId="tranches">
                            <Form.Label>Tranches</Form.Label>
                            <Form.Control as='textarea' rows={6}
                                disabled
                                value={trancheString}


                            />
                        </Form.Group>
                        <Form.Group controlId='date'>
                            <Form.Label>Only if modified since</Form.Label>
                            <Form.Control type='date'

                            />
                        </Form.Group>
                        <Form.Group controlId="format">
                            <Form.Label>Format</Form.Label>
                            <Form.Control as="select"
                                value={downloadFormat}
                                onChange={(e) => setDownloadFormat(e.target.value)}
                            >
                                {Object.keys(downloadFormats).map(format => {
                                    return (
                                        <option key={format} value={format}>{format}</option>
                                    )
                                }
                                )}
                            </Form.Control>
                        </Form.Group>
                        <Form.Group controlId="method">
                            <Form.Label>Method</Form.Label>
                            <Form.Control as="select"
                                onChange={(e) => setDownloadMethod(e.target.value)}
                            >
                                {Object.keys(downloadMethods).map(method => {
                                    return (
                                        <option key={method}>{method}</option>
                                    )
                                }
                                )}
                            </Form.Control>
                        </Form.Group>
                        <br />
                        <Button variant="secondary" onClick={() => downloadTranches()}>
                            Download
                        </Button>
                    </Form>

                </Modal.Body>

            </Modal>
            <ToastContainer></ToastContainer>
        </Container >
    )
}