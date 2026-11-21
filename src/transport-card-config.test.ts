import { describe, expect, it } from "vitest";
import {
    normalizeConfig,
    type TransportCardConfig,
} from "./transport-card-config.ts";

const minimal: TransportCardConfig = {
    type: "custom:transport-card",
    entity: "sensor.mock_station",
};

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

    it("hides traffic infos only when explicitly disabled", () => {
        const config = {
            ...minimal,
            show_traffic_infos: null,
        } as unknown as TransportCardConfig;
        expect(normalizeConfig(config).show_traffic_infos).toBe(true);
    });
});
