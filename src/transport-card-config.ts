import type { LovelaceCardConfig } from "./ha.ts";

// YAML writes an option without a value as null, so null means the option is not set.
export interface TransportCardConfig extends LovelaceCardConfig {
    type: "custom:transport-card";
    entity: string;
    lines?: Array<string> | null;
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

/** Resolves the options a config leaves out to their defaults. */
export function resolveConfig(
    config: TransportCardConfig,
): ResolvedTransportCardConfig {
    return {
        entity: config.entity,
        lines: Array.isArray(config.lines) ? config.lines : [],
        max_departures: config.max_departures ?? undefined,
        show_traffic_infos: config.show_traffic_infos ?? true,
    };
}
