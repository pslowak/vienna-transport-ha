export interface StopProperties {
    id: number;
    name: string;
}

export type TrafficInfoCategory = "elevator";

export interface TrafficInfo {
    description: string;
    category: TrafficInfoCategory;
}

export interface Stop {
    props: StopProperties;
    lines: Line[];
    traffic_infos: TrafficInfo[];
}

export interface Line {
    name: string;
    departures: Departure[];
    traffic_infos: TrafficInfo[];
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
    cooling: boolean;
}

export interface VehicleInfo {
    background: string;
    color: string;
}
