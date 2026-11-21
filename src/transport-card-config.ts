import type { LovelaceCardConfig } from "./ha.ts";

export interface TransportCardConfig extends LovelaceCardConfig {
    type: "custom:transport-card";
    entity: string;
    lines?: Array<string>;
    max_departures?: number;
    show_traffic_infos?: boolean;
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

/** Resolves the options a user left out, or set to an unusable value, to their defaults. */
export function normalizeConfig(
    config: TransportCardConfig,
): ResolvedTransportCardConfig {
    return {
        entity: config.entity,
        lines: Array.isArray(config.lines) ? config.lines : [],
        max_departures: isPositiveInteger(config.max_departures)
            ? config.max_departures
            : undefined,
        show_traffic_infos: config.show_traffic_infos !== false,
    };
}

/** Merges the resolved options into the config, keeping its type and other keys. */
export function toEditorConfig(
    config: TransportCardConfig,
): TransportCardConfig {
    const editorConfig: TransportCardConfig = {
        ...config,
        ...normalizeConfig(config),
    };
    // Showing all departures is the meaning of a missing max_departures.
    if (editorConfig.max_departures === undefined) {
        delete editorConfig.max_departures;
    }
    return editorConfig;
}

// A YAML config can hold any value. Departures are cut with slice, which reads
// null as 0 and would hide every departure, so only a count is kept.
function isPositiveInteger(value: unknown): value is number {
    return Number.isInteger(value) && (value as number) > 0;
}
