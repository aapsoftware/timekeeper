import config from 'config';
import { authHeader } from '../_helpers';


export const timezoneService = {
    getAll,
    getAllByUsername,
    create,
    update,
    delete: _delete
};

function getAll() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/timezone`, requestOptions).then(handleResponse);
}

function getAllByUsername() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/timezone/${username}`, requestOptions).then(handleResponse);
}

function create(timezone_details) {
    const requestOptions = {
        method: 'POST',
        headers: {  ...authHeader(), 'Content-Type': 'application/json', "Access-Control-Allow-Origin": "*"},
        body: JSON.stringify(timezone_details)
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/timezone/${username}`, requestOptions).then(handleResponse);
}

function update(timezone_name, timezone_details) {
    const requestOptions = {
        method: 'PUT',
        headers: { ...authHeader(), 'Content-Type': 'application/json'},
        body: JSON.stringify(timezone_details)
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/timezone/${username}/${timezone_name}`, requestOptions).then(handleResponse);
}

// prefixed function name with underscore because delete is a reserved word in javascript
function _delete(timezone_name) {
    const requestOptions = {
        method: 'DELETE',
        headers: authHeader()
    };
    let username = JSON.parse(localStorage.getItem('user'))['username'];
    return fetch(`${config.apiUrl}/timezone/${username}/${timezone_name}`, requestOptions).then(handleResponse);
}

function handleResponse(response) {
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        if (!response.ok) {
            if (response.status === 401) {
                // auto logout if 401 response returned from api
                logout();
                location.reload(true);
            }

            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }

        return data;
    });
}