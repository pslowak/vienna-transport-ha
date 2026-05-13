import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ExpiringCache } from "./expiring-cache.ts";

describe("ExpiringCache", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    describe("empty cache", () => {
        it("returns undefined on empty cache", () => {
            const cache = new ExpiringCache(1_000);
            expect(cache.get()).toBeUndefined();
        });
    });

    describe("expiring behaviour", () => {
        it("returns data within deadline (start)", () => {
            const cache = new ExpiringCache<string>(1_000);
            const data = "payload";
            cache.set(data);

            expect(cache.get()).toBe(data);
        });

        it("returns data within deadline (end)", () => {
            const window = 1_000;
            const cache = new ExpiringCache<string>(window);
            const data = "payload";
            cache.set(data);

            vi.advanceTimersByTime(window);

            expect(cache.get()).toBe(data);
        });

        it("returns undefined when data expired", () => {
            const cache = new ExpiringCache<string>(1_000);
            cache.set("payload");

            vi.advanceTimersByTime(1_001);

            expect(cache.get()).toBeUndefined();
        });
    });

    describe("overriding behavior", () => {
        it("returns latest data", () => {
            const cache = new ExpiringCache<string>(1_000);
            cache.set("first");
            const latest = "latest";
            cache.set(latest);

            expect(cache.get()).toBe(latest);
        });
    });
});
