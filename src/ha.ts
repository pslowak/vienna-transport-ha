export interface HassEntity {
    entity_id: string;
    state: string;
    attributes: Record<string, unknown>;
}

export type HassEntities = Record<string, HassEntity>;

export interface FrontendLocaleData {
    language: string;
}

export interface HomeAssistant {
    states: HassEntities;
    locale: FrontendLocaleData;
    language: string;
}

export interface LovelaceCardConfig {
    type: string;
    [key: string]: unknown;
}

export interface LovelaceCard extends HTMLElement {
    hass?: HomeAssistant;
    setConfig(config: LovelaceCardConfig): void;
    getCardSize?(): number | Promise<number>;
}

export interface LovelaceCardEditor extends HTMLElement {
    hass?: HomeAssistant;
    setConfig(config: LovelaceCardConfig): void;
}
