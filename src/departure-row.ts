import { css, type CSSResult, html, nothing } from "lit";
import type { Departure, Line } from "./api.ts";
import { departureTiming, formatDelay, formatWait } from "./departures.ts";
import { getVehicleInfo } from "./vehicle.ts";

export const departureRowStyles: CSSResult = css`
    .departure {
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: var(--ha-space-3, 12px);
        padding: 10px 0;
    }

    .departure + .departure {
        border-top: 1px solid var(--divider-color, rgba(128, 128, 128, 0.25));
    }

    .badge {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 26px;
        height: 26px;
        border-radius: var(--ha-border-radius-sm, 4px);
        font-weight: 600;
        font-size: var(--ha-font-size-s, 12px);
        background: var(--line-bg, var(--secondary-background-color));
        color: var(--line-fg, var(--primary-text-color));
    }

    .delay {
        color: var(--warning-color, #ff9800);
        font-variant-numeric: tabular-nums;
        font-size: var(--ha-font-size-s, 12px);
        margin-left: var(--ha-space-1, 4px);
        font-weight: 600;
    }

    .towards-cell {
        display: flex;
        align-items: center;
        gap: var(--ha-space-2, 8px);
        min-width: 0;
        overflow: hidden;
    }

    .towards-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    ha-icon[icon="mdi:snowflake"] {
        --mdc-icon-size: 14px;
        color: var(--info-color, #4fc3f7);
    }
`;

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
