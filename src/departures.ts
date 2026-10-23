import type { Departure, Line, Stop } from "./api.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import { t } from "./i18n.ts";

/** Wait in minutes from which the actual clock time is shown instead. */
const CLOCK_TIME_THRESHOLD_MINUTES = 15;

export interface DepartureTiming {
    /** Delay in minutes, negative when the departure is early. */
    delay: number;
    /** Minutes until the departure, negative when it already left. */
    wait: number;
    /** The real departure time. */
    actual: Date;
}

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

export function departureTiming(dep: Departure, now: Date): DepartureTiming {
    const planned = new Date(dep.time_planned);
    const actual = new Date(dep.time_real);

    return {
        delay: Math.round((actual.getTime() - planned.getTime()) / 60_000),
        wait: Math.round((actual.getTime() - now.getTime()) / 60_000),
        actual,
    };
}

export function formatWait(wait: number, actual: Date, lang: string): string {
    if (wait <= 0) {
        return t("card.time.now", lang);
    }
    if (wait < CLOCK_TIME_THRESHOLD_MINUTES) {
        return `${wait} ${t("card.time.minute_short", lang)}`;
    }
    return actual.toLocaleTimeString(lang, {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    });
}

export function formatDelay(delay: number, lang: string): string | undefined {
    if (delay === 0) {
        return undefined;
    }
    return Intl.NumberFormat(lang, { signDisplay: "always" }).format(delay);
}
