import config from '../config.json'

const backend_addr = `http://127.0.0.1:${config.backend_port}`

// get data
const response = await fetch(`${backend_addr}/desktops_info`)
const data = await response.json()

// section with header
const desktops_info_details = document.createElement('details')
desktops_info_details.open = true
desktops_info_details.innerHTML += `<summary class="text-xl mb-3 font-semibold">Current Desktops Info</summary>`

// table
const info_table = document.createElement('table')
desktops_info_details.appendChild(info_table)
info_table.classList.add('table-auto')

// table header
info_table.innerHTML += `
<tr>
    <th>Number</th>
    <th>Name</th>
    <th>Duration</th>
</tr>
`

// add info row for each desktop
data.forEach(desktop_info => {
    const duration_str = new Date(desktop_info.duration_seconds * 1000).toISOString().substr(11, 8)

    info_table.innerHTML += `
    <tr>
        <td>${desktop_info.num}</td>
        <td>${desktop_info.name}</td>
        <td>${duration_str}</td>
    </tr>
    `
})

export default desktops_info_details
