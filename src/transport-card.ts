import { css, html, LitElement, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { getVehicleInfo } from "./vehicle";
import {
    type Departure,
    type Line,
    type Stop,
    type VehicleInfo,
} from "./api.ts";
import { ExpiringCache } from "./expiring-cache";
import {
    TRANSPORT_CARD_EDITOR_NAME,
    TRANSPORT_CARD_NAME,
} from "./constants.ts";
import "./transport-card-editor.ts";
import { getHassLanguage, t } from "./i18n.ts";

@customElement(TRANSPORT_CARD_NAME)
export class TransportCard extends LitElement {
    @property({ attribute: false })
    set hass(hass: any) {
        this._hass = hass;
        this._lang = getHassLanguage(hass);
    }

    @state() private _hass: any;
    @state() private _lang: string = "en";

    @property() config: any;

    private cache: ExpiringCache<Stop> = new ExpiringCache<Stop>(
        2 * 60 * 1_000, // 2 minutes
    );

    static getConfigElement() {
        return document.createElement(TRANSPORT_CARD_EDITOR_NAME);
    }

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
            width: 24px;
            height: 24px;
            aspect-ratio: 1 / 1;
            padding: 6px;
            color: inherit;
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

    setConfig(config: any): void {
        if (!config.entity) {
            throw new Error(t("card.config.entity_required", this._lang));
        }
        this.config = config;
    }

    render() {
        if (!this.config || !this._hass) {
            return nothing;
        }

        const entity = this._hass.states[this.config.entity];
        if (!entity) {
            return html`
                <ha-card
                    >${t("card.errors.entity_not_found", this._lang, {
                        entity: this.config.entity,
                    })}</ha-card
                >
            `;
        }

        const stop: Stop = entity.attributes as Stop;
        const hasData = stop.lines && stop.lines.length > 0;

        if (hasData) {
            this.cache.set(stop);
        }

        const data = hasData ? stop : this.cache.get();

        if (!data) {
            return html`
                <ha-card
                    >${t("card.errors.fetch_departures", this._lang, {
                        message: "no data",
                    })}</ha-card
                >
            `;
        }

        let lines: Line[] = data.lines;

        if (
            this.config.lines &&
            Array.isArray(this.config.lines) &&
            this.config.lines.length > 0
        ) {
            lines = data.lines.filter((line: Line) =>
                this.config.lines.includes(line.name),
            );
        }

        if (lines.length === 0) {
            return html` <ha-card
                >${t("card.state.no_departures", this._lang)}</ha-card
            >`;
        }

        return html`
            <ha-card>
                <div class="stop">
                    <span>${data.props.name}</span>
                    ${lines.map((line: Line) => this.renderLine(line))}
                </div>
            </ha-card>
        `;
    }

    private renderLine(line: Line) {
        const max = this.config.max_departures ?? line.departures.length;
        const departures: Departure[] = line.departures.slice(0, max);

        return html`
            <div class="line">
                ${departures.map((dep: Departure) =>
                    this.renderDeparture(dep, line),
                )}
            </div>
        `;
    }

    private renderDeparture(dep: Departure, line: Line) {
        const planned = new Date(dep.time_planned);
        const actual = new Date(dep.time_real ?? dep.time_planned);
        const now = new Date();

        // in minutes
        const delay = Math.round(
            (actual.getTime() - planned.getTime()) / 60_000,
        );
        const wait = Math.round((actual.getTime() - now.getTime()) / 60_000);

        const info: VehicleInfo = getVehicleInfo(dep.vehicle, line);

        return html`
            <div class="departure">
                <div style="background:${info.background};color:${info.color}">
                    ${line.name}
                </div>
                <div>${dep.vehicle.towards}</div>
                <div>
                    ${wait < 15
                        ? html`<span
                              >${wait}
                              ${t("card.time.minute_short", this._lang)}</span
                          >`
                        : html`<span>
                              ${actual.toLocaleTimeString(this._lang, {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                  hour12: false,
                              })}
                          </span>`}
                    ${delay == 0
                        ? nothing
                        : html`<span class="delay">
                              (${Intl.NumberFormat(this._lang, {
                                  signDisplay: "always",
                              }).format(delay)})
                          </span>`}
                </div>
            </div>
        `;
    }
}
