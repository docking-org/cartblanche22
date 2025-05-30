import React from 'react';
import {
    useParams,
    Link,
    useLocation
} from "react-router-dom";
import { Container, Table, Tabs, Tab, Card, Row, Col, InputGroup, OverlayTrigger, Tooltip, Button, ButtonGroup, Dropdown, DropdownButton, Accordion } from "react-bootstrap";

import { useEffect } from 'react';

import Slider from '@mui/material/Slider';

import ResultsTable from '../Search/Components/ResultsTable';
import { ToastContainer } from 'react-toastify';
import Cart from '../Cart/Cart';

import "./sw.css";
import axios from 'axios';
import axiosRetry from 'axios-retry';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import initRDKit from '../utils/initRDKit';
import { Jsme } from 'jsme-react';

export default function SW(props) {
    

    const { findAndAdd } = Cart();
    const [cols] = React.useState({
        alignment: { name: "alignment", orderable: true, label: "" },
        dist: { name: "dist", orderable: true, label: "Distance" },
        ecfp4: { name: "ecfp4", orderable: true, label: "ECFP4" },
        daylight: { name: "daylight", orderable: true, label: "Daylight" },
        maj: { name: "maj", orderable: true, label: "Maj" },
        min: { name: "min", orderable: true, label: "Min" },
        hyb: { name: "hyb", orderable: true, label: "Hyb" },
        sub: { name: "sub", orderable: true, label: "Sub" },
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
    const [smi, setSmi] = React.useState(window.location.search.split("=")[1] ? decodeURIComponent(window.location.search.split("=")[1]) : "");
    const [db, setDB] = React.useState(Object.keys(maps)[0]);
    const [atomAlignment, setAtomAlignment] = React.useState(true);
    const [smartsAlignment, setSmartsAlignment] = React.useState(false);
    const [ecfp4, setecfp4] = React.useState(true);
    const [daylight, setDaylight] = React.useState(true);
    const [rdKit, setRDKit] = React.useState(null);
    const [smilesText, setSmilesText] = React.useState(smi);

    const useQuery = () => {
        return new URLSearchParams(useLocation().search);
      };
    const query = useQuery();
    const { smiles } = query.get("smiles") ? query.get("smiles") : "";

    if (smiles) {
        setSmi(decodeURIComponent(smiles));
        setSmilesText(decodeURIComponent(smiles));
    }


    const minDistance = 0;
    const ref = React.useRef();

    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);



    useEffect(() => {
        
        initRDKit().then((rdKit) => {
            setRDKit(rdKit);
        });
        getMaps();


    }, []);



    useEffect(() => {
        if (smi) {
            submitSearch(smi);
        }
    }, [db]);


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

    async function getMaps() {
        let res = await fetch(`https://${server}.docking.org/search/maps`,
            {
                credentials: server === "sw" ? "omit" : "include",

            }
        );
        res = await res.json();
     
        setMaps(res);
        setDB(Object.keys(res)[0])

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
            submitSearch(smi);
        }
        else {
            ref.current.getResults(hlid);
        }
    }


    async function submitSearch(smiles, fromJSME = false, fromText = false) {

        if (fromJSME) {
            setSmilesText(smiles);
        }
        else if (fromText) {

            setSmilesText(smiles);
            setSmi(smiles);
        }

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
        reqParams += `smi=${encodeURI(smiles)}`;
        reqParams += `&db=${db}`;

        sliders.forEach((item) => {
            reqParams += `&${item.name}=${item.value[1]}`;
        });
        // reqParams += "&scores=Atom%20Alignment,ECFP4,Daylight";
        reqParams += "&scores=" + (atomAlignment ? "Atom%20Alignment," : "") + (ecfp4 ? "ECFP4," : "") + (daylight ? "Daylight" : "") + (smartsAlignment ? ",SMARTS%20Alignment" : "");

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
                if (ref.current) {
                    ref.current.getResults(e.hlid, start);
                }
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
            console.log();
        }
        event.addEventListener("done", (e) => {
            event.close();
            setLoad(false);
        });

    }



    return (
        <Container className="mt-2 mb-2" fluid>


            <Row>
                <Col lg={4}>
                    <Jsme
                        src="/jsme/jsme.nocache.js"
                        height="250px"
                        onChange={(smiles) => {
                            console.log(smiles)
                            submitSearch(rdKit.get_mol(smiles).get_smiles(), true, false);
                        }}
                        smiles={(rdKit && rdKit.get_mol(smi).get_smiles()) ? rdKit.get_mol(smi).get_smiles(): ''}
                        options={"noautoez,newlook,nocanonize,multipart,zoom"}
                    />

                    <InputGroup className='mb-1 mt-1'
                        size='sm'
                    >
                        <InputGroup.Text>SMILES</InputGroup.Text>
                        <input
                            className="form-control"
                            value={smilesText}
                            id="inputSmiles"
                            onChange={(e) => {
                                submitSearch(e.target.value, false, true);
                            }}
                        />

                    </InputGroup>
                    <InputGroup
                        size='sm'
                        className='mb-1'
                    >
                        <InputGroup.Text>Dataset</InputGroup.Text>
                        <select
                            className="form-control"
                            value={db}
                            onChange={(e) => {

                                setDB(e.target.value);
                                submitSearch(smi);
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

                        <Card.Body
                            className='ps-1 px-1 pt-0 '
                        >
                            <Row
                                className=''
                                
                            >
                                {

                                    sliders.map((slider) => {
                                        return (

                                            <Col lg={slider.half ? 6 : 12}>
                                                <div className="d-flex justify-content-between ">
                                                    <b
                                                        style={{
                                                            width: slider.half ? "35%" : "27%",
                                                            textAlign: "start",
                                                            marginTop: "auto",
                                                            marginBottom: "auto",
                                                            fontSize: "0.55rem",
                                                            textWrap: "no-wrap",
                                                           
                                                        }}

                                                    >{slider.half ? slider.label.split(' ')[0] : slider.label}</b>

                                                    <div
                                                        style={{
                                                            width: slider.half ? "55%" : "70%",
                                                            display: "flex",
                                                        }}
                                                    >
                                                        <div
                                                         style={{
                                                            width: ".9rem",
                                                            textAlign: "start",
                                                            marginTop: ".4rem",
                                                            marginBottom: "auto",
                                                            fontSize: "0.55rem",
                                                            textWrap: "no-wrap",
                                                         }}
                                                        >
                                                            {slider.value[0]}
                                                        </div>
                                                
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
                                                    <div
                                                        style={{
                                                            
                                                            textAlign: "start",
                                                            marginTop: ".4rem",
                                                            marginBottom: "auto",
                                                            fontSize: "0.55rem",
                                                            textWrap: "no-wrap",
                                                        }}
                                                    >
                                                            {slider.value[1]} 
                                                            <b>
                                                            &nbsp;
                                                            
                                                            { slider.half && slider.label.split(' ')[1]}
                                                            </b>
                                                    </div>
                                                </div>
                                            </Col>
                                        );
                                    })
                                }

                            </Row>
                        </Card.Body>
                 


                    {/* <Card>
                        <Card.Header
                            className='p-0 ps-2'>
                            Scoring Methods
                        </Card.Header>
                        <Card.Body>
                            <input type={"checkbox"} checked={atomAlignment} onChange={(e) => {
                                setAtomAlignment(e.target.checked);
                                submitSearch(smi);
                            }} /> Atom Alignment
                            <br />
                            <input type={"checkbox"} checked={smartsAlignment} onChange={(e) => {
                                setSmartsAlignment(e.target.checked);
                                submitSearch(smi);
                            }} /> SMARTS Alignment
                            <br />
                            <input type={"checkbox"} checked={ecfp4} onChange={(e) => {
                                setecfp4(e.target.checked);
                                submitSearch(smi);
                            }} /> ECFP4
                            <br />
                            <input type={"checkbox"} checked={daylight} onChange={(e) => {
                                setDaylight(e.target.checked);
                                submitSearch(smi);
                            }} /> Daylight

                        </Card.Body>
                    </Card> */}
                    <p
                        style={{
                            fontSize: "0.6rem",
                            textAlign: "center",
                            marginTop: "auto",
                            marginBottom: "auto",
                            textWrap: "no-wrap",
                        }}
                    >
                    <br />
                    <img src="https://sw.docking.org/img/logo3_box.svg" width="20px" /> SmallWorld© 2015-2024 NextMove Software Ltd. All Rights Reserved.
                    <br />
                 
                    </p>

                    
                    
                </Col>
                <Col lg={8}>
                    <ResultsTable
                        ref={ref}
                        hlid={hlid}
                        cols={cols}
                        findAndAdd={findAndAdd}
                        server={server}
                        sliderValues={sliders}
                        db={db}
                        elapsed={elapsed}
                        loading={loading}
                    ></ResultsTable>
                </Col>
            </Row>

            <ToastContainer />
        </Container >

    );


}