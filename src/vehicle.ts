import type { Line, Vehicle, VehicleInfo } from "./types";

enum VehicleType {
    U1 = "U1",
    U2 = "U2",
    U3 = "U3",
    U4 = "U4",
    U5 = "U5",
    U6 = "U6",
    BUS = "BUS",
    NIGHT_BUS = "NIGHT_BUS",
    TRAM = "TRAM",
    BADEN_TRAM = "BADEN_TRAM",
    UNKNOWN = "UNKNOWN",
}

const VEHICLE_REGISTRY: Record<VehicleType, VehicleInfo> = {
    [VehicleType.U1]: { background: "#E3000F", color: "#fff"},
    [VehicleType.U2]: { background: "#A862A4", color: "#fff"},
    [VehicleType.U3]: { background: "#EF7C00", color: "#fff"},
    [VehicleType.U4]: { background: "#00963F", color: "#fff"},
    [VehicleType.U5]: { background: "#008F95", color: "#fff"},
    [VehicleType.U6]: { background: "#9D6830", color: "#fff"},
    [VehicleType.BUS]: { background: "#0a295d", color: "#fff"},
    [VehicleType.NIGHT_BUS]: { background: "#0a295d", color: "#fef208"},
    [VehicleType.TRAM]: { background: "#c00808", color: "#fff"},
    [VehicleType.BADEN_TRAM]: { background: "#015792", color: "#fff"},
    [VehicleType.UNKNOWN]: { background: "#888", color: "#fff"},
};

function vehicleTypeFromString(type: string, name: string): VehicleType {
    switch (type) {
        case "ptBusCity":
            return VehicleType.BUS;
        case "ptBusNight":
            return VehicleType.NIGHT_BUS;
        case "ptTram":
            return VehicleType.TRAM;
        case "ptTramWLB":
            return VehicleType.BADEN_TRAM;
        case "ptMetro":
            return name as VehicleType ?? VehicleType.UNKNOWN;
        default:
            return VehicleType.UNKNOWN;
    }
}

function getVehicleType(line: any): VehicleType {
    for (const dep of line.departures.departure) {
        if (dep.vehicle) {
            return vehicleTypeFromString(dep.vehicle.type, line.name);
        }
    }

    return VehicleType.UNKNOWN;
}


export function getVehicleInfo(vehicle: Vehicle | undefined, line: Line) : VehicleInfo {
    if (!vehicle) {
        // No vehicle info available for this departure
        // try other departures of the same line
        const type = getVehicleType(line);
        return VEHICLE_REGISTRY[type];
    }

    const type: VehicleType = vehicleTypeFromString(vehicle.type, line.name);
    return VEHICLE_REGISTRY[type];
}
