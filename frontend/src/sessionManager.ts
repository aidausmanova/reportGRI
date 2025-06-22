// src/sessionManager.ts
export function getSessionId(): string {
    const SESSION_KEY = 'app-session-id';
    let sessionId = sessionStorage.getItem(SESSION_KEY);

    if (!sessionId) {
        sessionId = crypto.randomUUID(); // modern and secure
        sessionStorage.setItem(SESSION_KEY, sessionId);
    }

    return sessionId;
}
  