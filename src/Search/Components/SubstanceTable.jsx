import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Col, Row, Button, Card, Table, Pagination, Navbar, Spinner, Dropdown, Container, NavLink } from 'react-bootstrap';
import MoleculeStructure from '../../RDKit/MoleculeStructure';
import CsvDownloadButton from 'react-json-to-csv'
import Cart from "../../Cart/Cart";
import axios from "axios";
import { ToastContainer, toast } from 'react-toastify';
import { saveAs } from "file-saver";
const SubstanceTable = forwardRef((props, ref) => {
    const [molecules, setMolecules] = React.useState(props.molecules);
    const [substructure, setSubstructure] = React.useState(props.subStructure);
    const [loadingMols, setLoadingMols] = React.useState(props.load);
    const [page, setPage] = React.useState(1);
    const [perPage, setPerPage] = React.useState(50);
    const [loading, setLoading] = React.useState(false);

    const [total, setTotal] = React.useState(props.molecules.length);
    const [molCards, setMolCards] = React.useState([]);

    function buildPagination() {
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

    useEffect(() => {
        setPage(1);
    }, [perPage]);


    function downloadResults(format) {
        const id = toast.loading("Saving File...", {
            position: toast.POSITION.BOTTOM_LEFT,
            autoClose: 2000
        });

        axios({
            method: "get",
            url: "/search/saveResult/" + props.task + "." + format,

        }).then(response => {
            let res = response.data;
            toast.update(id, {
                render: "Saved!",
                type: toast.TYPE.SUCCESS,
                autoClose: 2000,
                isLoading: false,
            });
            format === 'json' ? res = JSON.stringify(res) : res = res;
            let blob = new Blob([res], { type: format });
            saveAs(blob, "results." + format);
        }).catch(error => {
            toast.update(id, {
                render: "Error!",
                type: toast.TYPE.ERROR,
                autoClose: 2000,
                isLoading: false,
            });
        });
    }


    return (
        <Container fluid>
            <Navbar bg="clear" className='m-1'>

                <Pagination className="mb-1">
                    <Pagination.First onClick={() => setPage(1)} />
                    <Pagination.Prev onClick={() => page <= 1 ? setPage(1) : setPage(page - 1)} />
                    {buildPagination()}
                    <Pagination.Next onClick={() => page >= Math.ceil(total / perPage) ? setPage(Math.ceil(total / perPage)) : setPage(page + 1)} />
                    <Pagination.Last onClick={() => setPage(Math.ceil(total / perPage))} />

                </Pagination>
                &nbsp;

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
                Per Page
                &nbsp;

                <Navbar.Collapse key="1" className='justify-content-end align-middle'>

                    <Dropdown>
                        <Dropdown.Toggle variant="success" id="dropdown-basic">
                            <i className="fa fa-download"></i>
                        </Dropdown.Toggle>

                        <Dropdown.Menu>
                            <Dropdown.Item key="json" onClick={() => downloadResults("json")}>JSON</Dropdown.Item>
                            <Dropdown.Item key="csv" onClick={() => downloadResults("csv")}>CSV</Dropdown.Item>
                            <Dropdown.Item key="txt" onClick={() => downloadResults("txt")}>TXT</Dropdown.Item>


                        </Dropdown.Menu>


                    </Dropdown>
                    &nbsp;
                    <Button>{total} {total === 1 ? "result" : "results"} </Button>

                </Navbar.Collapse>
            </Navbar>
            <Row>
                {loading && <Spinner animation="border" role="status" className="mx-auto">
                    <span className="visually-hidden">Loading...</span> </Spinner>}

                {!loading && total > 0 &&            // display molecules in cards

                    molecules.slice((page - 1) * perPage, page * perPage).map((molecule, index) => {

                        let incart = molecule.inCart;

                        return (

                            <Col lg={2} md={3} sm={4}>

                                <Card key={index} className="mb-3" >

                                    <Card.Header className=""
                                        style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}
                                    >
                                        <NavLink href={`/substance/${molecule.zinc_id}`} target="_blank">
                                            {molecule.zinc_id}
                                        </NavLink>
                                    </Card.Header>
                                    <Card.Body
                                        onClick={() => {
                                            if (incart) {
                                                molecules[molecules.indexOf(molecule)].inCart = false;
                                                props.removeMol(molecule)
                                            } else {
                                                molecules[molecules.indexOf(molecule)].inCart = true;
                                                props.addMol(molecule)
                                            }
                                        }}
                                        className={incart ? "bg-light" : ""}
                                    >
                                        <div
                                            className="molecule-structure"
                                        >
                                            <MoleculeStructure
                                                id={molecule.zinc_id}
                                                key={molecule.zinc_id}
                                                structure={molecule.smiles}
                                                svgMode
                                            />
                                            {
                                                incart === true ?
                                                    (<i className="fa fa-check-circle text-success" aria-hidden="true"
                                                        style={{ position: "absolute", bottom: "5%", left: "5%" }}
                                                    ></i>)
                                                    :
                                                    (incart === "sorta" ?
                                                        (<i className="fa fa-check-circle text-warning" aria-hidden="true"
                                                            style={{ position: "absolute", bottom: "5%", left: "5%" }}
                                                        ></i>)
                                                        :
                                                        null)



                                            }
                                        </div>

                                    </Card.Body>
                                </Card>

                            </Col>
                        )
                    })
                }

            </Row>
        </Container >
    )

})
export default SubstanceTable;
