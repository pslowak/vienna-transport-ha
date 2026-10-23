import { describe, expect, it } from "vitest";
import type { Departure, Line, Stop, Vehicle } from "./api.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import { selectLines, visibleDepartures } from "./departures.ts";

const vehicle: Vehicle = {
    name: "U4",
    type: "ptMetro",
    towards: "Hütteldorf",
    cooling: false,
};

/** Timestamp within a fixed local day, returned as UTC ISO to stay timezone safe. */
function at(hour: number, minute: number, second = 0): string {
    return new Date(2026, 0, 1, hour, minute, second).toISOString();
}

function departure(planned: string, real: string): Departure {
    return { time_planned: planned, time_real: real, vehicle };
}

function line(name: string, departures: Departure[] = []): Line {
    return { name, departures, traffic_infos: [] };
}

function stop(lines: Line[]): Stop {
    return { props: { id: 1, name: "Volkertplatz" }, lines, traffic_infos: [] };
}

function config(lines?: string[], maxDepartures?: number): TransportCardConfig {
    return {
        type: "custom:transport-card",
        entity: "sensor.mock_station",
        lines,
        max_departures: maxDepartures,
    };
}

describe("selectLines", () => {
    const all = stop([line("U4"), line("U6"), line("71")]);

    it("returns all lines when no lines are configured", () => {
        expect(selectLines(all, config())).toEqual(all.lines);
    });

    it("returns all lines when the configured list is empty", () => {
        expect(selectLines(all, config([]))).toEqual(all.lines);
    });

    it("keeps only configured lines in stop order", () => {
        expect(
            selectLines(all, config(["71", "U4"])).map((l) => l.name),
        ).toEqual(["U4", "71"]);
    });

    it("returns nothing when no line matches", () => {
        expect(selectLines(all, config(["U9"]))).toEqual([]);
    });

    it("ignores a non-array value instead of crashing", () => {
        const malformed = {
            ...config(),
            lines: "U4",
        } as unknown as TransportCardConfig;
        expect(selectLines(all, malformed)).toEqual(all.lines);
    });
});

describe("visibleDepartures", () => {
    const departures = [
        departure(at(8, 0), at(8, 0)),
        departure(at(8, 10), at(8, 10)),
        departure(at(8, 20), at(8, 20)),
    ];
    const l = line("U4", departures);

    it("returns all departures without a maximum", () => {
        expect(visibleDepartures(l)).toEqual(departures);
    });

    it("limits to the maximum", () => {
        expect(visibleDepartures(l, 2)).toEqual(departures.slice(0, 2));
    });

    it("returns all departures when the maximum exceeds the list", () => {
        expect(visibleDepartures(l, 10)).toEqual(departures);
    });
});
