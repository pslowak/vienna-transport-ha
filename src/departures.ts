import type { Departure, Line, Stop } from "./api.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";

export function selectLines(stop: Stop, config: TransportCardConfig): Line[] {
    const names = config.lines;
    if (!Array.isArray(names) || names.length === 0) {
        return stop.lines;
    }
    return stop.lines.filter((line) => names.includes(line.name));
}

export function visibleDepartures(
    line: Line,
    maxDepartures?: number,
): Departure[] {
    return maxDepartures === undefined
        ? line.departures
        : line.departures.slice(0, maxDepartures);
}
