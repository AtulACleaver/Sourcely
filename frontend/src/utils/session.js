// A transient session ID that exists only for the duration of the page load.
// It is NOT stored in localStorage, so refresh = new session.
const SESSION_ID = crypto.randomUUID()

export const getSessionId = () => SESSION_ID
