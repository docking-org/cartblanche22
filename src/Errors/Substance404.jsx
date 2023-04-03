import React from "react";
import { useState } from "react";
import { Card, Container } from "react-bootstrap";
import { Link, useParams } from "react-router-dom";

export default function Substance404(){
    const [substance] = useState(useParams().id);
    return (
        <Container className="mt-2">
            <Card>
                <Card.Header>
                    <h1>404 - {substance} not found</h1>
                </Card.Header>
                <Card.Body>
                    <p>
                        The substance you are looking for does not exist in the database.
                    </p>
                    <p>
                        If you believe this is an error, please contact jjiteam@googlegroups.com.
                        
                    </p>
                    <p>
                        For more information and updates, &nbsp;
                            <a
                                href="https://wiki.docking.org/index.php/Legacy_IDs_in_ZINC22"
                            >
                        check the docking wiki.
                        </a>
                    </p>
                </Card.Body>
            </Card>
        </Container>

    );
}