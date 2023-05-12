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
    const minDistance = 0;
    const ref = React.useRef();

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

    async function submitSearch(smiles= null) {
        setResults([]);
        if(smiles){
            if(smiles !== params.smi && smiles !== patchedSmi){
                setParams({
                    ...params,
                    smi: smiles,
                });
                setPatchedSmi(rdKit.get_mol(smiles) ? rdKit.get_mol(smiles).get_smiles(): patchedSmi);
            }
        }


        if (ref.current) {
            ref.current.setPage(1);
            ref.current.getArthorResults(arthorSearchType);
        }



    }

    useEffect(() => {
        submitSearch();
    }, [arthorSearchType]);
    

    return (
        <Container className="mt-2 mb-2" fluid>

            <Row>
                <Col lg={4}>
                    <Jsme
                        width="100%"
                        height="350px"
                        onChange={(smiles) => {
                            submitSearch(smiles);
                        }}
                        smiles={patchedSmi}
                        options={"newlook,polarnitro,multipart,zoom"}
                    />

                    <Card className='mt-1 mb-1'>
                    <ButtonGroup>
                        <Button
                            disabled
                            size="sm"
                            variant="secondary" 
                        >
                            Search Type
                        </Button>
                        <Button
                            onClick={()=> setArthorSearchType("Similarity")}
                            variant={arthorSearchType === "Similarity"?  'primary':'secondary'}
                        >
                            Similarity
                        </Button>
                        <Button
                        onClick={()=> setArthorSearchType("Substructure")}
                        variant={arthorSearchType === "Substructure"?  'primary': 'secondary'}
                        >
                            Substructure
                        </Button>
                        <Button
                        onClick={()=> {
                            setArthorSearchType("SMARTS")
                        }}
                        variant={arthorSearchType === "SMARTS"? 'primary': 'secondary'}
                        >
                            SMARTS    
                        </Button>                            
                    </ButtonGroup>
                    </Card>
                    <InputGroup className='mb-1'>
                        <InputGroup.Text>{arthorSearchType !== "SMARTS" ? "SMILES" : "SMARTS"}</InputGroup.Text>
                        <input
                            className="form-control"
                            value={params.smi}
                            onChange={(e) => {
                                
                                submitSearch(e.target.value);
                            }}
                        />

                    </InputGroup>
                    
                    <InputGroup  className='mb-1'>
                        <InputGroup.Text>Dataset</InputGroup.Text>
                        <select
                            className="form-control"
                            value={params.db}
                            onChange={(e) => {
                                
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
                        style={{"fontSize": "10pt", "float":"right"}}
                    >
                        Database Information
                    </a>
                        <br></br>
                    

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
                        arthorSearchType = {arthorSearchType}
                    ></ResultsTable>
                </Col>
            </Row>

            <ToastContainer />
        </Container >

    );


}