import { useEffect, useState } from "react";
import { api, authHeaders } from "../api";

type Booking = {
  id: number;
  booking_code: string;
  guest_name: string;
  status: string;
  start_at: string;
  service_name: string;
  any_barber: boolean;
  barber_id: number | null;
};

export default function AdminPage() {
  const [token, setToken] = useState(localStorage.getItem("adminToken") || "");
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [pending, setPending] = useState<Booking[]>([]);
  const [dashboard, setDashboard] = useState<{ total_revenue: number } | null>(null);
  const [barberPick, setBarberPick] = useState<Record<number, number>>({});

  async function login(e: React.FormEvent) {
    e.preventDefault();
    const res = await api<{ access_token: string }>("/api/admin/login", {
      method: "POST",
      body: JSON.stringify({ username: user, password: pass }),
    });
    localStorage.setItem("adminToken", res.access_token);
    setToken(res.access_token);
  }

  async function refresh() {
    if (!token) return;
    const list = await api<Booking[]>("/api/admin/appointments/pending", {
      headers: authHeaders(token),
    });
    setPending(list);
    const now = new Date();
    const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
    const to = now.toISOString();
    const dash = await api<{ total_revenue: number }>(
      `/api/admin/dashboard?from_date=${encodeURIComponent(from)}&to_date=${encodeURIComponent(to)}`,
      { headers: authHeaders(token) }
    );
    setDashboard(dash);
  }

  useEffect(() => {
    refresh().catch(() => setToken(""));
  }, [token]);

  async function accept(id: number, anyBarber: boolean) {
    const body = anyBarber ? { barber_id: barberPick[id] } : {};
    await api(`/api/admin/appointments/${id}/accept`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    });
    refresh();
  }

  async function reject(id: number) {
    await api(`/api/admin/appointments/${id}/reject`, {
      method: "POST",
      headers: authHeaders(token),
    });
    refresh();
  }

  async function checkout(id: number) {
    await api(`/api/admin/appointments/${id}/checkout`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ revenue: 25 }),
    });
    refresh();
  }

  if (!token) {
    return (
      <div className="card">
        <h2>Admin login</h2>
        <form onSubmit={login}>
          <label>
            Username
            <input value={user} onChange={(e) => setUser(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" value={pass} onChange={(e) => setPass(e.target.value)} />
          </label>
          <button type="submit">Sign in</button>
        </form>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Admin</h2>
      {dashboard && <p>Revenue this month (completed): ${dashboard.total_revenue.toFixed(2)}</p>}
      <h3>Pending</h3>
      {pending.length === 0 && <p>No pending bookings.</p>}
      <ul>
        {pending.map((p) => (
          <li key={p.id}>
            {p.guest_name} — {p.service_name} — {new Date(p.start_at).toLocaleString()} ({p.booking_code})
            {p.any_barber && (
              <label>
                Assign barber id
                <input
                  type="number"
                  onChange={(e) => setBarberPick({ ...barberPick, [p.id]: Number(e.target.value) })}
                />
              </label>
            )}
            <button type="button" onClick={() => accept(p.id, p.any_barber)}>
              Accept
            </button>
            <button type="button" onClick={() => reject(p.id)}>
              Reject
            </button>
          </li>
        ))}
      </ul>
      <h3>Confirmed (quick checkout)</h3>
      <ConfirmedList token={token} onCheckout={checkout} />
    </div>
  );
}

function ConfirmedList({ token, onCheckout }: { token: string; onCheckout: (id: number) => void }) {
  const [rows, setRows] = useState<Booking[]>([]);
  useEffect(() => {
    api<Booking[]>("/api/admin/appointments?status=confirmed", { headers: authHeaders(token) }).then(setRows);
  }, [token]);
  return (
    <ul>
      {rows.map((r) => (
        <li key={r.id}>
          {r.guest_name} — {new Date(r.start_at).toLocaleString()}
          <button type="button" onClick={() => onCheckout(r.id)}>
            Checkout
          </button>
        </li>
      ))}
    </ul>
  );
}
