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

import "./sw.css";
import axios from 'axios';
import axiosRetry from 'axios-retry';

export default function SW(props) {
    const { findAndAdd } = Cart();
    const [cols] = React.useState({
        alignment: { name: "alignment", orderable: true, label: "" },
        dist: { name: "dist", orderable: true, label: "Distance" },
        ecfp4: { name: "ecfp4", orderable: true, label: "ECFP4" },
        daylight: { name: "daylight", orderable: true, label: "Daylight" },
    });
    axiosRetry(axios, { retries: 3 });
    const [results, setResults] = React.useState([]);
    const [loading, setLoad] = React.useState(false);
    const [config, setConfig] = React.useState({});
    const [hlid, setHlid] = React.useState(undefined);
    const [total, setTotal] = React.useState(0);
    const [server, setServer] = React.useState(useParams().server);
    const [currentEvent, setCurrentEvent] = React.useState(0);
    const [maps, setMaps] = React.useState({});
    const [elapsed, setElapsed] = React.useState(0);

    const minDistance = 0;
    const ref = React.useRef();

    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);


    const [params, setParams] = React.useState({
        smi: window.location.search.split("=")[1] ? decodeURIComponent(window.location.search.split("=")[1]) : "",
        db: Object.keys(maps)[0],
    });

    useEffect(() => {
        getMaps();
    }, []);

    const [sliders, setSliders] = React.useState([
        {
            name: "sdist",
            label: "Distance",
            min: 0,
            max: 16,
            maxSearch: 12,
            value: [0, 12],
            half: false,
        },
        {
            name: "dist",
            label: "Anonymous Distance",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: false,
        },
        {
            name: "tup",
            label: "Terminal Up",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "tdn",
            label: "Terminal Down",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "rup",
            label: "Ring Up",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "rdn",
            label: "Ring Down",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "lup",
            label: "Linker Up",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "ldn",
            label: "Linker Down",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "maj",
            label: "Mutation Up",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: true
        },
        {
            name: "min",
            label: "Mutation Down",
            min: 0,
            max: 8,
            value: [0, 4],

            maxSearch: 4,
            half: true
        },
        {
            name: "sub",
            label: "Substitution",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 4,
            half: false
        },
        {
            name: "hyb",
            label: "Hybridization",
            min: 0,
            max: 8,
            value: [0, 4],
            maxSearch: 8,
            half: false
        },
    ]);

    function getMaps() {

        axios.get(`https://${server}.docking.org/search/maps`,
            {
                withCredentials: server === "sw" ? false : true,

            }
        )
            .then((res) => {
                setMaps(res.data);
                setParams((prev) => {
                    return { ...prev, db: Object.keys(res.data)[0] }
                });
            }
            )
    }

    const handleSliderChangeDual = (
        event,
        newValue,
        activeThumb,
    ) => {
        if (!Array.isArray(newValue)) {
            return;
        }



        if (newValue[1] - newValue[0] < minDistance) {
            if (activeThumb === 0) {
                const clamped = Math.min(newValue[0], 100 - minDistance);
                setSliders((prev) => {
                    return prev.map((item) => {
                        if (item.name === event.target.name) {
                            return { ...item, value: [clamped, clamped + minDistance] }
                        }
                        return item;
                    })
                });

            } else {
                const clamped = Math.max(newValue[1], minDistance);
                setSliders((prev) => {
                    return prev.map((item) => {
                        if (item.name === event.target.name) {
                            return { ...item, value: [clamped - minDistance, clamped] }
                        }
                        return item;
                    })
                }
                );

            }
        } else {
            setSliders((prev) => {
                return prev.map((item) => {
                    if (item.name === event.target.name) {
                        return { ...item, value: newValue }
                    }
                    return item;
                })
            }
            );

        }


    };

    const handleSliderCommit = (event, newValue) => {
        //look through all sliders and see if any values[1] are greater than the maxSearch value
        //if so, set the maxSearch value to the value[1] value and create a new search
        //otherwise, trigger ref.current.getResults(hlid). this way the search is filtered and not re-run
        let newSearch = false;
        sliders.forEach((item) => {
            if (item.value[1] > item.maxSearch) {
                setSliders((prev) => {
                    return prev.map((item) => {
                        if (item.name === event.target.name) {
                            return { ...item, maxSearch: item.value[1] }
                        }
                        return item;
                    })
                }
                );
                newSearch = true;
            }
        }
        );
        if (newSearch) {
            submitSearch();
        }
        else {
            ref.current.getResults(hlid);
        }
    }


    async function submitSearch() {
        setResults([]);
        setLoad(true);
        setHlid("");
        setElapsed(0);
        let start = 0;
        if (currentEvent) {
            currentEvent.close();
        }
        if (ref.current) {
            ref.current.setPage(1);
        }
        let reqParams = "";
        reqParams += `smi=${encodeURIComponent(params.smi)}`;
        reqParams += `&db=${params.db}`;

        sliders.forEach((item) => {
            reqParams += `&${item.name}=${item.value[1]}`;
        });
        reqParams += "&scores=Atom%20Alignment,ECFP4,Daylight";

        const event = new EventSource(`https://${server}.docking.org/search/submit?${reqParams}`,
            {
                retry: 0,
                withCredentials: server === "sw" ? false : true,
            }
        );

        setCurrentEvent(event);

        event.onmessage = (e) => {
            e = JSON.parse(e.data);
            if (e.hlid) {
                setHlid(e.hlid);
                ref.current.getResults(e.hlid, start);
                start += 1;
            }
            if (e.elap) {
                setElapsed(e.elap);
                console.log(elapsed)
            }

        }
        event.onerror = (e) => {
            event.close();
            setLoad(false);
        }
        event.onopen = (e) => {
            console.log(e);
        }
        event.addEventListener("done", (e) => {
            event.close();
            setLoad(false);
        });

    }

    return (
        <Container className="mt-2 mb-2" fluid>
            <Card>
                <Card.Header><b>Similarity Search</b></Card.Header>
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
                                                <option value={key}>{maps[key].name}</option>
                                            )
                                        })
                                    }
                                </select>
                            </InputGroup>


                            <Accordion className="mt-2">
                                <Accordion.Item eventKey="0">
                                    <Accordion.Header>Advanced Options</Accordion.Header>
                                    <Accordion.Body eventKey="0">
                                        <Row>

                                            {

                                                sliders.map((slider) => {
                                                    return (

                                                        <Col lg={slider.half ? 6 : 12}>
                                                            <div className="d-flex justify-content-between m-1 border-bottom ">
                                                                <b
                                                                    style={{
                                                                        width: slider.half ? "35%" : "27%",
                                                                        textAlign: "start",
                                                                        marginTop: "auto",
                                                                        marginBottom: "auto",
                                                                        fontSize: "0.7rem",
                                                                        textWrap: "nowrap",
                                                                    }}

                                                                >{slider.label}</b>

                                                                <div
                                                                    style={{
                                                                        width: slider.half ? "55%" : "73%",

                                                                    }}
                                                                >
                                                                    <Slider
                                                                        size='small'
                                                                        name={slider.name}
                                                                        value={slider.value}
                                                                        onChange={handleSliderChangeDual}
                                                                        onChangeCommitted={handleSliderCommit}
                                                                        valueLabelDisplay="auto"
                                                                        aria-labelledby="range-slider"
                                                                        min={slider.min}
                                                                        max={slider.max}
                                                                        step={1}
                                                                        marks={[{
                                                                            value: slider.value[0],
                                                                            label: slider.value[0],
                                                                        },
                                                                        {
                                                                            value: slider.value[1],
                                                                            label: slider.value[1],
                                                                        },
                                                                        ]
                                                                        }
                                                                    />
                                                                </div>
                                                            </div>
                                                        </Col>
                                                    );
                                                })
                                            }
                                        </Row>
                                    </Accordion.Body>
                                </Accordion.Item>

                            </Accordion>

                            <br />
                        </Col>
                        <Col lg={8}>
                            <ResultsTable
                                ref={ref}
                                hlid={hlid}
                                cols={cols}
                                findAndAdd={findAndAdd}
                                server={server}
                                sliderValues={sliders}
                                db={params.db}
                                elapsed={elapsed}
                                loading={loading}
                            ></ResultsTable>
                        </Col>
                    </Row>
                </Card.Body>
            </Card >
            <ToastContainer />
        </Container >

    );


}