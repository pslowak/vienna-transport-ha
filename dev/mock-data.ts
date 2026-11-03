import type { Departure, Stop, TrafficInfo } from "../src/api.ts";

const MINUTE_MS = 60_000;

const ELEVATOR_INFO: TrafficInfo = {
    description:
        "Fahrtrichtung U4 Heiligenstadt. - Ausgang Ramperstorffergasse - " +
        "Aufzugsanlage ist wegen Bauarbeiten bis 2030 außer Betrieb!",
    category: "elevator",
};

function departure(
    minutesAhead: number,
    delayMinutes: number,
    cooling: boolean,
): Departure {
    const planned = new Date(Date.now() + minutesAhead * MINUTE_MS);
    const real = new Date(planned.getTime() + delayMinutes * MINUTE_MS);

    return {
        time_planned: planned.toISOString(),
        time_real: real.toISOString(),
        vehicle: {
            name: "U4",
            type: "ptMetro",
            towards: "Hütteldorf",
            cooling,
        },
    };
}

/**
 * Sensor attributes for stop 4420 (Pilgramgasse), shaped like the
 * integration's `stop.to_dict()`. Departures are relative to now so the
 * card never runs out of upcoming departures.
 */
export function createMockStop(): Stop {
    return {
        props: { id: 4420, name: "Pilgramgasse" },
        traffic_infos: [],
        lines: [
            {
                name: "U4",
                traffic_infos: [ELEVATOR_INFO],
                departures: [
                    departure(0, 0, true),
                    departure(3, 1, false),
                    departure(15, 0, true),
                    departure(25, 0, false),
                ],
            },
        ],
    };
}
