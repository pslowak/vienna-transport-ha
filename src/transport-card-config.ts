import type { LovelaceCardConfig } from "./ha.ts";

export interface TransportCardConfig extends LovelaceCardConfig {
    type: "transport-card";
    entity: string;
    lines?: Array<string>;
    max_departures?: number;
}
