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

import initRDKit from '../utils/initRDKit';
import { exactProp } from '@mui/utils';
import { parseArgs } from 'util';

export default function Arthor(props) {
    const { findAndAdd } = Cart();
    const [cols] = React.useState({

    });


    axiosRetry(axios, { retries: 3 });
    const [results, setResults] = React.useState([]);
    const [loading, setLoad] = React.useState(false);

    const [hlid, setHlid] = React.useState(undefined);
    const [rdKit, setRdKit] = React.useState(undefined);
    const [server, setServer] = React.useState(useParams().server);
    const [arthorSearchType, setArthorSearchType] = React.useState("Substructure")
    const [maps, setMaps] = React.useState({});
    const [patchedSmi, setPatchedSmi] = React.useState("");
    const [ringSystems, setRingSystems] = React.useState(true);
    const [chains, setChains] = React.useState(true);
    const [properties, setProperties] = React.useState(true);
    const [smilesText, setSmilesText] = React.useState("");
    const [smi, setSmi] = React.useState("");
    const ref = React.useRef();

    //making a table of search flags
    //when ring systems, chains, and properies are true, the flag is 7680
    //when chains and properties are true, the flag is 7168
    //when ring systems and properties are true, the flag is 6656
    //when only properties are true, the flag is 1536
    //when only chains are true, the flag is 1024
    //when only ring systems are true, the flag is 512
    //when ring systems, chains are true and properties are false, the flag is 6144
    // if ring syst4em and chains are false, properties has to be true always

    const [searchFlags, setSearchFlags] = React.useState({
        "7680": [true, true, true],
        "7168": [false, true, true],
        "6656": [true, false, true],
        "1536": [false, false, true],
        "1024": [false, true, false],
        "512": [true, false, false],
        "6144": [true, true, false],
    });

    useEffect(() => {
        document.title = props.title || "";
    }, [props.title]);

    const [params, setParams] = React.useState({
        smi: window.location.search.split("=")[1] || "",
        db: maps[1] ? maps[1].displayName : [],
    });

    useEffect(() => {
        initRDKit().then((rdKit) => {
            setRdKit(rdKit);
        });
        getMaps();
    }, []);

    async function getMaps() {
        let res = await fetch(`https://${server}.docking.org/dt/data`,
            {
                credentials: server === "arthor" ? "omit" : "include",
            }
        )
        res = await res.json();
        setMaps(res);
        setParams((prev) => {
            return { ...prev, db: res[1].displayName }
        });

    }

    async function submitSearch(smiles = null, fromJSME = false, fromText = false) {
        if (fromJSME) {
            setSmilesText(smiles);
        }
        else if (fromText) {
            setSmilesText(smiles);
            setSmi(smiles);
        }

        let array = [ringSystems, chains, properties];
        console.log(array);
        let searchFlag = Object.keys(searchFlags).find(key => JSON.stringify(searchFlags[key]) === JSON.stringify(array));
        console.log(searchFlag);
        setResults([]);



        if (ref.current) {
            ref.current.setPage(1);
            ref.current.getArthorResults(arthorSearchType, searchFlag);
        }



    }

    useEffect(() => {
        submitSearch();
    }, [arthorSearchType]);

    useEffect(() => {
        (!ringSystems && !chains) ? setProperties(true) : console.log()
        submitSearch();
    }, [ringSystems, chains, properties]);

    return (
        <Container className="mt-2 mb-2" fluid>

            <Row>
                <Col lg={4}>
                    <Jsme
                        src="/jsme/jsme.nocache.js"
                        height="350px"
                        onChange={(smiles) => {

                            submitSearch(rdKit.get_mol(smiles).get_smiles(), true, false);
                        }}
                        smiles={rdKit ? rdKit.get_mol(smi).get_smiles() : ''}
                        options={"noautoez,newlook,nocanonize,multipart,zoom"}
                    />

                    <InputGroup className='mb-1 mt-1'>
                        <InputGroup.Text>{arthorSearchType !== "SMARTS" ? "SMILES" : "SMARTS"}</InputGroup.Text>
                        <input
                            className="form-control"
                            value={smilesText}
                            onChange={(e) => {
                                submitSearch(e.target.value, false, true);
                            }}
                        />

                    </InputGroup>


                    <InputGroup className='mb-1'>
                        <InputGroup.Text>Dataset</InputGroup.Text>
                        <select
                            className="form-control"
                            value={params.db}
                            onChange={(e) => {
                                setParams((prev) => {
                                    return { ...prev, db: e.target.value }
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
                    <a

                        href="https://wiki.docking.org/index.php/Smallworld_and_Arthor_Databases#Smallworld_Databases"
                        style={{ "fontSize": "10pt", "float": "right" }}
                    >
                        Database Information
                    </a>
                    <br></br>

                    <Card className='mt-1 mb-1'
                        style={{ width: "100%" }}
                    >
                        <ButtonGroup
                            style={{ width: "100%", "font-size": "2vw" }}
                        >
                            <Button
                                disabled
                                size="sm"
                                variant="secondary"
                                style={{ "font-size": "0.7vw" }}
                            >
                                Search Type
                            </Button>
                            <Button
                                onClick={() => setArthorSearchType("Similarity")}
                                variant={arthorSearchType === "Similarity" ? 'primary' : 'secondary'}
                                style={{ "font-size": "1vw" }}
                            >
                                Similarity
                            </Button>
                            <Button
                                onClick={() => setArthorSearchType("Substructure")}
                                variant={arthorSearchType === "Substructure" ? 'primary' : 'secondary'}
                                style={{ "font-size": "1vw" }}
                            >
                                Substructure
                            </Button>
                            <Button
                                style={{ "font-size": "1vw" }}
                                onClick={() => {
                                    setArthorSearchType("SMARTS")
                                }}
                                variant={arthorSearchType === "SMARTS" ? 'primary' : 'secondary'}
                            >
                                SMARTS
                            </Button>
                        </ButtonGroup>
                    </Card>
                    <Card className='mt-1 mb-1'
                        style={{ width: "100%" }}
                    >
                        <ButtonGroup
                            style={{ width: "100%" }}
                        >

                            <Button
                                style={{ "font-size": "0.8vw", 'white-space': 'nowrap' }}
                                variant="outline-secondary"
                                onClick={() => {
                                    setRingSystems(!ringSystems);
                                }
                                }
                            >
                                {ringSystems ? <i className="fas fa-lock"></i> : <i className="fas fa-lock-open"></i>} &nbsp;
                                Ring Systems
                            </Button>
                            <Button
                                style={{ "font-size": "0.8vw", 'white-space': 'nowrap' }}
                                variant="outline-secondary"
                                onClick={() => {
                                    setChains(!chains);
                                }
                                }
                            >
                                {chains ? <i className="fas fa-lock"></i> : <i className="fas fa-lock-open"></i>} &nbsp;
                                Chains
                            </Button>
                            <Button
                                style={{ "font-size": "0.8vw", 'white-space': 'nowrap' }}
                                variant="outline-secondary"
                                onClick={() => {
                                    if (!chains && !ringSystems) {
                                        setProperties(true);
                                    }
                                    else {
                                        setProperties(!properties);
                                    }
                                }
                                }
                            >
                                {properties ? <i className="fas fa-lock"></i> : <i className="fas fa-lock-open"></i>} &nbsp;
                                &nbsp;
                                Properties
                            </Button>
                        </ButtonGroup>
                    </Card>





                    <br />

                    <p
                        style={{
                            fontSize: "0.7rem",
                            textAlign: "center",
                            marginTop: "auto",
                            marginBottom: "auto",
                            textWrap: "no-wrap",
                        }}
                    >
                    <br />
                    <img src="https://arthor.docking.org/img/arthor_bandit_crop_32x32.png" width="40px" /> Arthor© 2018-2023 NextMove Software Ltd. All Rights Reserved.
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
                        arthor={true}
                        db={params.db}
                        smi={params.smi}
                        arthorSearchType={arthorSearchType}
                    ></ResultsTable>
                </Col>
            </Row>

            <ToastContainer />
        </Container >

    );


}