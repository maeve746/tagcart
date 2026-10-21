const SESSION_KEY = 'tagcart.mock.session.v1'
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function cleanDisplayName(value = '') {
  return value
    .replace(/\d+/g, ' ')
    .replace(/[._-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function nameFromEmail(email = '') {
  return cleanDisplayName(email.split('@')[0]) || 'Seller'
}

// SIMULATED AUTH ONLY. No credentials are verified or transmitted.
export const authService = {
  getSession() {
    try {
      const session = JSON.parse(localStorage.getItem(SESSION_KEY))
      if (!session) return null
      const name = cleanDisplayName(session.name) || nameFromEmail(session.email)
      if (name !== session.name) localStorage.setItem(SESSION_KEY, JSON.stringify({ ...session, name }))
      return { ...session, name }
    } catch { return null }
  },
  async login({ email, password }) { await wait(650); if (!email.includes('@') || password.length < 6) throw new Error('Enter a valid email and at least 6 characters for the demo password.'); const user = { name: nameFromEmail(email), email, simulated: true }; localStorage.setItem(SESSION_KEY, JSON.stringify(user)); return user },
  async register({ name, email, password }) { await wait(700); const displayName = cleanDisplayName(name); if (displayName.length < 2 || !email.includes('@') || password.length < 6) throw new Error('Complete all fields. Demo passwords need at least 6 characters.'); const user = { name: displayName, email, simulated: true }; localStorage.setItem(SESSION_KEY, JSON.stringify(user)); return user },
  logout() { localStorage.removeItem(SESSION_KEY) },
}
