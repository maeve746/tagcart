const SESSION_KEY = 'tagcart.mock.session.v1'
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// SIMULATED AUTH ONLY. No credentials are verified or transmitted.
export const authService = {
  getSession() { try { return JSON.parse(localStorage.getItem(SESSION_KEY)) } catch { return null } },
  async login({ email, password }) { await wait(650); if (!email.includes('@') || password.length < 6) throw new Error('Enter a valid email and at least 6 characters for the demo password.'); const user = { name: email.split('@')[0].replace(/[._-]/g, ' '), email, simulated: true }; localStorage.setItem(SESSION_KEY, JSON.stringify(user)); return user },
  async register({ name, email, password }) { await wait(700); if (name.trim().length < 2 || !email.includes('@') || password.length < 6) throw new Error('Complete all fields. Demo passwords need at least 6 characters.'); const user = { name: name.trim(), email, simulated: true }; localStorage.setItem(SESSION_KEY, JSON.stringify(user)); return user },
  logout() { localStorage.removeItem(SESSION_KEY) },
}
