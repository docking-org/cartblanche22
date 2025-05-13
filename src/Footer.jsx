import React, { useEffect } from "react";
import useToken from "./utils/useToken.js";
import axios from "axios";
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button, OverlayTrigger, Tooltip } from "react-bootstrap";

export default function Footer() {
    return (
        <div className="footer bg-dark">
            <Container fluid className="text-center">
                <div>
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
                    &nbsp;
                    &nbsp;
                    Arthor/Smallworld by <a href="https://www.nextmovesoftware.com/">NextMove Software Ltd. </a>
                </div>
                <div style={{ marginTop: "15px", fontSize: "0.9em" }}>
                    © 1991-2025 UCSF DOCK team and the UC Regents, Department of Pharmaceutical Chemistry, UCSF
                </div>
                <div style={{ fontSize: "0.8em", marginTop: "5px" }}>
                    This is not an official UCSF website. The opinions or statements expressed herein should not be taken as a position of or endorsement by the University of California, San Francisco.
                </div>
            </Container>
        </div>
    );
}