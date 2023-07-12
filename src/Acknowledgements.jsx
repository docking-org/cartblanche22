import React, { useEffect } from "react";
import useToken from "./utils/useToken.js";
import axios from "axios";
import { Container, Row, Col, Form, Navbar, Nav, NavDropdown, Modal, Button, OverlayTrigger, Tooltip } from "react-bootstrap";
export default function Acknowledgements() {
    

    return (
        <Container>
    
      <div class="row">
        <div class="col-md-5 col-lg-4">
          <div class="row">
            <div class="col-xs-6 col-md-12 bg-light border rounded-3 m-4 mt-1 p-3">
              <h2 class="display-7">Getting Started</h2>
              <ul>
                <li>
                  Select database subset in <a href="/tranches/2d">2D</a>
                </li>
                <li>
                  Select database subset in <a href="/tranches/3d">3D</a>
                </li>

                <li>
                  <a href="/sw">Search for similar molecules using Smallworld</a>
                </li>
                <li>
                  <a href="/arthor">Search by Substructure or SMARTS using Arthor</a>
                </li>
                <li>
                  <a href="/search/zincid">Lookup molecules by ZINC ID</a>
                </li>

                <li>
                  <a href="/search/catitems">Lookup molecules by supplier code</a>
                </li>
                <li>
                  <a href="/search/smiles">Lookup molecules by SMILEs in bulk</a>
                </li>
                <li>
                  <a href="/search/random">Select random molecules</a>
                </li>

              </ul>
            </div>
          </div>
        </div>
        &nbsp;
        <div class="col-md-4 col-lg-4 bg-light border rounded-3 m-4 mt-1 p-3">
          <h2 class="display-7">More about Zinc22</h2>
          <ul>
            <li>
              <a href="https://wiki.docking.org/index.php/ZINC22:Getting_started">How to get started with ZINC-22</a>
            </li>
            <li>
              <a href="https://wiki.docking.org/index.php/Zinc22:Searching">Searching ZINC-22</a>
            </li>
            <li>
              <a href="https://wiki.docking.org/index.php/Selecting_tranches_in_ZINC22">Selecting tranches in ZINC22</a>
            </li>
            <li>
              <a href="https://wiki.docking.org/index.php/ZINC22:Downloading">Downloading ZINC22</a>
            </li>
            <li>
              <a href="https://wiki.docking.org/index.php/ZINC22:Why">Why ZINC22?</a>
            </li>
          </ul>
        </div>


      </div>
    </Container >

    );
}