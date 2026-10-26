import { describe, expect, it } from "vitest";
import type { Departure, Line, Stop, Vehicle } from "./api.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import {
    departureTiming,
    formatDelay,
    formatWait,
    selectLines,
    visibleDepartures,
} from "./departures.ts";

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

function localDate(hour: number, minute: number, second = 0): Date {
    return new Date(at(hour, minute, second));
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
    const now = localDate(7, 55);

    it("returns all departures without a maximum", () => {
        expect(visibleDepartures(l, undefined, now)).toEqual(departures);
    });

    it("limits to the maximum", () => {
        expect(visibleDepartures(l, 2, now)).toEqual(departures.slice(0, 2));
    });

    it("returns all departures when the maximum exceeds the list", () => {
        expect(visibleDepartures(l, 10, now)).toEqual(departures);
    });

    it("drops departures left more than 30 seconds ago", () => {
        expect(visibleDepartures(l, undefined, localDate(8, 0, 31))).toEqual([
            departures[1],
            departures[2],
        ]);
    });

    it("keeps departures left less than 30 seconds ago", () => {
        expect(visibleDepartures(l, undefined, localDate(8, 0, 29))).toEqual(
            departures,
        );
    });
});

describe("departureTiming", () => {
    it("reports no delay for an on-time departure", () => {
        const timing = departureTiming(
            departure(at(8, 0), at(8, 0)),
            localDate(7, 55),
        );

        expect(timing.delay).toBe(0);
        expect(timing.wait).toBe(5);
        expect(timing.actual.getTime()).toBe(localDate(8, 0).getTime());
    });

    it("reports a positive delay when the departure is late", () => {
        expect(
            departureTiming(departure(at(8, 0), at(8, 3)), localDate(7, 55))
                .delay,
        ).toBe(3);
    });

    it("reports a negative delay when the departure is early", () => {
        expect(
            departureTiming(departure(at(8, 0), at(7, 58)), localDate(7, 55))
                .delay,
        ).toBe(-2);
    });

    it("reports a negative wait once the departure has left", () => {
        expect(
            departureTiming(departure(at(8, 0), at(8, 3)), localDate(8, 5))
                .wait,
        ).toBe(-2);
    });

    it("rounds the wait to the nearest minute", () => {
        expect(
            departureTiming(departure(at(8, 0), at(8, 0)), localDate(7, 59, 30))
                .wait,
        ).toBe(0);
    });
});

describe("formatWait", () => {
    const actual = localDate(8, 3);

    it("shows the now label for a departure that is due", () => {
        expect(formatWait(0, actual, "en")).toBe("now");
        expect(formatWait(0, actual, "de")).toBe("Jetzt");
    });

    it("shows the now label for a departure that has left", () => {
        expect(formatWait(-2, actual, "en")).toBe("now");
    });

    it("shows minutes below the clock time threshold", () => {
        expect(formatWait(14, actual, "en")).toBe("14 min");
        expect(formatWait(14, actual, "de")).toBe("14 Min");
    });

    it("shows the clock time from the threshold on", () => {
        expect(formatWait(15, actual, "en")).toBe("08:03");
    });
});

describe("formatDelay", () => {
    it("hides no delay", () => {
        expect(formatDelay(0)).toBeUndefined();
    });

    it("signs a delay", () => {
        expect(formatDelay(3)).toBe("+3");
    });

    it("signs an early departure", () => {
        expect(formatDelay(-2)).toBe("-2");
    });
});
