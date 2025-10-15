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
    [VehicleType.U1]: { color: "#E3000F"},
    [VehicleType.U2]: { color: "#A862A4"},
    [VehicleType.U3]: { color: "#EF7C00"},
    [VehicleType.U4]: { color: "#00963F"},
    [VehicleType.U5]: { color: "#008F95"},
    [VehicleType.U6]: { color: "#9D6830"},
    [VehicleType.BUS]: { color: "#0a295d"},
    [VehicleType.NIGHT_BUS]: { color: "#0a295d"},
    [VehicleType.TRAM]: { color: "#c00808"},
    [VehicleType.BADEN_TRAM]: { color: "#015792"},
    [VehicleType.UNKNOWN]: { color: "#888"},
};

function vehicleTypeFromString(type: string, name: string): VehicleType {
    switch (type) {
        case "ptBusCity":
            return VehicleType.BUS;
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
