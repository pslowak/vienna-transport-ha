import { css, html, LitElement, nothing, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { TRANSPORT_CARD_EDITOR_NAME } from "./constants.ts";
import type { HomeAssistant, LovelaceCardEditor } from "./ha.ts";
import type { TransportCardConfig } from "./transport-card-config.ts";
import { getHassLanguage, t } from "./i18n.ts";

interface EditorSchema {
    name: string;
}

@customElement(TRANSPORT_CARD_EDITOR_NAME)
export class TransportCardEditor
    extends LitElement
    implements LovelaceCardEditor
{
    @property({ attribute: false }) hass?: HomeAssistant;

    @state() private _lang: string = "en";
    @state() private _config?: TransportCardConfig;

    willUpdate(changedProps: PropertyValues): void {
        if (changedProps.has("hass")) {
            this._lang = getHassLanguage(this.hass);
        }
    }

    static styles = css`
        ha-form {
            display: block;
            margin-bottom: 24px;
        }
    `;

    setConfig(config: TransportCardConfig): void {
        this._config = config;
    }

    render() {
        if (!this.hass) {
            return nothing;
        }

        return html`
            <ha-form
                .hass=${this.hass}
                .data=${this._config}
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
                    number: { min: 1, max: 15, mode: "box" },
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

    private computeLabel = (schema: EditorSchema) => {
        switch (schema.name) {
            case "entity":
                return t("editor.fields.entity.label", this._lang);
            case "max_departures":
                return t("editor.fields.max_departures.label", this._lang);
            case "lines":
                return t("editor.fields.lines.label", this._lang);
        }

        return schema.name || undefined;
    };

    private computeHelper = (schema: EditorSchema) => {
        switch (schema.name) {
            case "entity":
                return t("editor.fields.entity.helper", this._lang);
            case "max_departures":
                return t("editor.fields.max_departures.helper", this._lang);
            case "lines":
                return t("editor.fields.lines.helper", this._lang);
        }

        return undefined;
    };

    private onValueChanged(ev: CustomEvent) {
        const value = ev.detail.value as Partial<TransportCardConfig>;

        const newConfig: TransportCardConfig = {
            type: "transport-card",
            entity: "",
            ...this._config,
            ...value,
            lines: (value.lines ?? this._config?.lines ?? []).filter(
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
