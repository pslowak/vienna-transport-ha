import { nothing } from "lit";
import { describe, expect, it } from "vitest";
import type { TrafficInfo } from "./api.ts";
import { renderTrafficInfos } from "./traffic-info.ts";

const infos: TrafficInfo[] = [
    { category: "elevator", description: "Elevator out of service" },
];

describe("renderTrafficInfos", () => {
    it("renders infos by default", () => {
        expect(renderTrafficInfos(infos, "en")).not.toBe(nothing);
    });

    it("renders infos when enabled", () => {
        expect(renderTrafficInfos(infos, "en", true)).not.toBe(nothing);
    });

    it("renders nothing when disabled", () => {
        expect(renderTrafficInfos(infos, "en", false)).toBe(nothing);
    });

    it("renders nothing without infos", () => {
        expect(renderTrafficInfos([], "en")).toBe(nothing);
    });
});
