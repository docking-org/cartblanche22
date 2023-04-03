import React from 'react';
import {
    useParams,
    Link,
} from "react-router-dom";
import { Container, Table, Tabs, Tab, Card, Row, Col, InputGroup, OverlayTrigger, Tooltip, Button, ButtonGroup, Dropdown, DropdownButton, Accordion } from "react-bootstrap";

import { useEffect } from 'react';
import { Jsme } from 'jsme-react';

import Slider from '@mui/material/Slider';

import ResultsTable from '../Search/Components/ResultsTable';
import { ToastContainer } from 'react-toastify';
import Cart from '../Cart/Cart';

import axios from 'axios';
import axiosRetry from 'axios-retry';

export default function Arthor() {
    const { findAndAdd } = Cart();
    const [cols] = React.useState({

    });
    axiosRetry(axios, { retries: 3 });
    const [results, setResults] = React.useState([]);
    const [loading, setLoad] = React.useState(false);

    const [hlid, setHlid] = React.useState(undefined);

    const [server, setServer] = React.useState(useParams().server);

    const [maps, setMaps] = React.useState({});
    const minDistance = 0;
    const ref = React.useRef();


    const [params, setParams] = React.useState({
        smi: window.location.search.split("=")[1] || "",
        db: maps[1] ? maps[1].displayName : [],
    });

    useEffect(() => {
        getMaps();
    }, []);


    function getMaps() {
        axios.get(`https://${server}.docking.org/dt/data`,
            {
                withCredentials: server === "arthor" ? false : true,
            }
        )
            .then((res) => {
                setMaps(res.data);
                setParams((prev) => {
                    return { ...prev, db: res.data[1].displayName }
                });
            }
            )
    }

    async function submitSearch() {
        setResults([]);


        if (ref.current) {
            ref.current.setPage(1);
            ref.current.getArthorResults();
        }



    }

    return (
        <Container className="mt-2 mb-2" fluid>
            <Card>
                <Card.Header><b>Pattern Search</b></Card.Header>
                <Card.Body>
                    <Row>
                        <Col lg={4}>
                            <Jsme
                                width="100%"
                                height="350px"
                                onChange={(smiles) => {
                                    setParams({
                                        ...params,
                                        smi: smiles,
                                    });

                                    submitSearch();
                                }}
                                smiles={params.smi}

                            />

                            <br />
                            <InputGroup className='mb-1'>
                                <InputGroup.Text>SMILES</InputGroup.Text>
                                <input
                                    className="form-control"
                                    value={params.smi}
                                    onChange={(e) => {
                                        setParams({
                                            ...params,
                                            smi: e.target.value,
                                        });
                                        submitSearch();
                                    }}
                                />

                            </InputGroup>
                            <InputGroup>
                                <InputGroup.Text>Dataset</InputGroup.Text>
                                <select
                                    className="form-control"
                                    value={params.db}
                                    onChange={(e) => {

                                        setParams({
                                            ...params,
                                            db: e.target.value,
                                        });
                                        submitSearch();
                                    }}
                                >
                                    {
                                        Object.keys(maps).map((key) => {
                                            return (
                                                <option value={maps[key].displayName}>{maps[key].displayName}</option>
                                            )
                                        })
                                    }
                                </select>
                            </InputGroup>




                            <br />
                        </Col>
                        <Col lg={8}>
                            <ResultsTable
                                ref={ref}
                                hlid={hlid}
                                cols={cols}
                                findAndAdd={findAndAdd}
                                server={server}
                                arthor={true}
                                db={params.db}
                                smi={params.smi}
                            ></ResultsTable>
                        </Col>
                    </Row>
                </Card.Body>
            </Card >
            <ToastContainer />
        </Container >

    );


}