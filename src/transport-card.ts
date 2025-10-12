import { LitElement, html, css, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";

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
            color: var(--primary-text-color, );
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
            grid-template-columns: 40px 1fr auto auto;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 10px;
            background: var(--ha-card-background, #fafafa);
            transition: background 0.3s ease;
        }

        .departure div:first-child {
            font-weight: 600;
            color: var(--primary-color, #1976d2);
        }

        .departure div:nth-child(2) {
            color: var(--secondary-text-color, #666);
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
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
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

        const monitors = entity.attributes.monitors ?? [];
        if (monitors.length === 0) {
            return html`<ha-card>No monitors available</ha-card>`;
        }

        return html`
            <ha-card>
                ${monitors.map((monitor: any) => this.renderMonitor(monitor))}
            </ha-card>
        `;
    }

    private renderMonitor(monitor: any) {
        const stopName = monitor.locationStop.properties.title;

        return html`
            <div class="stop">
                <span>${stopName}</span>
                ${monitor.lines.map((line: any) => this.renderLine(line))}
            </div>
        `;
    }

    private renderLine(line: any) {
        return html`
            <div class="line">
                ${line.departures.departure.map((dep: any) => this.renderDeparture(dep, line))}
            </div>
        `;
    }

    private renderDeparture(departure: any, line: any) {
        const planned = new Date(departure.departureTime.timePlanned);
        const actual = new Date(departure.departureTime.timeReal || departure.departureTime.timePlanned);
        const now = new Date();

        // in minutes
        const delay = Math.round((actual.getTime() - planned.getTime()) / 60_000);
        const wait = Math.round((actual.getTime() - now.getTime()) / 60_000);

        return html`
            <div class="departure">
                <div>${line.name}</div>
                <div>${line.towards}</div>
                ${wait < 15 
                        ? html`<div>${wait} min</div>`
                        : html`<div>${actual.toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            hour12: false
                        })}</div>`}
                ${delay == 0 
                        ? nothing 
                        : html`<div class="delay">(${Intl.NumberFormat('en', {
                    signDisplay: "always"
                }).format(delay)})</div>`}
            </div>
        `;
    }
}
