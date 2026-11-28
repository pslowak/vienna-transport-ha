import { describe, expect, it } from "vitest";
import en from "./translations/en.json";

type Bundle = { [key: string]: string | Bundle };

const bundles = import.meta.glob<Bundle>("./translations/*.json", {
    eager: true,
    import: "default",
});

function keys(bundle: Bundle, prefix = ""): string[] {
    return Object.entries(bundle)
        .flatMap(([key, value]) =>
            typeof value === "string"
                ? [prefix + key]
                : keys(value, `${prefix}${key}.`),
        )
        .sort();
}

describe("translations", () => {
    it.each(Object.entries(bundles))(
        "%s has the same keys as en.json",
        (_, bundle) => {
            expect(keys(bundle)).toEqual(keys(en));
        },
    );
});
