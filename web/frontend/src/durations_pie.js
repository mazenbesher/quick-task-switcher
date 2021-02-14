import Plotly from 'plotly.js/dist/plotly'
import {seconds_to_str} from "./utils";

export const create_desktops_durations_pie = (data, div) => {
    var data = [{
        values: data.map(info => info.duration_seconds),
        labels: data.map(info => info.name),
        type: 'pie',
        text: data.map(info => `${info.name}<br>${seconds_to_str(info.duration_seconds)}`),
        hoverinfo: 'text',
    }];

    var layout = {
        height: 400,
        width: 500
    };

    Plotly.newPlot(div, data, layout);
}
