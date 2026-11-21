import { describe, expect, it } from "vitest";
import type { Departure, Line } from "./api.ts";
import { visibleDepartures } from "./departures.ts";
import {
    normalizeConfig,
    type TransportCardConfig,
} from "./transport-card-config.ts";

const minimal: TransportCardConfig = {
    type: "custom:transport-card",
    entity: "sensor.mock_station",
};

function departure(): Departure {
    const time = new Date(2026, 0, 1, 8, 10).toISOString();
    return {
        time_planned: time,
        time_real: time,
        vehicle: {
            name: "U4",
            type: "ptMetro",
            towards: "Hütteldorf",
            cooling: false,
        },
    };
}

describe("normalizeConfig", () => {
    it("resolves missing options to their defaults", () => {
        expect(normalizeConfig(minimal)).toEqual({
            entity: "sensor.mock_station",
            lines: [],
            max_departures: undefined,
            show_traffic_infos: true,
        });
    });

    it("keeps options that are set", () => {
        const config: TransportCardConfig = {
            ...minimal,
            lines: ["U4", "71"],
            max_departures: 3,
            show_traffic_infos: false,
        };
        expect(normalizeConfig(config)).toEqual({
            entity: "sensor.mock_station",
            lines: ["U4", "71"],
            max_departures: 3,
            show_traffic_infos: false,
        });
    });

    it("shows all lines when lines is not a list", () => {
        const config = {
            ...minimal,
            lines: "U4",
        } as unknown as TransportCardConfig;
        expect(normalizeConfig(config).lines).toEqual([]);
    });

    it.each([
        ["null", null],
        ["a string", "3"],
        ["zero", 0],
        ["a negative number", -1],
        ["a fraction", 2.5],
        ["NaN", NaN],
    ])("shows all departures when max_departures is %s", (_, value) => {
        const config = {
            ...minimal,
            max_departures: value,
        } as unknown as TransportCardConfig;
        expect(normalizeConfig(config).max_departures).toBeUndefined();
    });

    it("keeps all departures visible for a null max_departures", () => {
        const config = {
            ...minimal,
            max_departures: null,
        } as unknown as TransportCardConfig;
        const line: Line = {
            name: "U4",
            departures: [departure(), departure()],
            traffic_infos: [],
        };
        const now = new Date(2026, 0, 1, 8, 0);
        expect(
            visibleDepartures(
                line,
                normalizeConfig(config).max_departures,
                now,
            ),
        ).toHaveLength(2);
    });

    it("hides traffic infos only when explicitly disabled", () => {
        const config = {
            ...minimal,
            show_traffic_infos: null,
        } as unknown as TransportCardConfig;
        expect(normalizeConfig(config).show_traffic_infos).toBe(true);
    });
});
