import React, { useEffect } from "react";
import useToken from "./utils/useToken.js";
import axios from "axios";
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button, OverlayTrigger, Tooltip } from "react-bootstrap";
export default function Footer() {
    

    return (
        <div className="footer bg-dark">
            <Container fluid>
                        {/* <a href="/acknowledgements">Acknowledgements</a>
                        &nbsp;
                        &nbsp; */}
                        <a href="https://wiki.docking.org/index.php/Zinc22:Searching">Usage</a>
                        &nbsp;
                        &nbsp;
                        <a href="mailto:chemistry4biology@gmail.com">Contact</a>
                        &nbsp;
                        &nbsp;
                        <a href="https://wiki.docking.org/index.php/Terms_And_Conditions"> Terms of Use </a>
                        &nbsp;
                        &nbsp;
                        <a href="https://wiki.docking.org/index.php/Privacy_policy"> Privacy Policy </a>
                        &nbsp;
                        &nbsp;
                        <a href="https://www.nigms.nih.gov/">Supported by NIGMS via GM71896</a>
                        &nbsp;
                        &nbsp;
                        <a href="https://irwinlab.compbio.ucsf.edu/">Irwin</a>, <a href="https://bkslab.org/">Shoichet</a> Labs and UC Regents
            </Container>
        </div>

    );
}