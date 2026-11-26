import { html, LitElement, nothing, unsafeCSS, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { TRANSPORT_CARD_EDITOR_NAME } from "./constants.ts";
import type { HomeAssistant, LovelaceCardEditor } from "./ha.ts";
import {
    resolveConfig,
    type TransportCardConfig,
} from "./transport-card-config.ts";
import { getHassLanguage, t } from "./i18n.ts";
import type en from "./translations/en.json";
import editorStyles from "./transport-card-editor.css?inline";

interface EditorSchema {
    name: keyof typeof en.editor.fields;
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

    static styles = unsafeCSS(editorStyles);

    setConfig(config: TransportCardConfig): void {
        this._config = {
            ...config,
            show_traffic_infos: resolveConfig(config).show_traffic_infos,
        };
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
                name: "show_traffic_infos",
                selector: {
                    boolean: {},
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

    private computeLabel = (schema: EditorSchema) =>
        t(`editor.fields.${schema.name}.label`, this._lang);

    private computeHelper = (schema: EditorSchema) =>
        t(`editor.fields.${schema.name}.helper`, this._lang);

    private onValueChanged(ev: CustomEvent) {
        const value = ev.detail.value as Partial<TransportCardConfig>;

        const newConfig: TransportCardConfig = {
            type: "custom:transport-card",
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
