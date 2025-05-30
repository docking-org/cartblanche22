import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Card, Container, Table } from "react-bootstrap";
import axios from "axios";
import useToken from "../utils/useToken";

export default function SmilesSearch(props) {
  //use text box value by default
  const [input, setInput] = React.useState("");
  const { token } = useToken();
  const [zinc20, setZinc20] = React.useState(false);
  const [zinc22, setZinc22] = React.useState(true);

  useEffect(() => {
    document.title = props.title || "";
  }, [props.title]);

  useEffect(() => {}, []);

  function getMolecules() {
    var bodyFormData = new FormData();
    bodyFormData.append("smiles", input);
    bodyFormData.append("dist", document.getElementById("distformat").value);
    bodyFormData.append("adist", document.getElementById("adistformat").value);
    let databases = [];
    if (zinc20) {
      databases.push("zinc20");
    }
    if (zinc22) {
      databases.push("zinc22");
    }
    bodyFormData.append("database", databases.join(","));

    var file = document.getElementById("smilesfile").files[0];
    if (file) {
      bodyFormData.append("smiles", file);
    }
    axios({
      method: "post",
      url: "/smiles.json",
      data: bodyFormData,
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: token ? `Bearer ${token}` : "",
      },
    }).then((response) => {
      window.location.href = "/results?task=" + response.data.task;
    });
  }

  function loadTestData() {
    setInput("C1CCC(-C2NNCNN2)CC1\nC1CCC(C2CNNC2)C1\nC1=CC=CC=C1C2=CC=CC=C2\n");
  }

  return (
    <Container className="mt-2 mb-2">
      <Card>
        <Card.Header>
          <b>Search by Smiles identifier, one per line</b>
        </Card.Header>

        <Card.Body>
          <form
            id="data"
            method="post"
            enctype="multipart/form-data"
            onSubmit={(e) => e.preventDefault()}
          >
            <div class="form-group">
              <textarea
                id="smilesTextarea"
                class="form-control"
                rows="6"
                cols="20"
                placeholder="Smiles"
                name="smilesTextarea"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
            </div>
            <div class="form-group">
              <label for="smilesfile">OR Upload a file (.txt only):</label>
              <input
                type="file"
                id="smilesfile"
                name="smilesfile"
                class="form-control"
                accept=".txt"
              />
            </div>
            <label for="distformat">dist:</label>
            <select name="dist" class="btn btn-info m-1" id="distformat">
              <option value="0" id="dist-0" selected>
                0
              </option>
              <option value="1" id="dist-1">
                1
              </option>
              <option value="2" id="dist-2">
                2
              </option>
              <option value="3" id="dist-3">
                3
              </option>
            </select>
            &nbsp;
            <label for="adistformat">anon dist:</label>
            <select name="adist" class="btn btn-info m-1" id="adistformat">
              <option value="0" id="adist-0" selected>
                0
              </option>
              <option value="1" id="adist-1">
                1
              </option>
              <option value="2" id="adist-2">
                2
              </option>
              <option value="3" id="adist-3">
                3
              </option>
            </select>
            <br></br>
            Search Database
            <br></br>
            <input
              type={"checkbox"}
              id={"zinc22"}
              name={"zinc22"}
              value={zinc22}
              defaultChecked={zinc22}
              onClick={() => setZinc22(!zinc22)}
            ></input>
            &nbsp;<label for={"zinc22"}>ZINC22</label>
            <br></br>
            <input
              type={"checkbox"}
              id={"zinc20"}
              name={"zinc20"}
              value={zinc20}
              defaultChecked={zinc20}
              onClick={() => setZinc20(!zinc20)}
            />
            &nbsp;<label for={"zinc20"}>ZINC20 For Sale</label>
            <br></br>
            <br />
            <button
              id="searchZincBtn2"
              type="submit"
              onClick={getMolecules}
              class="btn btn-info m-1"
            >
              Search
            </button>
            <button
              id="testData"
              onClick={loadTestData}
              class="btn btn-secondary m-1"
            >
              Load Test Data
            </button>
          </form>
        </Card.Body>
      </Card>

      <Card className="mt-2">
        <Card.Header>
          <b>CURL commands for searching using SMILES</b>
        </Card.Header>
        <Card.Body>
          <p>
            Example:{" "}
            <code>
              curl -X GET https://cartblanche22.docking.org/smiles.txt -F
              smiles=@smiles.txt -F dist=4 -F adist=4
            </code>
          </p>

          <p>
            - Results can be formatted in the desired file format.
            <br />
            - If output_fields are not specified, all available molecule data is
            returned.
            <br />- The zinc_id and smiles output fields will be returned by
            default unless otherwise specified.
            <br></br>- The search is asynchronous by default. The submission
            will return a task ID that can be used to check the status of the
            search.
            <br></br>
            <br></br>Asynchronous results can be retrieved using this url
            format:
            <br></br>
            <code>
              curl -X GET https://cartblanche.docking.org/search/saveResult/
              <b>task_id</b>
              .txt
            </code>
            <br></br>
            <br></br>
          </p>
          <Table bordered striped hover>
            <thead>
              <tr>
                <th class="col-md-4">Description</th>
                <th class="col-md-5">Attributes</th>
                <th class="col-md-3">Parameters</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>To specify return format</td>
                <td>
                  <code>
                    curl -X GET https://cartblanche22.docking.org/smiles
                    <i>
                      <b>.txt</b>
                    </i>
                  </code>
                </td>
                <td>
                  <ul>
                    <li>.txt</li>
                    <li>.csv</li>
                    <li>.json</li>
                  </ul>
                </td>
              </tr>
              <tr>
                <td>To add search value</td>
                <td>
                  {" "}
                  <code>
                    -F smiles=<i>@test.txt</i>
                  </code>
                </td>
                <td>.txt file with list of smiles</td>
              </tr>
              <tr>
                <td>
                  To specify dist, adist
                  <br />
                  <small>
                    If either dist or adist are not defined, values will default
                    to 0.
                  </small>
                </td>
                <td>
                  <code>
                    -F dist=<i>4</i>
                  </code>
                  <code>
                    -F adist=<i>4</i>
                  </code>
                </td>
                <td>Number</td>
              </tr>
              <tr>
                <td>
                  Start synchronous search. Retrieves results immediately (not
                  recommended for larger searches).
                </td>
                <td>
                  <code>-F synchronous=true</code>
                </td>
              </tr>
            </tbody>
          </Table>
          <p>
            If you want to learn more about search, please go to{" "}
            <a
              href="http://wiki.docking.org/index.php/Zinc22:Searching"
              target="_blank"
            >
              {" "}
              Zinc22 documentation on wiki page
            </a>
          </p>
        </Card.Body>
      </Card>
    </Container>
  );
}
