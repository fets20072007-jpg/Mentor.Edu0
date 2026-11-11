export function showToast(message, type = "info") {
    const region = document.getElementById("toastRegion");
    if (!region) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type === "error" ? "toast--error" : ""}`;
    toast.textContent = message;
    region.appendChild(toast);
    setTimeout(() => toast.remove(), 4200);
}
