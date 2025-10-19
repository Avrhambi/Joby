// Real HTTP API client for backend running on localhost:8001
const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';

async function request(path, { method = 'GET', token = null, body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
  if (!res.ok) {
    const msg = (data && data.message) || res.statusText || 'API error';
    throw new Error(msg);
  }
  return data;
}

const api = {
  signup: async ({ email, password, firstName, lastName }) => {
    return await request('/signup', { method: 'POST', body: { email, password, firstName, lastName } });
  },
  login: async ({ email, password }) => {
    return await request('/login', { method: 'POST', body: { email, password } });
  },
  getNotifications: async (token) => {
    return await request('/notifications', { method: 'GET', token });
  },
  // Save a full list of notifications for the current user
  saveNotifications: async (token, notifs) => {
    return await request('/notifications', { method: 'PUT', token, body: notifs });
  },
  // Create a single notification (returns created resource)
  createNotification: async (token, payload) => {
    return await request('/notifications', { method: 'POST', token, body: payload });
  },
  // Update a single notification by id
  updateNotification: async (token, id, payload) => {
    return await request(`/notifications/${id}`, { method: 'PUT', token, body: payload });
  },
  // Delete a single notification by id
  deleteNotification: async (token, id) => {
    return await request(`/notifications/${id}`, { method: 'DELETE', token });
  },
  // Optional helpers
  getUser: async (token) => {
    return await request('/user/me', { method: 'GET', token });
  },
  updateUser: async (token, payload) => {
    return await request('/user/me', { method: 'PUT', token, body: payload });
  }
  ,
  changePassword: async (token, { currentPassword, newPassword }) => {
    // Expected backend endpoint: POST /user/me/password with { currentPassword, newPassword }
    return await request('/user/me/password', { method: 'POST', token, body: { currentPassword, newPassword } });
  }
};

export default api;
