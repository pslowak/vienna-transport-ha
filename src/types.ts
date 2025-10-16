export interface Monitor {
    lines: Line[];
    locationStop: LocationStop;
}

export interface LocationStop {
    properties: LocationStopProperties;
}

export interface LocationStopProperties {
    title: string;
}

export interface Line {
    name: string;
    towards: string;
    departures: Departures;
}

export interface Departures {
    departure: Departure[];
}

export interface Departure {
    departureTime: DepartureTime;
    vehicle?: Vehicle;
}

export interface DepartureTime {
    timePlanned: string;
    timeReal?: string;
}

export interface Vehicle {
    type: string;
}

export interface VehicleInfo {
    background: string;
    color: string;
}