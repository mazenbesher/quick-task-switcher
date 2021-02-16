import Plotly from 'plotly.js/dist/plotly'
import {seconds_to_str} from "./utils";

export const create_desktops_durations_pie = (desktops_info, div) => {
    // filter to only desktop with durations more than one minute
    const filtered_info = desktops_info.filter(info => info.duration_seconds >= 60)


    const to_draw_data = [{
        values: filtered_info.map(info => info.duration_seconds),
        labels: filtered_info.map(info => info.name),
        type: 'pie',
        text: filtered_info.map(info => `${info.name}<br>${seconds_to_str(info.duration_seconds)}`),
        hoverinfo: 'text',
    }];

    const layout = {
        height: 400,
        width: 500
    };

    Plotly.newPlot(div, to_draw_data, layout);
}
