export class ExpiringCache<T> {
    private data: T | undefined;
    private timestamp: number | undefined;

    private readonly expiryMillis: number;

    constructor(expiryMillis: number) {
        this.expiryMillis = expiryMillis;
    }

    set(data: T) {
        this.data = data;
        this.timestamp = Date.now();
    }

    get(): T | undefined {
        if (this.data === undefined || this.timestamp === undefined) {
            return undefined;
        }

        if (Date.now() - this.timestamp > this.expiryMillis) {
            return undefined;
        }

        return this.data;
    }
}
