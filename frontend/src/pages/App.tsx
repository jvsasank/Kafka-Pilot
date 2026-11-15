import { useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, Banknote, Check, RadioTower, RefreshCw, ShieldCheck } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Alert, api, Summary, Transaction } from "../lib/api";
import { KpiCard } from "../components/KpiCard";
import { TransactionTable } from "../components/TransactionTable";

const merchants = ["Atlas Crypto Desk", "Urban Grocer", "Bluebird Travel", "Northstar Gift Cards", "Metro Utilities"];
const countries = ["US", "US", "CA", "GB", "NG"];
const channels = ["card", "card", "manual_entry", "wire"];

function randomEvent() {
  const risky = Math.random() > 0.65;
  return {
    event_id: `evt-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    account_id: `acct-${Math.ceil(Math.random() * 12)}`,
    merchant: risky ? merchants[Math.floor(Math.random() * merchants.length)] : "Neighborhood Market",
    amount: risky ? Math.ceil(2500 + Math.random() * 14000) : Math.ceil(15 + Math.random() * 600),
    currency: "USD",
    country: risky ? countries[Math.floor(Math.random() * countries.length)] : "US",
    channel: risky ? channels[Math.floor(Math.random() * channels.length)] : "card",
    account_velocity_10m: risky ? Math.ceil(Math.random() * 11) : Math.ceil(Math.random() * 3),
    occurred_at: new Date().toISOString()
  };
}

export function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [riskFilter, setRiskFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      const [nextSummary, nextTransactions, nextAlerts] = await Promise.all([
        api.summary(),
        api.transactions(riskFilter),
        api.alerts()
      ]);
      setSummary(nextSummary);
      setTransactions(nextTransactions);
      setAlerts(nextAlerts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reach API");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 5000);
    return () => window.clearInterval(timer);
  }, [riskFilter]);

  const chartData = useMemo(
    () =>
      ["low", "medium", "high", "critical"].map((level) => ({
        level,
        count: summary?.risk_distribution[level] ?? 0
      })),
    [summary]
  );

  async function simulate() {
    await api.createTransaction(randomEvent());
    await load();
  }

  async function acknowledge(id: string) {
    await api.acknowledge(id);
    await load();
  }

  return (
    <main>
      <header className="topbar">
        <div>
          <span className="eyebrow"><RadioTower size={14} /> Kafka Pilot</span>
          <h1>Financial event monitoring for fraud operations</h1>
        </div>
        <div className="actions">
          <button title="Refresh dashboard" onClick={load}>
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="primary" title="Generate a sample transaction" onClick={simulate}>
            <Activity size={16} /> Simulate Event
          </button>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="kpiGrid" aria-busy={loading}>
        <KpiCard icon={Banknote} label="Processed Volume" value={`$${(summary?.processed_volume ?? 0).toLocaleString()}`} />
        <KpiCard icon={ShieldCheck} label="Transactions" value={`${summary?.total_transactions ?? 0}`} />
        <KpiCard icon={AlertTriangle} label="High Risk" value={`${summary?.high_risk_transactions ?? 0}`} tone="warn" />
        <KpiCard icon={AlertTriangle} label="Open Alerts" value={`${summary?.unacknowledged_alerts ?? 0}`} tone="danger" />
      </section>

      <section className="contentGrid">
        <div className="panel">
          <div className="panelHead">
            <h2>Risk Distribution</h2>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="level" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panelHead">
            <h2>Alert Queue</h2>
          </div>
          <div className="alertList">
            {alerts.map((alert) => (
              <article className={`alertItem ${alert.acknowledged ? "done" : ""}`} key={alert.id}>
                <div>
                  <strong>{alert.title}</strong>
                  <p>{alert.transaction?.merchant} · {alert.description}</p>
                </div>
                {!alert.acknowledged && (
                  <button title="Acknowledge alert" onClick={() => acknowledge(alert.id)}>
                    <Check size={16} />
                  </button>
                )}
              </article>
            ))}
            {!alerts.length && <p className="empty">No alerts yet.</p>}
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panelHead">
          <h2>Transaction Stream</h2>
          <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)} aria-label="Risk filter">
            <option value="">All risk levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <TransactionTable transactions={transactions} />
      </section>
    </main>
  );
}
