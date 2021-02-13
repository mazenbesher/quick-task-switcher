import config from '../config.json'
import './style.css';
import desktops_info_details from './desktops_info'

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

document.body.appendChild(desktops_info_details)