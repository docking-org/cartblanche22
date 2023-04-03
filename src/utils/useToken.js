import { useState } from 'react';

export default function useToken() {
    function getToken() {
        const userToken = localStorage.getItem('token');
        return userToken && userToken
    }

    function getUserName() {
        const userName = localStorage.getItem('username');
        return userName && userName
    }
    

    const [username, setUsername] = useState(getUserName());
    const [token, setToken] = useState(getToken());

    function saveToken(userToken, userName = username) {
        localStorage.setItem('token', userToken);
        localStorage.setItem('username', userName);
        setToken(userToken);
        setUsername(userName);
    };

    function removeToken() {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        setToken(null);
        setUsername(null);
    }

    return {
        setToken: saveToken,
        token,
        removeToken,
        username,
    }

}
