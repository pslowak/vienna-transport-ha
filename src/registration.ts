import { TRANSPORT_CARD_NAME } from "./constants.ts";

interface CustomCardsWindow extends Window {
    customCards?: Array<Record<string, unknown>>;
}

const customCardsWindow = window as unknown as CustomCardsWindow;
customCardsWindow.customCards = customCardsWindow.customCards || [];
customCardsWindow.customCards.push({
    type: TRANSPORT_CARD_NAME,
    name: "Vienna Public Transport Card",
    description: "Display departures from Vienna public transport stops",
    preview: true,
    documentationURL: "https://github.com/pslowak/vienna-transport-ha",
});
