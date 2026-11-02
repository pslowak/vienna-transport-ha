/**
 * Minimal `ha-icon` stand-in for the standalone dev harness.
 * Paths are the official Material Design Icons (same source HA uses).
 */
const MDI_PATHS: Record<string, string> = {
    "mdi:elevator-passenger":
        "M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3M8.5 6C9.19 6 9.75 6.56 9.75 7.25S9.19 8.5 8.5 8.5 7.25 7.94 7.25 7.25 7.81 6 8.5 6M11 14H10V18H7V14H6V11.5C6 10.4 6.9 9.5 8 9.5H9C10.1 9.5 11 10.4 11 11.5V14M15.5 17L13 13H18L15.5 17M13 11L15.5 7L18 11H13Z",
    "mdi:snowflake":
        "M20.79,13.95L18.46,14.57L16.46,13.44V10.56L18.46,9.43L20.79,10.05L21.31,8.12L19.54,7.65L20,5.88L18.07,5.36L17.45,7.69L15.45,8.82L13,7.38V5.12L14.71,3.41L13.29,2L12,3.29L10.71,2L9.29,3.41L11,5.12V7.38L8.5,8.82L6.5,7.69L5.92,5.36L4,5.88L4.47,7.65L2.7,8.12L3.22,10.05L5.55,9.43L7.55,10.56V13.45L5.55,14.58L3.22,13.96L2.7,15.89L4.47,16.36L4,18.12L5.93,18.64L6.55,16.31L8.55,15.18L11,16.62V18.88L9.29,20.59L10.71,22L12,20.71L13.29,22L14.7,20.59L13,18.88V16.62L15.5,15.17L17.5,16.3L18.12,18.63L20,18.12L19.53,16.35L21.3,15.88L20.79,13.95M9.5,10.56L12,9.11L14.5,10.56V13.44L12,14.89L9.5,13.44V10.56Z",
    "mdi:alert": "M13 14H11V9H13M13 18H11V16H13M1 21H23L12 2L1 21Z",
};

const STYLES = `
    :host {
        display: inline-block;
        flex-shrink: 0;
        width: var(--mdc-icon-size, 24px);
        height: var(--mdc-icon-size, 24px);
    }
    svg {
        display: block;
        width: 100%;
        height: 100%;
        fill: currentColor;
    }
`;

class HaIconStub extends HTMLElement {
    static observedAttributes = ["icon"];

    private readonly root = this.attachShadow({ mode: "open" });

    connectedCallback(): void {
        this.update();
    }

    attributeChangedCallback(): void {
        this.update();
    }

    private update(): void {
        const path = MDI_PATHS[this.getAttribute("icon") ?? ""];
        this.root.innerHTML =
            `<style>${STYLES}</style>` +
            (path
                ? `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${path}"/></svg>`
                : "");
    }
}

if (!customElements.get("ha-icon")) {
    customElements.define("ha-icon", HaIconStub);
}
