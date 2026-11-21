import { describe, expect, it } from "vitest";
import type { Departure, Line } from "./api.ts";
import { visibleDepartures } from "./departures.ts";
import type { LovelaceCardConfig } from "./ha.ts";
import { t } from "./i18n.ts";
import {
    assertConfig,
    resolveConfig,
    type TransportCardConfig,
} from "./transport-card-config.ts";

const minimal: TransportCardConfig = {
    type: "custom:transport-card",
    entity: "sensor.mock_station",
};

function withOption(option: string, value: unknown): LovelaceCardConfig {
    return { ...minimal, [option]: value };
}

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

describe("assertConfig", () => {
    it.each([
        ["no options", minimal],
        [
            "all options",
            {
                ...minimal,
                lines: ["U4", "13A"],
                max_departures: 3,
                show_traffic_infos: false,
            },
        ],
        ["numeric line names", withOption("lines", [71, "U4"])],
        ["null lines", withOption("lines", null)],
        ["null max_departures", withOption("max_departures", null)],
        ["null show_traffic_infos", withOption("show_traffic_infos", null)],
        ["no entity", { type: "custom:transport-card", entity: "" }],
    ])("accepts %s", (_, config) => {
        expect(() => assertConfig(config)).not.toThrow();
    });

    it.each([
        ["lines", "U4", "card.config.invalid_lines"],
        ["lines", [true], "card.config.invalid_lines"],
        ["lines", [{ name: "U4" }], "card.config.invalid_lines"],
        ["lines", [NaN], "card.config.invalid_lines"],
        ["lines", [Infinity], "card.config.invalid_lines"],
        ["max_departures", 0, "card.config.invalid_max_departures"],
        ["max_departures", -1, "card.config.invalid_max_departures"],
        ["max_departures", 2.5, "card.config.invalid_max_departures"],
        ["max_departures", NaN, "card.config.invalid_max_departures"],
        ["max_departures", "3", "card.config.invalid_max_departures"],
        ["show_traffic_infos", "no", "card.config.invalid_show_traffic_infos"],
        ["show_traffic_infos", 1, "card.config.invalid_show_traffic_infos"],
    ])("rejects %s set to %o", (option, value, key) => {
        expect(() => assertConfig(withOption(option, value))).toThrow(t(key));
    });

    it("names the invalid option in the user's language", () => {
        expect(() =>
            assertConfig(withOption("max_departures", 0), "de"),
        ).toThrow(t("card.config.invalid_max_departures", "de"));
    });
});

describe("resolveConfig", () => {
    it("resolves missing options to their defaults", () => {
        expect(resolveConfig(minimal)).toEqual({
            entity: "sensor.mock_station",
            lines: [],
            max_departures: undefined,
            show_traffic_infos: true,
        });
    });

    it("resolves null options to their defaults", () => {
        const config: TransportCardConfig = {
            ...minimal,
            lines: null,
            max_departures: null,
            show_traffic_infos: null,
        };
        expect(resolveConfig(config)).toEqual(resolveConfig(minimal));
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

    it("reads numeric line names as names", () => {
        const config: TransportCardConfig = { ...minimal, lines: [71, "U4"] };
        expect(resolveConfig(config).lines).toEqual(["71", "U4"]);
    });

    it("keeps all departures visible for a null max_departures", () => {
        const config: TransportCardConfig = {
            ...minimal,
            max_departures: null,
        };
        const line: Line = {
            name: "U4",
            departures: [departure(), departure()],
            traffic_infos: [],
        };
        const now = new Date(2026, 0, 1, 8, 0);
        expect(
            visibleDepartures(line, resolveConfig(config).max_departures, now),
        ).toHaveLength(2);
    });
});
