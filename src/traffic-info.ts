import { css, html, nothing, type CSSResult } from "lit";
import { t } from "./i18n.ts";
import type { TrafficInfo, TrafficInfoCategory } from "./api.ts";

export const trafficInfoStyles: CSSResult = css`
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

const TRAFFIC_INFO_ICONS = {
    elevator: "mdi:elevator-passenger",
} satisfies Record<TrafficInfoCategory, string>;

const DEFAULT_TRAFFIC_INFO_ICON = "mdi:alert";

export function trafficInfoIcon(category: TrafficInfoCategory): string {
    const icons: Record<string, string | undefined> = TRAFFIC_INFO_ICONS;
    return icons[category] ?? DEFAULT_TRAFFIC_INFO_ICON;
}

export function renderTrafficInfos(infos: TrafficInfo[], lang: string) {
    if (infos.length === 0) {
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
