import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Card, Container, Table, Form } from "react-bootstrap";
import axios from "axios";
import useToken from "../utils/useToken";
import { useNavigate } from "react-router-dom";

export default function ZincIdSearch(props) {
  const navigate = useNavigate();
  const [input, setInput] = React.useState("");
  const { token, removeToken, setToken, username } = useToken();

  useEffect(() => {}, []);

  useEffect(() => {
    document.title = props.title || "";
  }, [props.title]);

  function getMolecules() {
    var bodyFormData = new FormData();
    bodyFormData.append("zinc_ids", input);
    if (document.getElementById("smiles_only").checked) {
      bodyFormData.append("smiles_only", true);
    }

    var file = document.getElementById("zincfile").files[0];
    if (file) {
      bodyFormData.append("zinc_ids", file);
    }
    return axios({
      method: "post",
      url: "/substances.json",
      data: bodyFormData,
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: token ? `Bearer ${token}` : "",
      },
    }).then((response) => {
      console.log(response.data);

      navigate("/results?task=" + response.data.task);
    });
  }

  function loadTestData() {
    setInput(
      "ZINCar0000000p57\nZINCde000000YNim\nZINCms000002NiP3\nZINCqq000005JJSl\nZINCjB000003FXzy\n"
    );
  }

  return (
    <Container className="mt-2 mb-2">
      <Card>
        <Card.Header>
          <b>Search by ZINC identifier, one per line</b>
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
                id="zinc_ids"
                class="form-control"
                rows="6"
                cols="20"
                placeholder="ZINC IDs"
                onLoad={(e) => setInput(e.target.value)}
                name="myTextarea"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              ></textarea>
            </div>
            <div class="form-group mt-1 mb-2">
              <label for="zincfile">OR Upload a File (.txt only):</label>
              <input
                type="file"
                id="zincfile"
                name="zincfile"
                class="form-control"
                accept=".txt"
              />

              <Form.Check
                type={"checkbox"}
                id={`smiles_only`}
                label={`Search for SMILES only`}
              />
            </div>

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
          <b>CURL commands for searching multiple ZincIDs</b>
        </Card.Header>
        <Card.Body>
          <p>
            Example:{" "}
            <code>
              curl -X GET https://cartblanche22.docking.org/substances.txt -F
              zinc_ids=@test.txt -F output_fields='smiles,zinc_id'
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
              https://cartblanche22.docking.org/search/result/<b>task_id</b>
            </code>
            <br></br>
            <br></br>
          </p>
          <Table bordered striped hover>
            <thead>
              <tr>
                <th class="col-md-4">Description</th>
                <th class="col-md-5">Attributes</th>
                <th class="col-md-3">Possible fields</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>To specify return format</td>
                <td>
                  <code>
                    curl -X GET https://cartblanche22.docking.org/substances
                    <i>.txt</i>
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
                    -F zinc_ids=<i>@test.txt</i>
                  </code>
                </td>
                <td>.txt file with list of zinc identifers</td>
              </tr>
              <tr>
                <td>
                  To specify output fields
                  <br />
                  <small>
                    If no fields are defined, search will return all possible
                    fields
                  </small>
                </td>
                <td>
                  <code>
                    -F output_fields=<i>'smiles,zinc_id'</i>
                  </code>
                </td>
                <td>
                  <ul>
                    <li>catalogs</li>
                    <li>smiles</li>
                    <li>sub_id</li>
                    <li>tranche</li>
                    <li>tranche_details</li>
                    <li>zinc_id</li>
                  </ul>
                </td>
              </tr>
              <tr>
                <td>
                  Search for SMILES only (search returns zinc_id, smiles){" "}
                </td>
                <td>
                  <code>-F smiles_only=true</code>
                </td>
              </tr>
              <tr>
                <td>
                  Start synchronous search (not recommended for larger searches)
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
