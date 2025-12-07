const API_URL = "http://localhost:8000/api/v1/items";

export async function getItems() {
    const resp = await fetch(API_URL);
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Ошибка загрузки items: ${resp.status} ${text}`);
    }
    return await resp.json();
}

export async function addItem(item) {
    const resp = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
    });
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Ошибка добавления item: ${resp.status} ${text}`);
    }
    return await resp.json();
}
