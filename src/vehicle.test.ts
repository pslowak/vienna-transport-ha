import { describe, expect, it } from "vitest";
import type { Line, Vehicle } from "./api.ts";
import { getVehicleInfo } from "./vehicle.ts";

const UNKNOWN_INFO = { background: "#888", color: "#fff" };

function vehicle(type: string): Vehicle {
    return { name: "", type, towards: "somewhere", cooling: false };
}

function line(name: string): Line {
    return { name, departures: [] };
}

function infoFor(type: string, lineName: string) {
    return getVehicleInfo(vehicle(type), line(lineName));
}

describe("getVehicleInfo", () => {
    describe("metro lines", () => {
        it.each([
            ["U1", "#E3000F", "#fff"],
            ["U2", "#A862A4", "#fff"],
            ["U3", "#EF7C00", "#fff"],
            ["U4", "#00963F", "#fff"],
            ["U5", "#008F95", "#fff"],
            ["U6", "#9D6830", "#fff"],
        ])("resolves %s to its registry colors", (name, background, color) => {
            expect(infoFor("ptMetro", name)).toEqual({ background, color });
        });
    });

    describe("non-metro vehicle types", () => {
        it("resolves ptBusCity regardless of line name", () => {
            expect(infoFor("ptBusCity", "some bus name")).toEqual({
                background: "#0a295d",
                color: "#fff",
            });
        });

        it("resolves ptBusNight regardless of line name", () => {
            expect(infoFor("ptBusNight", "some night bus name")).toEqual({
                background: "#0a295d",
                color: "#fef208",
            });
        });

        it("resolves ptTram regardless of line name", () => {
            expect(infoFor("ptTram", "some tram name")).toEqual({
                background: "#c00808",
                color: "#fff",
            });
        });

        it("resolves ptTramWLB regardless of line name", () => {
            expect(infoFor("ptTramWLB", "some baden tram name")).toEqual({
                background: "#015792",
                color: "#fff",
            });
        });
    });

    describe("unknown vehicle types", () => {
        it.each(["boat", "airplane", "", "PTMETRO"])(
            "falls back for %j",
            (type) => {
                expect(infoFor(type, "U1")).toEqual(UNKNOWN_INFO);
            },
        );
    });

    describe("metro lines outside the registry", () => {
        it("falls back for an unknown metro line instead of crashing", () => {
            expect(infoFor("ptMetro", "U7")).toEqual(UNKNOWN_INFO);
        });

        it.each(["U8", "", "u1", "U1 ", " U1"])(
            "falls back for unnormalized name %j",
            (name) => {
                expect(infoFor("ptMetro", name)).toEqual(UNKNOWN_INFO);
            },
        );

        it("resolves a line literally named UNKNOWN to the unknown colors", () => {
            expect(infoFor("ptMetro", "UNKNOWN")).toEqual(UNKNOWN_INFO);
        });
    });
});
