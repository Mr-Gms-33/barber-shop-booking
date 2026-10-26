import { useEffect, useState } from "react";
import { api, authHeaders } from "../api";
import { formatEuro } from "../format";
import AdminCatalog from "./AdminCatalog";
import AdminHistory from "./AdminHistory";

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
  const [dashboard, setDashboard] = useState<{
    total_revenue: number;
    by_service: { name: string; revenue: number }[];
    by_barber: { name: string; revenue: number }[];
    by_day: { date: string; revenue: number }[];
  } | null>(null);
  const [barbers, setBarbers] = useState<{ id: number; name: string }[]>([]);
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
    setBarbers(await api<{ id: number; name: string }[]>("/api/admin/barbers", { headers: authHeaders(token) }));
    const now = new Date();
    const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
    const to = now.toISOString();
    const dash = await api<{
      total_revenue: number;
      by_service: { name: string; revenue: number }[];
      by_barber: { name: string; revenue: number }[];
      by_day: { date: string; revenue: number }[];
    }>(
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

  async function checkout(id: number, defaultPrice: number) {
    const input = window.prompt("Revenue (EUR)", String(defaultPrice));
    if (!input) return;
    await api(`/api/admin/appointments/${id}/checkout`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ revenue: Number(input) }),
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
      {dashboard && (
        <div>
          <p>Umsatz diesen Monat (abgeschlossen): {formatEuro(dashboard.total_revenue)}</p>
          <details>
            <summary>Breakdowns</summary>
            <p>By service: {dashboard.by_service.map((x) => `${x.name} ${formatEuro(x.revenue)}`).join(", ") || "—"}</p>
            <p>By barber: {dashboard.by_barber.map((x) => `${x.name} ${formatEuro(x.revenue)}`).join(", ") || "—"}</p>
            <p>By day: {dashboard.by_day.map((x) => `${x.date} ${formatEuro(x.revenue)}`).join(", ") || "—"}</p>
          </details>
        </div>
      )}
      <AdminCatalog token={token} />
      <h3>Pending</h3>
      {pending.length === 0 && <p>No pending bookings.</p>}
      <ul>
        {pending.map((p) => (
          <li key={p.id}>
            {p.guest_name} — {p.service_name} — {new Date(p.start_at).toLocaleString()} ({p.booking_code})
            {p.any_barber && (
              <label>
                Assign barber
                <select
                  onChange={(e) => setBarberPick({ ...barberPick, [p.id]: Number(e.target.value) })}
                  defaultValue=""
                >
                  <option value="" disabled>
                    Choose…
                  </option>
                  {barbers.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
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
      <AdminHistory token={token} />
    </div>
  );
}

function ConfirmedList({
  token,
  onCheckout,
}: {
  token: string;
  onCheckout: (id: number, defaultPrice: number) => void;
}) {
  const [rows, setRows] = useState<Booking[]>([]);
  useEffect(() => {
    api<Booking[]>("/api/admin/appointments?status=confirmed", { headers: authHeaders(token) }).then(setRows);
  }, [token]);
  return (
    <ul>
      {rows.map((r) => (
        <li key={r.id}>
          {r.guest_name} — {new Date(r.start_at).toLocaleString()}
          <button type="button" onClick={() => onCheckout(r.id, 32)}>
            Checkout
          </button>
        </li>
      ))}
    </ul>
  );
}
