import { css, html, LitElement, nothing, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { type Line, type Stop } from "./api.ts";
import {
    TRANSPORT_CARD_EDITOR_NAME,
    TRANSPORT_CARD_NAME,
} from "./constants.ts";
import type { HomeAssistant, LovelaceCard } from "./ha.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import "./registration.ts";
import "./transport-card-editor.ts";
import { getHassLanguage, t } from "./i18n.ts";
import { renderTrafficInfos, trafficInfoStyles } from "./traffic-info.ts";
import { departureRowStyles, renderDepartureRow } from "./departure-row.ts";
import { selectLines, visibleDepartures } from "./departures.ts";

@customElement(TRANSPORT_CARD_NAME)
export class TransportCard extends LitElement implements LovelaceCard {
    @property({ attribute: false }) hass?: HomeAssistant;

    @state() private _lang: string = "en";

    @state() private config?: TransportCardConfig;

    @state() private _now: Date = new Date();

    private _timer?: ReturnType<typeof setInterval>;

    static getConfigElement(): HTMLElement {
        return document.createElement(TRANSPORT_CARD_EDITOR_NAME);
    }

    static getStubConfig(): TransportCardConfig {
        return {
            type: "custom:transport-card",
            entity: "",
            max_departures: 3,
        };
    }

    connectedCallback(): void {
        super.connectedCallback();
        this._now = new Date();
        this._timer = setInterval(() => {
            this._now = new Date();
        }, 20_000);
    }

    disconnectedCallback(): void {
        super.disconnectedCallback();
        clearInterval(this._timer);
        this._timer = undefined;
    }

    willUpdate(changedProps: PropertyValues): void {
        if (changedProps.has("hass")) {
            this._lang = getHassLanguage(this.hass);
        }
    }

    static styles = [
        css`
            ha-card {
                display: flex;
                flex-direction: column;
                gap: var(--ha-space-1, 4px);
                padding: var(--ha-space-3, 12px);
                background: var(
                    --ha-card-background,
                    var(--card-background-color, white)
                );
                color: var(--primary-text-color, black);
            }

            .stop {
                display: flex;
                flex-direction: column;
                gap: var(--ha-space-1, 4px);
            }

            .stop > span {
                font-weight: 600;
                font-size: var(--ha-font-size-s, 12px);
                letter-spacing: 0.03em;
                text-transform: uppercase;
                color: var(--secondary-text-color);
            }

            .line {
                display: flex;
                flex-direction: column;
            }

            .line + .line {
                border-top: 1px solid
                    var(--divider-color, rgba(128, 128, 128, 0.25));
            }

            .stop > .line:last-child > .departure:last-child {
                padding-bottom: 0;
            }
        `,
        trafficInfoStyles,
        departureRowStyles,
    ];

    setConfig(config: TransportCardConfig): void {
        if (!config.entity) {
            throw new Error(t("card.config.entity_required", this._lang));
        }
        this.config = config;
    }

    getCardSize(): number {
        return 3;
    }

    render() {
        if (!this.config || !this.hass) {
            return nothing;
        }

        const entity = this.hass.states[this.config.entity];
        if (!entity) {
            return html`
                <ha-card
                    >${t("card.errors.entity_not_found", this._lang, {
                        entity: this.config.entity,
                    })}</ha-card
                >
            `;
        }

        const stop = entity.attributes as unknown as Stop;
        const config = this.config;
        const lines: Line[] = selectLines(stop, config);

        if (lines.length === 0) {
            return html`
                <ha-card>
                    ${renderTrafficInfos(stop.traffic_infos, this._lang)}
                    ${t("card.state.no_departures", this._lang)}
                </ha-card>
            `;
        }

        return html`
            <ha-card>
                ${renderTrafficInfos(stop.traffic_infos, this._lang)}
                <div class="stop">
                    <span>${stop.props.name}</span>
                    ${lines.map((line: Line) =>
                        this.renderLine(line, config, this._now),
                    )}
                </div>
            </ha-card>
        `;
    }

    private renderLine(line: Line, config: TransportCardConfig, now: Date) {
        const departures = visibleDepartures(line, config.max_departures, now);

        return html`
            <div class="line">
                ${renderTrafficInfos(line.traffic_infos, this._lang)}
                ${departures.map((dep) =>
                    renderDepartureRow(dep, line, this._lang, now),
                )}
            </div>
        `;
    }
}
