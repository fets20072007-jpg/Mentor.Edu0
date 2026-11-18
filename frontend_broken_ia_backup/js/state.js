const state = {
    user: null,
    role: null,
    currentPage: "overview",
    unreadNotifications: 0,
};

export function getState() {
    return state;
}

export function setState(patch) {
    Object.assign(state, patch);
    return state;
}

export function resetState() {
    state.user = null;
    state.role = null;
    state.currentPage = "overview";
    state.unreadNotifications = 0;
}
