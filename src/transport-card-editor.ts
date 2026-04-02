import { css, html, LitElement, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { TRANSPORT_CARD_EDITOR_NAME } from "./constants.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";

@customElement(TRANSPORT_CARD_EDITOR_NAME)
export class TransportCardEditor extends LitElement {
    @property({ attribute: false }) hass: any;

    @state() private config: TransportCardConfig = {};

    static styles = css`
        ha-form {
            display: block;
            margin-bottom: 24px;
        }
    `;

    setConfig(config: TransportCardConfig): void {
        this.config = config;
    }

    render() {
        if (!this.hass) {
            return nothing;
        }

        return html`
            <ha-form
                .hass=${this.hass}
                .data=${this.config}
                .schema=${this.schema}
                .computeLabel=${this.computeLabel}
                .computeHelper=${this.computeHelper}
                @value-changed=${this.onValueChanged}
            ></ha-form>
        `;
    }

    private get schema() {
        return [
            {
                name: "entity",
                selector: {
                    entity: { domain: "sensor" },
                },
            },
            {
                name: "max_departures",
                selector: {
                    number: { min: 0, max: 15, mode: "box" },
                },
            },
            {
                name: "lines",
                selector: {
                    text: { multiple: true },
                },
            },
        ];
    }

    private computeLabel = (schema: any) => {
        switch (schema.name) {
            case "entity":
                return "Entity";
            case "max_departures":
                return "Maximum departures";
            case "lines":
                return "Line";
        }

        return schema.name || undefined;
    };

    private computeHelper = (schema: any) => {
        switch (schema.name) {
            case "entity":
                return "Use your pre-defined sensor here.";
            case "max_departures":
                return "Maximum number of departures to show. Set to 0 to show all.";
            case "lines":
                return "Add line names (e.g., U1). Leave empty to show all.";
        }

        return undefined;
    };

    private onValueChanged(ev: CustomEvent) {
        const value = ev.detail.value as Partial<TransportCardConfig>;

        const newConfig: TransportCardConfig = {
            ...this.config,
            ...value,
            lines: (value.lines ?? []).filter(
                (line) => line?.trim().length > 0,
            ),
        };

        this.dispatchEvent(
            new CustomEvent("config-changed", {
                detail: { config: newConfig },
                bubbles: true,
                composed: true,
            }),
        );
    }
}
