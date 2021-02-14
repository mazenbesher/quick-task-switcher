import {seconds_to_str} from './utils'
import {create_desktops_durations_pie} from './durations_pie'

export const create_desktop_info_sec = (data) => {
    // data == desktop_infos

    const total_duration_seconds = data.map(info => info.duration_seconds).reduce((a, b) => a + b, 0)

    // section with header
    const desktops_info_details = document.createElement('details')
    desktops_info_details.open = true
    desktops_info_details.innerHTML += `<summary class="text-xl mb-3 font-semibold">Current Desktops Info</summary>`
    desktops_info_details.innerHTML += `<p class="mb-5">Total Duration: ${seconds_to_str(total_duration_seconds)}</p>`

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
        <th>Percentage</th>
    </tr>
    `

    // add info row for each desktop
    data.forEach(desktop_info => {
        const percentage = Math.round(((desktop_info.duration_seconds / total_duration_seconds) + Number.EPSILON) * 100)

        info_table.innerHTML += `
            <tr>
                <td>${desktop_info.num}</td>
                <td>${desktop_info.name}</td>
                <td>${seconds_to_str(desktop_info.duration_seconds)}</td>
                <td>${percentage}%</td>
            </tr>
            `
    })

    // desktops durations pie chart
    const duration_pie_div = document.createElement('div')
    create_desktops_durations_pie(data, duration_pie_div)
    desktops_info_details.appendChild(duration_pie_div)

    return desktops_info_details
}


