import React from "react";
import { Container, Row, Col, Form, Button } from "react-bootstrap";
import axios from "axios";
import {
    useParams,
    Link,
} from "react-router-dom";
import useToken from "../utils/useToken";

export default function ResetPassword() {
    const [passwordToken] = React.useState(useParams().token);
    const [password, setPassword] = React.useState("");
    const [password2, setPassword2] = React.useState("");
    const { token, removeToken, setToken, username } = useToken();

    const handleSubmit = (e) => {
        e.preventDefault();

        axios({
            method: "post",
            url: "https://cartblanche22.docking.org/reset_password",
            data: {
                token: passwordToken,
                password: password,
            },
            headers: { "Content-Type": "multipart/form-data" },

        }).then((response) => {
            alert(response.data.msg);

            setToken(response.data.access_token, response.data.username);
            window.location.href = "/";
        }).catch((error) => {
            alert(error);

        })
    }

    return (
        <Container className="mt-5 ">
            <Row className="justify-content-md-center">
                < Col xs={6} md={4} className="bg-light border rounded p-3" >
                    <h1>Reset Password</h1>
                    <Form onSubmit={handleSubmit}>
                        <Form.Group controlId="formBasicPassword">
                            <Form.Label>New Password</Form.Label>
                            <Form.Control type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        </Form.Group>
                        <br />
                        <Form.Group controlId="formBasicPassword">
                            <Form.Label>Confirm Password</Form.Label>
                            <Form.Control type="password" placeholder="Confirm Password" value={password2} onChange={(e) => setPassword2(e.target.value)}
                                isInvalid={password !== password2 && password2.length > 0}
                            />

                        </Form.Group>
                        <br />
                        <Button variant="primary" type="submit">
                            Submit
                        </Button>
                    </Form>

                </Col >
            </Row >
        </Container >

    )
}


