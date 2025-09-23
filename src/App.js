import logo from './logo.svg';
import './App.css';
import React from 'react';
import { Container } from 'react-bootstrap';
function App() {
  return (
    <Container>
      <div class="bg-light border rounded-3 p-3 m-4 mb-0 row">
        <div class="col-md-6">
          <h1 class="display-5 fw-bold">CartBlanche</h1>
          <p>
            Welcome to Cartblanche22, an interface to ZINC-22. ZINC-22 is a free
            database of commercially-available compounds for virtual screening.
            ZINC-22 focuses on make-on-demand ("tangible") compounds from a small
            number of large catalogs: Enamine, WuXi and Mcule. Our sister
            database, <a target='blank' href="https://ZINC20.docking.org">ZINC20</a>
            &nbsp; focuses on smaller catalogs. ZINC-22 currently has about 54.9 billion molecules 
            in 2D and 5.9 billion in 3D.
            <br />
            <br />
            Cartblanche allows you to:
            <ul>
              <li>Search for individual molecules by similarity, substructure or
                patterns. We call this <b>A</b>nalog <b>B</b>y <b>C</b>atalog. </li>
              <li>Select parts of available chemical space by heavy atom count (HAC),
                lipophilicity (calculated logP), net molecular charge, and format
                (mol2, sdf, pdbqt, smiles and db2) in 2D or 3D</li>
              <li>Obtain scripts that help you download or otherwise access the database.</li>
              <li>Look up molecules by supplier code, ZINC ID, SMILES.</li>
              <li>Prioritize compounds for purchase using a shopping cart.</li>
            </ul>
          </p>

        </div>
        <div class="col-md-6">
          <p>
            Cartblanche is provided by the <a target="_blank" href="https://irwinlab.compbio.ucsf.edu">Irwin</a> 
            and <a target="_blank" href="https://bkslab.org">Shoichet</a> Laboratories in the
            Department of Pharmaceutical Chemistry at the University of California, San Francisco (UCSF).
            We thank <a target="_blank" href="https://www.nigms.nih.gov">NIGMS</a> for financial support (GM71896 and
            GM133836).
          </p>
          <p>
            To cite CartBlanche22 (ZINC-22), please reference: Irwin, JCIM, 2022, submitted. <a href="https://doi.org/10.26434/chemrxiv-2022-82czl">https://doi.org/10.26434/chemrxiv-2022-82czl</a>
            <br />
            You may also wish to cite Irwin, Tang, Young, Dandarchuluun, Wong, Khurelbaatar, Moroz, Mayfield, Sayle, <em>J.
              Chem. Inf. Model 2020.</em>
            <a href="https://pubs.acs.org/doi/10.1021/acs.jcim.0c00675"
              target="_blank">https://pubs.acs.org/doi/10.1021/acs.jcim.0c00675</a>.
            <br />
            Or Sterling and Irwin, <em>J. Chem. Inf. Model, 2015</em>
            <em><a href="https://pubs.acs.org/doi/abs/10.1021/acs.jcim.5b00559"
              target="_blank">https://pubs.acs.org/doi/abs/10.1021/acs.jcim.5b00559</a></em>.
          </p>

          <br />
          ZINC - 22 is free to use for everyone, but you may not redistribute
          major portions without the express written permission of John Irwin,
          chemistry4biology@gmail.com
          <br />
          <br />
          <b>Caveat Emptor</b>: ZINC - 22 is made publicly available in the hope that it
          will be useful, but you must use it at your own risk.

        </div>







      </div >

      <br />
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
                  <a href="/similarity/sw">Search for similar molecules using Smallworld</a>
                </li>
                <li>
                  <a href="/patterns/arthor">Search by Substructure or SMARTS using Arthor</a>
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




  )
}

export default App;
