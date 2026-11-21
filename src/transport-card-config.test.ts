import { describe, expect, it } from "vitest";
import {
    resolveConfig,
    type TransportCardConfig,
} from "./transport-card-config.ts";

const minimal: TransportCardConfig = {
    type: "custom:transport-card",
    entity: "sensor.mock_station",
};

const defaults = {
    entity: "sensor.mock_station",
    lines: [],
    max_departures: undefined,
    show_traffic_infos: true,
};

describe("resolveConfig", () => {
    it("resolves missing options to their defaults", () => {
        expect(resolveConfig(minimal)).toEqual(defaults);
    });

    it("resolves options without a value to their defaults", () => {
        const config: TransportCardConfig = {
            ...minimal,
            lines: null,
            max_departures: null,
            show_traffic_infos: null,
        };
        expect(resolveConfig(config)).toEqual(defaults);
    });

    it("keeps options that are set", () => {
        const config: TransportCardConfig = {
            ...minimal,
            lines: ["U4", "13A"],
            max_departures: 3,
            show_traffic_infos: false,
        };
        expect(resolveConfig(config)).toEqual({
            entity: "sensor.mock_station",
            lines: ["U4", "13A"],
            max_departures: 3,
            show_traffic_infos: false,
        });
    });

    it("shows all lines when lines is not a list", () => {
        const config = {
            ...minimal,
            lines: "U4",
        } as unknown as TransportCardConfig;
        expect(resolveConfig(config).lines).toEqual([]);
    });
});
