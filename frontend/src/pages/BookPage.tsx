import { useEffect, useState } from "react";
import { api } from "../api";

type Service = { id: number; name: string; duration_minutes: number; price: number };
type Barber = { id: number; name: string };
type Suggestion = { barber_id: number; barber_name: string; start_at: string };

export default function BookPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [serviceId, setServiceId] = useState<number>();
  const [barberId, setBarberId] = useState<number | "any">("any");
  const [startAt, setStartAt] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [bookingCode, setBookingCode] = useState<string | null>(null);

  useEffect(() => {
    api<Service[]>("/api/services").then(setServices);
    api<Barber[]>("/api/barbers").then(setBarbers);
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    setSuggestions([]);
    setBookingCode(null);
    if (!serviceId || !startAt) return;
    const body = {
      service_id: serviceId,
      start_at: new Date(startAt).toISOString(),
      any_barber: barberId === "any",
      barber_id: barberId === "any" ? null : barberId,
      guest_name: name,
      guest_phone: phone,
    };
    const res = await api<{ ok: boolean; booking?: { booking_code: string }; message?: string; suggestions?: Suggestion[] }>(
      "/api/bookings",
      { method: "POST", body: JSON.stringify(body) }
    );
    if (res.ok && res.booking) {
      setBookingCode(res.booking.booking_code);
      setMessage("Booking submitted — pending admin approval.");
    } else {
      setMessage(res.message || "Could not book");
      setSuggestions(res.suggestions || []);
    }
  }

  function applySuggestion(s: Suggestion) {
    setBarberId(s.barber_id);
    setStartAt(new Date(s.start_at).toISOString().slice(0, 16));
  }

  return (
    <div className="card">
      <h2>Book an appointment</h2>
      <form onSubmit={submit}>
        <label>
          Service
          <select
            value={serviceId ?? ""}
            onChange={(e) => setServiceId(Number(e.target.value))}
            required
          >
            <option value="">Select…</option>
            {services.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.duration_minutes} min — ${s.price})
              </option>
            ))}
          </select>
        </label>
        <label>
          Barber
          <select value={barberId} onChange={(e) => setBarberId(e.target.value === "any" ? "any" : Number(e.target.value))}>
            <option value="any">Any available barber</option>
            {barbers.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Date & time
          <input type="datetime-local" value={startAt} onChange={(e) => setStartAt(e.target.value)} required />
        </label>
        <label>
          Your name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} required />
        </label>
        <button type="submit">Request booking</button>
      </form>
      {message && <p className={bookingCode ? "success" : "error"}>{message}</p>}
      {bookingCode && (
        <p>
          Booking code: <strong>{bookingCode}</strong> — use My booking with last 4 digits of your phone.
        </p>
      )}
      {suggestions.length > 0 && (
        <div>
          <p>Suggested alternatives:</p>
          <ul>
            {suggestions.map((s, i) => (
              <li key={i}>
                {s.barber_name} at {new Date(s.start_at).toLocaleString()}{" "}
                <button type="button" onClick={() => applySuggestion(s)}>
                  Use
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
