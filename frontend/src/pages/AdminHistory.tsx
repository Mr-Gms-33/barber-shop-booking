import { useState } from "react";
import { api, authHeaders } from "../api";

type Booking = {
  id: number;
  booking_code: string;
  guest_name: string;
  status: string;
  start_at: string;
  service_name: string;
};

export default function AdminHistory({ token }: { token: string }) {
  const [status, setStatus] = useState("");
  const [rows, setRows] = useState<Booking[]>([]);

  async function search(e: React.FormEvent) {
    e.preventDefault();
    const q = status ? `?status=${status}` : "";
    const data = await api<Booking[]>(`/api/admin/appointments${q}`, { headers: authHeaders(token) });
    setRows(data);
  }

  return (
    <section>
      <h3>History</h3>
      <form onSubmit={search}>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="pending">pending</option>
          <option value="confirmed">confirmed</option>
          <option value="completed">completed</option>
          <option value="cancelled">cancelled</option>
          <option value="declined">declined</option>
        </select>
        <button type="submit">Filter</button>
      </form>
      <ul>
        {rows.map((r) => (
          <li key={r.id}>
            {r.guest_name} — {r.service_name} — {r.status} — {new Date(r.start_at).toLocaleString()}
          </li>
        ))}
      </ul>
    </section>
  );
}
