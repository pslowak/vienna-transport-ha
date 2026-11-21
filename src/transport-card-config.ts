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
        max_departures: config.max_departures,
        show_traffic_infos: config.show_traffic_infos !== false,
    };
}
