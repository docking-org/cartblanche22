import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Col, Button, Card, Table, Pagination, Navbar, Spinner, Dropdown } from 'react-bootstrap';
import MoleculeStructure from "../../RDKit/MoleculeStructure";

import axios from 'axios';
import Cart from "../../Cart/Cart";
import { ToastContainer } from "react-toastify";
import ReactHtmlParser from 'react-html-parser';
import "./tables.css";



const ResultsTable = forwardRef((props, ref) => {
    const { findAndAdd, inCart, removeFromCart } = Cart();
    const [Results, setResults] = React.useState([]);
    const [total, setTotal] = React.useState(0);
    const [page, setPage] = React.useState(1);
    const [perPage, setPerPage] = React.useState(20);
    const [hlid, setHlid] = React.useState(props.hlid);
    const [cols] = React.useState(props.cols);
    const [loading, setLoading] = React.useState(false);
    const [currentEvent, setCurrentEvent] = React.useState(0);
    const [substructure, setSubstructure] = React.useState(null);

    useImperativeHandle(ref, () => ({
        getResults(hlid, draw, substructure = null) {
            getResults(hlid, draw, substructure);
        },
        getArthorResults() {
            getArthorResults();
        },
        setPage(page) {
            setPage(page);
        }
    }));


    function getArthorResults() {
        console.log("getArthorResults");

        let url = `https://${encodeURIComponent(props.server)}.docking.org/dt/${(props.db)}/search`
        url += `?query=${encodeURIComponent(props.smi)}`
        url += `&start=${(page - 1) * perPage}`;
        url += `&length=${perPage}`;
        url += `&flags=6144`;
        url += `&qopts=`;
        url += `&type=Substructure`;

        url = encodeURI(url);

        Object.keys(cols).map((key, index) => {
            url += `&${encodeURIComponent(`columns[${index}][data]`)}=${index}`;
            url += `&${encodeURIComponent(`columns[${index}][name]`)}=${cols[key].name}`;
            url += `&${encodeURIComponent(`columns[${index}][orderable]`)}=${cols[key].orderable}`;
            url += `&${encodeURIComponent(`columns[${index}][searchable]`)}=${cols[key].searchable}`;
            url += `&${encodeURIComponent(`columns[${index}][search][value]`)}=`;
            url += `&${encodeURIComponent(`columns[${index}][search][regex]`)}=false`;
        });
        axios.get(url, {
            withCredentials: props.server === "arthor" ? false : true,
        })
            .then((response) => {

                let res = []
                console.log(response.data);
                if (response.data.data) {
                    response.data.data.map((row, index) => {
                        let newRow = {};
                        newRow["id"] = row[1].split(" ")[1] || row[1].split("\t")[1] || row[1].split(" ")[0];
                        newRow["hitSmiles"] = row[1].split(" ")[0] || row[1].split("\t")[0] || row[1].split(" ")[0];
                        res.push([newRow]);

                    });
                }

                setResults(res);
                setTotal(response.data.recordsTotal > 20000 ? 20000 : response.data.recordsTotal);

                setLoading(false);
            }).catch((error) => {
                setResults([]);
                setTotal(0);
                setLoading(false);
            }
            );
    }

    function getResults(hlid, draw, substructure = null, start = (page - 1) * perPage) {
        let url = `https://${props.server}.docking.org/search/view?hlid=${hlid}`;
        let index = 0;
        Object.keys(cols).map((key, index) => {
            url += `&${encodeURIComponent(`columns[${index}][data]`)}=${index}`;
            url += `&${encodeURIComponent(`columns[${index}][name]`)}=${cols[key].name}`;
            url += `&${encodeURIComponent(`columns[${index}][orderable]`)}=${cols[key].orderable}`;
            index++;
        });
        if (props.sliderValues && props.sliderValues.length > 0) {
            props.sliderValues.map((slider, index) => {
                url += `&${encodeURIComponent(`columns[${index}][data]`)}=${index}`;
                url += `&${encodeURIComponent(`columns[${index}][name]`)}=${slider.name}`;
                url += `&${encodeURIComponent(`columns[${index}][min]`)}=${slider.min}`;
                url += `&${encodeURIComponent(`columns[${index}][searchable]`)}=true`;
                url += `&${encodeURIComponent(`columns[${index}][search][value]`)}=${slider.min}-${slider.value[1]}`;
                url += `&${encodeURIComponent(`columns[${index}][search][regex]`)}=false`;
                index++;
            });
        }

        url += `&${encodeURIComponent(`order[0][column]`)}=2`;
        url += `&${encodeURIComponent(`order[0][dir]`)}=desc`;
        url += `&start=${start}`;
        url += '&length=' + perPage;

        axios.get(url, {
            withCredentials: props.server === "sw" ? false : true
        }).then((response) => {
            setResults(response.data.data);

            setTotal(response.data.recordsTotal);
        }).catch((error) => {
            console.log(error);
        });
    }

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



    useEffect(() => {
        if (props.arthor) {
            getArthorResults();
        }
        else {
            getResults(props.hlid, props.draw, substructure, (page - 1) * perPage);
        }

    }, [page, perPage]);

    return (
        <>
            <Card>
                <Card.Header>{total.toLocaleString('en-US', { maximumFractionDigits: 2 })} results</Card.Header>
                <Card.Body>
                    <Navbar bg="clear" className=''>
                        <Pagination style={{ "marginBottom": "auto", }}>
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
                        &nbsp;

                        <Navbar.Collapse className='justify-content-end align-middle'>


                            <Button variant="success" id="dropdown-basic"
                                onClick={() => {
                                    let url = `https://${props.server}.docking.org/search/export?hlid=${props.hlid}`;
                                    Object.keys(cols).map((key, index) => {
                                        url += `&${encodeURIComponent(`columns[${index}][data]`)}=${index}`;
                                        url += `&${encodeURIComponent(`columns[${index}][name]`)}=${cols[key].name}`;
                                        url += `&${encodeURIComponent(`columns[${index}][orderable]`)}=${cols[key].orderable}`;
                                    });
                                    url += `&${encodeURIComponent(`order[0][column]`)}=2`;
                                    url += `&${encodeURIComponent(`order[0][dir]`)}=desc`;
                                    url += `&start=0`;
                                    url += '&length=' + total;
                                    window.open(url, '_blank');

                                }}>
                                <i className="fa fa-download" aria-hidden="true"></i>
                            </Button>
                        </Navbar.Collapse>
                    </Navbar>


                    <Table striped bordered hover className="">
                        <thead>
                            <tr>
                                <th>
                                    <i className="fa fa-shopping-cart" aria-hidden="true"></i>
                                </th>
                                <th></th>

                                {Object.keys(cols).map((key, index) => (
                                    <th key={index}>{cols[key].label}</th>
                                ))}
                                {
                                    props.arthor ?
                                        (
                                            <>
                                                <th>
                                                    ID
                                                </th>
                                                <th>
                                                    SMILES
                                                </th>
                                            </>
                                        )
                                        :
                                        null
                                }
                            </tr>
                        </thead>
                        {total === 0 &&
                            < tbody >
                                <tr>
                                    <td colSpan="100">
                                        <div className="text-center">
                                            No results found.
                                        </div>

                                    </td>
                                </tr>
                            </tbody>
                        }
                        {!loading && total > 0 &&
                            <tbody className="results-table">
                                {Results.map((molecule, index) => (

                                    <tr className="align-middle"
                                        onClick={() => {
                                            if (inCart(molecule[0].id)) {
                                                removeFromCart(molecule[0].id);
                                            }
                                            else {
                                                findAndAdd(molecule[0].id, props.db, molecule[0].hitSmiles);

                                            }
                                        }}
                                        key={index}>
                                        <td>
                                            {inCart(molecule[0].id) === true ?

                                                (<i className="fa fa-check-circle text-success" aria-hidden="true"
                                                    style={{ bottom: "5%", left: "5%" }}
                                                ></i>)
                                                :
                                                (inCart(molecule[0].id) === "sorta" ?
                                                    (<i className="fa fa-check-circle text-warning" aria-hidden="true"
                                                        style={{ bottom: "5%", left: "5%" }}
                                                    ></i>)
                                                    :
                                                    null)

                                            }
                                        </td>
                                        <td
                                            className="molecule-structure"
                                            style={{ "width": props.arthor ? "200px" : "100px" }}
                                        >
                                            <MoleculeStructure id={molecule[0].hitSmiles} structure={molecule[0].hitSmiles} height={100} width={100} svgMode
                                                subStructure={props.smi}
                                            />

                                        </td>
                                        <td
                                            className="mol-info"
                                        >
                                            <p><b>{

                                                molecule[0].id.includes("ZINC") ?
                                                    <a href={`/substance/${molecule[0].id}`} target="_blank" rel="noopener noreferrer">{molecule[0].id}</a>
                                                    :
                                                    molecule[0].id

                                            }</b></p>
                                            {molecule[0].anonIdx &&
                                                <p><b>SWIDX: </b>{molecule[0].anonIdx}</p>}
                                            {molecule[0].mf &&
                                                <p><b>MF: </b>{ReactHtmlParser(molecule[0].mf)}</p>}
                                            {molecule[0].mw &&
                                                <p><b>MW:</b> {molecule[0].mw}</p>}
                                        </td>
                                        {
                                            props.arthor &&
                                            <td
                                            >
                                                <p

                                                    style={{ "overflowWrap": "break-word" }}
                                                ><b>{molecule[0].hitSmiles}</b></p>
                                            </td>
                                        }
                                        {
                                            molecule[1] ? <td>{molecule[1]}</td> : null
                                        }
                                        {
                                            molecule[2] ? <td>{parseFloat(molecule[2]).toFixed(2)}</td> : null
                                        }
                                        {
                                            molecule[3] ? <td>{parseFloat(molecule[3]).toFixed(2)}</td> : null
                                        }


                                    </tr>
                                ))}
                            </tbody>
                        }
                    </Table>

                </Card.Body>

            </Card>

        </>
    )

})
export default ResultsTable;
