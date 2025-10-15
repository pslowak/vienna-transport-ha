import { LitElement, html, css, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";
import { getVehicleInfo } from "./vehicle";
import type { Departure, Line, Monitor, VehicleInfo } from "./types";

@customElement("transport-card")
export class TransportCard extends LitElement {
    @property({ attribute: false }) hass: any;
    @property() config: any;

    static styles = css`
        ha-card {
            display: flex;
            flex-direction: column;
            padding: 12px;
            gap: 12px;
            background: var(--card-background-color, white);
            color: var(--primary-text-color, black);
            transition: all 0.3s ease;
        }

        .stop {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 12px;
            border-radius: 12px;
            background: var(--secondary-background-color, rgba(0, 0, 0, 0.03));
            transition: background 0.3s ease;
        }

        .stop > span {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--primary-color, #1976d2);
        }

        .line {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .departure {
            display: grid;
            grid-template-columns: auto 1fr auto;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 10px;
            background: var(--ha-card-background, #fafafa);
            transition: background 0.3s ease;
        }

        .departure div:first-child {
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 8px;
            font-weight: 600;
            color: white;
            width: 24px;
            height: 24px;
            aspect-ratio: 1 / 1;
            padding: 6px;
            background: inherit;
        }

        .delay {
            color: var(--error-color, #e53935);
        }

        @media (prefers-color-scheme: dark) {
            ha-card {
                background: rgba(40, 40, 40, 0.8);
                color: #f1f1f1;
            }

            .departure {
                background: rgba(255, 255, 255, 0.05);
            }

            .stop {
                background: rgba(255, 255, 255, 0.04);
            }
        }
    `;

    setConfig(config: any) {
        if (!config.entity) {
            throw new Error("You need to define an entity");
        }
        this.config = config;
    }

    render() {
        if (!this.config || !this.hass) {
            return nothing;
        }

        const entity = this.hass.states[this.config.entity];
        if (!entity) {
            return html`<ha-card>Entity ${this.config.entity} not found</ha-card>`;
        }

        const monitors: Monitor[] = entity.attributes.monitors ?? [];
        if (monitors.length === 0) {
            return html`<ha-card>No monitors available</ha-card>`;
        }

        let filtered: Monitor[] = monitors;
        if (this.config.lines && Array.isArray(this.config.lines) && this.config.lines.length > 0) {
           filtered = monitors.filter((monitor: Monitor) =>
                   monitor.lines.some((line: Line) => this.config.lines.includes(line.name))
           );
        }

        return html`
            <ha-card>
                ${filtered.map((monitor: Monitor) => this.renderMonitor(monitor))}
            </ha-card>
        `;
    }

    private renderMonitor(monitor: Monitor) {
        const stopName = monitor.locationStop.properties.title;

        return html`
            <div class="stop">
                <span>${stopName}</span>
                ${monitor.lines.map((line: Line) => this.renderLine(line))}
            </div>
        `;
    }

    private renderLine(line: Line) {
        const max = this.config.max_departures ?? line.departures.departure.length;
        const departures: Departure[] = line.departures.departure.slice(0, max);

        return html`
            <div class="line">
                ${departures.map((dep: Departure) => this.renderDeparture(dep, line))}
            </div>
        `;
    }

    private renderDeparture(dep: Departure, line: Line) {
        const planned = new Date(dep.departureTime.timePlanned);
        const actual = new Date(dep.departureTime.timeReal ?? dep.departureTime.timePlanned);
        const now = new Date();

        // in minutes
        const delay = Math.round((actual.getTime() - planned.getTime()) / 60_000);
        const wait = Math.round((actual.getTime() - now.getTime()) / 60_000);

        const info: VehicleInfo = getVehicleInfo(dep.vehicle, line);

        return html`
            <div class="departure">
                <div style="background:${info.color}">${line.name}</div>
                <div>${line.towards}</div>
                <div>
                    ${wait < 15
                            ? html`<span>${wait} min</span>`
                            : html`<span>${actual.toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                            })}</span>`}
                    ${delay == 0
                            ? nothing
                            : html`<span class="delay">(${Intl.NumberFormat('en', {
                                signDisplay: "always"
                            }).format(delay)})</span>`} 
                </div>
            </div>
        `;
    }
}
