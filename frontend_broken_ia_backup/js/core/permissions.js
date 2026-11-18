export const ROLES = Object.freeze({
    STUDENT: "aluno",
    TEACHER: "professor",
    ADMIN: "administracao",
    SUPPORT: "suporte",
});

export function normalizeRole(role) {
    const value = String(role || "").trim().toLowerCase();
    if (["administração", "administracao", "admin"].includes(value)) return ROLES.ADMIN;
    if (value === "aluno") return ROLES.STUDENT;
    if (value === "professor") return ROLES.TEACHER;
    if (value === "suporte") return ROLES.SUPPORT;
    return value;
}

export function roleLabel(role) {
    return ({
        [ROLES.STUDENT]: "Aluno",
        [ROLES.TEACHER]: "Professor",
        [ROLES.ADMIN]: "Administração",
        [ROLES.SUPPORT]: "Suporte",
    })[normalizeRole(role)] || "Usuário";
}
