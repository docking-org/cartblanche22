import React from "react";
import { useState } from "react";
import { Card, Container, Form } from "react-bootstrap";
import { Link, useParams } from "react-router-dom";

export default function NoResults(props) {
    return (
        <Container className="mt-2">
            <Card>
                <Card.Header>
                    <h1>No Results Found</h1>
                </Card.Header>
                <Card.Body>
                    <p>
                        Your search did not return any results.
                    </p>
                    <p>
                        You searched for:

                        <Form.Control as='textarea' rows={6}
                            editable="false"
                            disabled={true}
                            value={props.submission.join('\n')}
                        />

                    </p>
                    <p>
                        If you believe this is an error, please contact jjiteam@googlegroups.com.
                    </p>

                </Card.Body>
            </Card>
        </Container>

    );
}