import config from 'config';
import { authHeader } from '../_helpers';
import { router } from '../_helpers';

export const userService = {
    login,
    logout,
    register,
    getAll,
    getUserDetails,
    updateUserDetails,
    delete: _delete
};

function login(username, password) {
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    };

    return fetch(`${config.apiUrl}/auth/login`, requestOptions)
        .then(
            resp => handleResponse(resp, {no_logout:true}),
            error => {}
        )
        .then(resp => {
            // login successful if there's a jwt token in the response
            if (resp.access_token) {
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                var user_data = {
                    "access_token": resp.access_token,
                    "username": username
                }
                localStorage.setItem('user', JSON.stringify(user_data));
            }

            return resp;
        });
}

export function logout(options) {
    if (options && options.has_token) {
        const requestOptions = {
            method: 'POST',
            headers: authHeader()
        };
        fetch(`${config.apiUrl}/auth/logout`, requestOptions);
    }
    localStorage.removeItem('user');
    router.push('/');
}

function register(user) {
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', "Access-Control-Allow-Origin": "*"},
        body: JSON.stringify(user)
    };

    return fetch(`${config.apiUrl}/user`, requestOptions).then(handleResponse);
}

function getAll() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/user`, requestOptions).then(handleResponse);
}

function getUserDetails() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/user/${username}`, requestOptions).then(handleResponse);
}

function updateUserDetails(user) {
    const requestOptions = {
        method: 'PUT',
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify(user)
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/user/${username}`, requestOptions).then(handleResponse);
}

// prefixed function name with underscore because delete is a reserved word in javascript
function _delete(username) {
    const requestOptions = {
        method: 'DELETE',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/user/${username}`, requestOptions).then(handleResponse);
}

function handleResponse(response, options) {
    return response.text().then(text => {

        const data = text && JSON.parse(text);
        if (!response.ok) {
            if (!options.no_logout){
                if (response.status === 401) {
                    // auto logout if 401 response returned from api
                    logout();
                    location.reload(true);
                }
            }
            let msg = (data.error === undefined)? data.message : data.error.message;
            const error = (data && msg) || response.statusText;

            return Promise.reject(error);
        }

        return data;
    });
}