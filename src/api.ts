export interface StopProperties {
    id: number;
    name: string;
}

export interface Stop {
    props: StopProperties;
    lines: Line[];
}

export interface Line {
    name: string;
    departures: Departure[];
}

export interface Departure {
    time_planned: string;
    time_real: string;
    vehicle: Vehicle;
}

export interface Vehicle {
    name: string;
    type: string;
    towards: string;
}

export interface VehicleInfo {
    background: string;
    color: string;
}
