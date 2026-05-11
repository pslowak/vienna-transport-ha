import { describe, expect, it } from "vitest";
import { t } from "./i18n.ts";

describe("t", () => {
    describe("language resolution", () => {
        it("resolves en-US to English bundle", () => {
            expect(t("meta.locale", "en-US")).toBe("en");
        });

        it("resolves en to English bundle", () => {
            expect(t("meta.locale", "en")).toBe("en");
        });

        it("resolves de-AT to German bundle", () => {
            expect(t("meta.locale", "de-AT")).toBe("de");
        });

        it("resolves de to German bundle", () => {
            expect(t("meta.locale", "de")).toBe("de");
        });
    });

    describe("key resolution", () => {
        it("resolves a top-level nested key in English", () => {
            expect(t("meta.locale", "en")).toBe("en");
        });

        it("resolves a top-level nested key in German", () => {
            expect(t("meta.locale", "de")).toBe("de");
        });

        it("resolves a deeply nested key", () => {
            expect(t("editor.fields.entity.label", "en")).toBe("Entity");
        });
    });

    describe("missing keys", () => {
        it("returns key if key does not exist", () => {
            const key = "key.does.not.exist";
            expect(t(key, "en")).toBe(key);
        });

        it("returns key if key points to subtree", () => {
            const key = "meta";
            expect(t(key, "en")).toBe(key);
        });

        it("returns key if intermediate segment does not exist", () => {
            const key = "card.missing.entity_not_found";
            expect(t(key, "en")).toBe(key);
        });
    });

    describe("placeholder interpolation", () => {
        it("does not interpolate when replacements is not provided", () => {
            expect(t("card.errors.entity_not_found", "en")).toBe(
                "Entity {entity} not found.",
            );
        });

        it("interpolates a single string placeholder in English", () => {
            expect(
                t("card.errors.entity_not_found", "en", {
                    entity: "sensor.wl_u4",
                }),
            ).toBe("Entity sensor.wl_u4 not found.");
        });

        it("interpolates a single string placeholder in German", () => {
            expect(
                t("card.errors.entity_not_found", "de", {
                    entity: "sensor.wl_u4",
                }),
            ).toBe("Entität sensor.wl_u4 nicht gefunden.");
        });

        it("interpolates a number placeholder coerced to string", () => {
            expect(
                t("card.errors.fetch_departures", "en", { message: 404 }),
            ).toBe("Error fetching departures: 404");
        });
    });
});
