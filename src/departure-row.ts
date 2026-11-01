import { type CSSResult, html, nothing, unsafeCSS } from "lit";
import type { Departure, Line } from "./api.ts";
import { departureTiming, formatDelay, formatWait } from "./departures.ts";
import { getVehicleInfo } from "./vehicle.ts";
import rowStyles from "./departure-row.css?inline";

export const departureRowStyles: CSSResult = unsafeCSS(rowStyles);

export function renderDepartureRow(
    dep: Departure,
    line: Line,
    lang: string,
    now: Date,
) {
    const { delay, wait, actual } = departureTiming(dep, now);
    const info = getVehicleInfo(dep.vehicle, line);

    return html`
        <div class="departure">
            <div
                class="badge"
                style="--line-bg:${info.background};--line-fg:${info.color}"
            >
                ${line.name}
            </div>
            <div class="towards-cell">
                <span class="towards-text">${dep.vehicle.towards}</span>
                ${renderCoolingIndicator(dep.vehicle.cooling)}
            </div>
            <div>
                <span>${formatWait(wait, actual, lang)}</span>
                ${renderDelay(delay)}
            </div>
        </div>
    `;
}

function renderCoolingIndicator(cooling: boolean) {
    if (!cooling) {
        return nothing;
    }
    return html`<ha-icon icon="mdi:snowflake"></ha-icon>`;
}

function renderDelay(delay: number) {
    const formatted = formatDelay(delay);
    if (formatted === undefined) {
        return nothing;
    }
    return html`<span class="delay">${formatted}</span>`;
}
