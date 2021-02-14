import './style.css';
import config from '../config.json'
import {create_desktop_info_sec} from './desktops_info'


// add uptime
{
    // get up time
    const backend_addr = `http://127.0.0.1:${config.backend_port}`
    const response = await fetch(`${backend_addr}/info/uptime`)
    const uptime_seconds = parseFloat(await response.text())

    // multiplied by 1000 so that the argument is in milliseconds, not seconds.
    const uptime = new Date(uptime_seconds * 1000);

    // format and add
    document.body.innerHTML += `
        <p class="mb-5">Start time: ${uptime.toLocaleString()}</p>
    `
}

// get desktops info data
const backend_addr = `http://127.0.0.1:${config.backend_port}`
const response = await fetch(`${backend_addr}/info/desktops`)
const desktops_info = await response.json()
const durations_info_sec = create_desktop_info_sec(desktops_info)

// desktops info section
document.body.appendChild(durations_info_sec)
