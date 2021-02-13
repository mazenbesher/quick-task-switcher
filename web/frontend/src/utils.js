export const seconds_to_str = seconds =>
    new Date(seconds * 1000).toISOString().substr(11, 8)