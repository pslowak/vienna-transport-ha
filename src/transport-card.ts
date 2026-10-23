import { css, html, LitElement, nothing, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { getVehicleInfo } from "./vehicle";
import {
    type Departure,
    type Line,
    type Stop,
    type TrafficInfo,
    type TrafficInfoCategory,
    type VehicleInfo,
} from "./api.ts";
import {
    TRANSPORT_CARD_EDITOR_NAME,
    TRANSPORT_CARD_NAME,
} from "./constants.ts";
import type { HomeAssistant, LovelaceCard } from "./ha.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import "./registration.ts";
import "./transport-card-editor.ts";
import { getHassLanguage, t } from "./i18n.ts";

const TRAFFIC_INFO_ICONS = {
    elevator: "mdi:elevator-passenger",
} satisfies Record<TrafficInfoCategory, string>;

const DEFAULT_TRAFFIC_INFO_ICON = "mdi:alert";

function trafficInfoIcon(category: TrafficInfoCategory): string {
    const icons: Record<string, string | undefined> = TRAFFIC_INFO_ICONS;
    return icons[category] ?? DEFAULT_TRAFFIC_INFO_ICON;
}

@customElement(TRANSPORT_CARD_NAME)
export class TransportCard extends LitElement implements LovelaceCard {
    @property({ attribute: false }) hass?: HomeAssistant;

    @state() private _lang: string = "en";

    @state() private config?: TransportCardConfig;

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

    willUpdate(changedProps: PropertyValues): void {
        if (changedProps.has("hass")) {
            this._lang = getHassLanguage(this.hass);
        }
    }

    static styles = css`
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

        .line + .line,
        .departure + .departure {
            border-top: 1px solid
                var(--divider-color, rgba(128, 128, 128, 0.25));
        }

        .departure {
            display: grid;
            grid-template-columns: auto 1fr auto;
            align-items: center;
            gap: var(--ha-space-3, 12px);
            padding: 10px 0;
        }

        .stop > .line:last-child > .departure:last-child {
            padding-bottom: 0;
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
            color: var(--error-color, #e53935);
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

        .traffic-info {
            display: flex;
            flex-direction: column;
            gap: var(--ha-space-1, 4px);
            padding: 8px 12px;
            margin: var(--ha-space-1, 4px) 0;
            border-radius: 10px;
            border-left: 4px solid var(--warning-color, #ffa726);
            background: var(
                --secondary-background-color,
                rgba(127, 127, 127, 0.08)
            );
            font-size: var(--ha-font-size-s, 12px);
        }

        .traffic-info-header {
            display: flex;
            align-items: center;
            gap: var(--ha-space-2, 8px);
        }

        .traffic-info ha-icon {
            --mdc-icon-size: 20px;
            color: var(--warning-color, #ffa726);
            flex-shrink: 0;
        }

        .traffic-info-category {
            font-weight: 600;
        }
    `;

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
        let lines: Line[] = stop.lines;

        if (
            this.config!.lines &&
            Array.isArray(this.config!.lines) &&
            this.config!.lines.length > 0
        ) {
            lines = stop.lines.filter((line: Line) =>
                this.config!.lines!.includes(line.name),
            );
        }

        if (lines.length === 0) {
            return html`
                <ha-card>
                    ${this.renderTrafficInfos(stop.traffic_infos)}
                    ${t("card.state.no_departures", this._lang)}
                </ha-card>
            `;
        }

        return html`
            <ha-card>
                ${this.renderTrafficInfos(stop.traffic_infos)}
                <div class="stop">
                    <span>${stop.props.name}</span>
                    ${lines.map((line: Line) => this.renderLine(line))}
                </div>
            </ha-card>
        `;
    }

    private renderLine(line: Line) {
        const max = this.config!.max_departures ?? line.departures.length;
        const departures: Departure[] = line.departures.slice(0, max);

        return html`
            <div class="line">
                ${this.renderTrafficInfos(line.traffic_infos)}
                ${departures.map((dep: Departure) =>
                    this.renderDeparture(dep, line),
                )}
            </div>
        `;
    }

    private renderTrafficInfos(infos: TrafficInfo[]) {
        if (infos.length === 0) {
            return nothing;
        }
        return infos.map(
            (info) => html`
                <div class="traffic-info">
                    <div class="traffic-info-header">
                        <ha-icon
                            icon="${trafficInfoIcon(info.category)}"
                        ></ha-icon>
                        <span class="traffic-info-category"
                            >${t(
                                `card.traffic_info.category.${info.category}`,
                                this._lang,
                            )}</span
                        >
                    </div>
                    <span>${info.description}</span>
                </div>
            `,
        );
    }

    private renderDeparture(dep: Departure, line: Line) {
        const planned = new Date(dep.time_planned);
        const actual = new Date(dep.time_real);
        const now = new Date();

        // in minutes
        const delay = Math.round(
            (actual.getTime() - planned.getTime()) / 60_000,
        );
        const wait = Math.round((actual.getTime() - now.getTime()) / 60_000);

        const info: VehicleInfo = getVehicleInfo(dep.vehicle, line);

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
                    ${this.renderCoolingIndicator(dep.vehicle.cooling)}
                </div>
                <div>
                    ${this.renderWaitingTime(wait, actual)}
                    ${this.renderDelay(delay)}
                </div>
            </div>
        `;
    }

    private renderCoolingIndicator(cooling: boolean) {
        if (!cooling) {
            return nothing;
        }
        return html`<ha-icon icon="mdi:snowflake"></ha-icon>`;
    }

    private renderWaitingTime(wait: number, actual: Date) {
        if (wait <= 0) {
            return html`<span>${t("card.time.now", this._lang)}</span>`;
        }
        if (wait < 15) {
            return html`
                <span>${wait} ${t("card.time.minute_short", this._lang)}</span>
            `;
        }
        return html`
            <span
                >${actual.toLocaleTimeString(this._lang, {
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                })}</span
            >
        `;
    }

    private renderDelay(delay: number) {
        if (delay == 0) {
            return nothing;
        }
        return html`<span class="delay">
            (${Intl.NumberFormat(this._lang, {
                signDisplay: "always",
            }).format(delay)})
        </span>`;
    }
}
