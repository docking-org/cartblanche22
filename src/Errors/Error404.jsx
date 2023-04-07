import React from "react";
import { useState } from "react";
import { Card, Container } from "react-bootstrap";
import { Link, useParams } from "react-router-dom";

export default function Error404(props){
    const [substance] = useState(useParams().id);

    React.useEffect(() => {
        document.title = props.title || "";
      }, [props.title]);

    return (
        <Container className="mt-2">
            <Card>
                <Card.Header>
                    <h1>404 - Page not found</h1>
                </Card.Header>
                <Card.Body>
                    <p>
                        The page you are looking for does not exist.
                    </p>
                    <p>
                        If you believe this is an error, please contact jjiteam@googlegroups.com.
                        
                    </p>
                   
                </Card.Body>
            </Card>
        </Container>

    );
}