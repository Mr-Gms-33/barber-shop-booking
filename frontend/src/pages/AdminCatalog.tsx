import { useEffect, useState } from "react";
import { api, authHeaders } from "../api";
import { formatEuro } from "../format";

type Service = { id: number; name: string; duration_minutes: number; price: number; active: boolean };
type Barber = { id: number; name: string; active: boolean };

export default function AdminCatalog({ token }: { token: string }) {
  const h = authHeaders(token);
  const [services, setServices] = useState<Service[]>([]);
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [svcForm, setSvcForm] = useState({ name: "", duration_minutes: 30, price: 30, active: true });
  const [barberName, setBarberName] = useState("");
  const [scheduleBarberId, setScheduleBarberId] = useState<number | "">("");
  const [dow, setDow] = useState(0);
  const [startT, setStartT] = useState("09:00");
  const [endT, setEndT] = useState("17:00");

  async function load() {
    setServices(await api<Service[]>("/api/admin/services", { headers: h }));
    setBarbers(await api<Barber[]>("/api/admin/barbers", { headers: h }));
  }

  useEffect(() => {
    load();
  }, [token]);

  async function addService(e: React.FormEvent) {
    e.preventDefault();
    await api("/api/admin/services", { method: "POST", headers: h, body: JSON.stringify(svcForm) });
    setSvcForm({ name: "", duration_minutes: 30, price: 30, active: true });
    load();
  }

  async function toggleService(s: Service) {
    await api(`/api/admin/services/${s.id}`, {
      method: "PATCH",
      headers: h,
      body: JSON.stringify({ ...s, active: !s.active }),
    });
    load();
  }

  async function addBarber(e: React.FormEvent) {
    e.preventDefault();
    await api("/api/admin/barbers", {
      method: "POST",
      headers: h,
      body: JSON.stringify({ name: barberName, active: true }),
    });
    setBarberName("");
    load();
  }

  async function saveSchedule(e: React.FormEvent) {
    e.preventDefault();
    if (!scheduleBarberId) return;
    await api(`/api/admin/barbers/${scheduleBarberId}/schedule`, {
      method: "PUT",
      headers: h,
      body: JSON.stringify([
        { day_of_week: dow, start_time: `${startT}:00`, end_time: `${endT}:00` },
      ]),
    });
    alert("Schedule saved (Mon–Fri defaults remain from seed if not replaced fully).");
  }

  return (
    <section>
      <h3>Services (EUR)</h3>
      <ul>
        {services.map((s) => (
          <li key={s.id}>
            {s.name} — {s.duration_minutes} Min. — {formatEuro(Number(s.price))}{" "}
            {s.active ? "(active)" : "(inactive)"}
            <button type="button" onClick={() => toggleService(s)}>
              Toggle active
            </button>
          </li>
        ))}
      </ul>
      <form onSubmit={addService}>
        <input
          placeholder="Service name"
          value={svcForm.name}
          onChange={(e) => setSvcForm({ ...svcForm, name: e.target.value })}
          required
        />
        <input
          type="number"
          placeholder="Minutes"
          value={svcForm.duration_minutes}
          onChange={(e) => setSvcForm({ ...svcForm, duration_minutes: Number(e.target.value) })}
        />
        <input
          type="number"
          step="0.01"
          placeholder="Price EUR"
          value={svcForm.price}
          onChange={(e) => setSvcForm({ ...svcForm, price: Number(e.target.value) })}
        />
        <button type="submit">Add service</button>
      </form>

      <h3>Barbers</h3>
      <ul>
        {barbers.map((b) => (
          <li key={b.id}>
            #{b.id} {b.name} {b.active ? "" : "(inactive)"}
          </li>
        ))}
      </ul>
      <form onSubmit={addBarber}>
        <input value={barberName} onChange={(e) => setBarberName(e.target.value)} placeholder="Barber name" required />
        <button type="submit">Add barber</button>
      </form>

      <h3>Weekly hours (one day slot)</h3>
      <form onSubmit={saveSchedule}>
        <select value={scheduleBarberId} onChange={(e) => setScheduleBarberId(Number(e.target.value))} required>
          <option value="">Barber…</option>
          {barbers.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <select value={dow} onChange={(e) => setDow(Number(e.target.value))}>
          {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d, i) => (
            <option key={d} value={i}>
              {d}
            </option>
          ))}
        </select>
        <input type="time" value={startT} onChange={(e) => setStartT(e.target.value)} />
        <input type="time" value={endT} onChange={(e) => setEndT(e.target.value)} />
        <button type="submit">Save day schedule</button>
      </form>
    </section>
  );
}
