import { type CSSResult, html, nothing, unsafeCSS } from "lit";
import { t } from "./i18n.ts";
import type { TrafficInfo, TrafficInfoCategory } from "./api.ts";
import infoStyles from "./traffic-info.css?inline";

export const trafficInfoStyles: CSSResult = unsafeCSS(infoStyles);

const TRAFFIC_INFO_ICONS = {
    elevator: "mdi:elevator-passenger",
} satisfies Record<TrafficInfoCategory, string>;

const DEFAULT_TRAFFIC_INFO_ICON = "mdi:alert";

function trafficInfoIcon(category: TrafficInfoCategory): string {
    const icons: Record<string, string | undefined> = TRAFFIC_INFO_ICONS;
    return icons[category] ?? DEFAULT_TRAFFIC_INFO_ICON;
}

export function renderTrafficInfos(
    infos: TrafficInfo[],
    lang: string,
    enabled = true,
) {
    if (!enabled || infos.length === 0) {
        return nothing;
    }
    return infos.map(
        (info) => html`
            <div class="traffic-info">
                <div class="traffic-info-header">
                    <ha-icon
                        icon="${trafficInfoIcon(info.category)}"
                        aria-hidden="true"
                    ></ha-icon>
                    <span class="traffic-info-category"
                        >${t(
                            `card.traffic_info.category.${info.category}`,
                            lang,
                        )}</span
                    >
                </div>
                <span>${info.description}</span>
            </div>
        `,
    );
}
