import type { LovelaceCardConfig } from "./ha.ts";
import { t } from "./i18n.ts";

// YAML writes an option without a value as null, so null means the option is not set.
export interface TransportCardConfig extends LovelaceCardConfig {
    type: "custom:transport-card";
    entity: string;
    /** Line names; YAML reads names like 71 as numbers. */
    lines?: Array<string | number> | null;
    max_departures?: number | null;
    show_traffic_infos?: boolean | null;
}

/** Card config with each option resolved to the value the card uses. */
export interface ResolvedTransportCardConfig {
    entity: string;
    /** Lines to show, empty to show all lines. */
    lines: string[];
    /** Maximum departures per line, undefined to show all departures. */
    max_departures?: number;
    show_traffic_infos: boolean;
}

/**
 * Checks the options of a config, throwing an error that names the invalid option.
 *
 * The entity is not checked: the editor starts from a config without one.
 */
export function assertConfig(
    config: LovelaceCardConfig,
    lang?: string,
): asserts config is TransportCardConfig {
    const { lines, max_departures, show_traffic_infos } = config;

    if (lines != null && !isLineList(lines)) {
        throw new Error(t("card.config.invalid_lines", lang));
    }
    if (max_departures != null && !isPositiveInteger(max_departures)) {
        throw new Error(t("card.config.invalid_max_departures", lang));
    }
    if (show_traffic_infos != null && typeof show_traffic_infos !== "boolean") {
        throw new Error(t("card.config.invalid_show_traffic_infos", lang));
    }
}

/** Resolves the options a config leaves out to their defaults. */
export function resolveConfig(
    config: TransportCardConfig,
): ResolvedTransportCardConfig {
    return {
        entity: config.entity,
        lines: (config.lines ?? []).map(String),
        max_departures: config.max_departures ?? undefined,
        show_traffic_infos: config.show_traffic_infos ?? true,
    };
}

/**
 * Builds the config to save from the editor form.
 *
 * The form sends all its data on every change, including defaults it only
 * displays. Options the previous config left unset stay unset while they
 * keep their default.
 */
export function toSavedConfig(
    previous: TransportCardConfig,
    formValue: TransportCardConfig,
): TransportCardConfig {
    const config: TransportCardConfig = { ...previous, ...formValue };

    const lines = (config.lines ?? []).filter(
        (line) => String(line).trim().length > 0,
    );
    if (lines.length > 0 || previous.lines != null) {
        config.lines = lines;
    } else {
        delete config.lines;
    }

    if (
        config.show_traffic_infos === true &&
        previous.show_traffic_infos == null
    ) {
        delete config.show_traffic_infos;
    }

    return config;
}

function isLineList(value: unknown): value is Array<string | number> {
    return (
        Array.isArray(value) &&
        value.every((line) => typeof line === "string" || Number.isFinite(line))
    );
}

function isPositiveInteger(value: unknown): value is number {
    return Number.isInteger(value) && (value as number) > 0;
}
