import type { HomeAssistant } from "./ha.ts";
import en from "./translations/en.json";
import de from "./translations/de.json";

type TranslationVal = string | { [key: string]: TranslationVal };

const LOCALE_REGISTRY: Record<string, TranslationVal> = {
    en,
    de,
};

const DEFAULT_LANG = "en";

function resolveRegistryKey(lang: string): string {
    let candidate: string = lang.toLowerCase();

    while (candidate.length > 0) {
        if (candidate in LOCALE_REGISTRY) {
            return candidate;
        }

        const lastHyphen = candidate.lastIndexOf("-");

        if (lastHyphen === -1) {
            // Nothing found
            return DEFAULT_LANG;
        }

        candidate = candidate.slice(0, lastHyphen);
    }

    return DEFAULT_LANG;
}

function lookup(lang: string, key: string): string | undefined {
    const value = key
        .split(".")
        .reduce<TranslationVal | undefined>(
            (node, segment) =>
                (node as Record<string, TranslationVal>)?.[segment],
            LOCALE_REGISTRY[lang],
        );
    return typeof value === "string" ? value : undefined;
}

export function t(
    key: string,
    lang: string = DEFAULT_LANG,
    replacements?: Record<string, string | number>,
): string {
    const registryKey = resolveRegistryKey(lang);
    // A key missing in the user's language falls back to English.
    const value = lookup(registryKey, key) ?? lookup(DEFAULT_LANG, key);

    if (value === undefined) {
        console.warn(`[i18n] Missing key "${key}" in locale "${registryKey}"`);
        return key;
    }

    if (!replacements) {
        return value;
    }

    return value.replace(/\{(\w+)}/g, (match, name) =>
        replacements[name] !== undefined ? String(replacements[name]) : match,
    );
}

export function getHassLanguage(hass?: HomeAssistant): string {
    return hass?.locale?.language ?? hass?.language ?? DEFAULT_LANG;
}
