import type { Line, Vehicle, VehicleInfo } from "./api.ts";

const UNKNOWN: VehicleInfo = { background: "#888", color: "#fff" };

const BUS = "BUS";
const NIGHT_BUS = "NIGHT_BUS";
const TRAM = "TRAM";
const BADEN_TRAM = "BADEN_TRAM";

const VEHICLE_REGISTRY: ReadonlyMap<string, VehicleInfo> = new Map([
    ["U1", { background: "#E3000F", color: "#fff" }],
    ["U2", { background: "#A862A4", color: "#fff" }],
    ["U3", { background: "#EF7C00", color: "#fff" }],
    ["U4", { background: "#00963F", color: "#fff" }],
    ["U5", { background: "#008F95", color: "#fff" }],
    ["U6", { background: "#9D6830", color: "#fff" }],
    [BUS, { background: "#0a295d", color: "#fff" }],
    [NIGHT_BUS, { background: "#0a295d", color: "#fef208" }],
    [TRAM, { background: "#c00808", color: "#fff" }],
    [BADEN_TRAM, { background: "#015792", color: "#fff" }],
]);

function vehicleKey(type: string, name: string): string {
    switch (type) {
        case "ptBusCity":
            return BUS;
        case "ptBusNight":
            return NIGHT_BUS;
        case "ptTram":
            return TRAM;
        case "ptTramWLB":
            return BADEN_TRAM;
        case "ptMetro":
            return name;
        default:
            return "";
    }
}

export function getVehicleInfo(vehicle: Vehicle, line: Line): VehicleInfo {
    return VEHICLE_REGISTRY.get(vehicleKey(vehicle.type, line.name)) ?? UNKNOWN;
}
