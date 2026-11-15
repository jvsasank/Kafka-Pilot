import { Transaction } from "../lib/api";

export function RiskBadge({ level }: { level: Transaction["risk_level"] }) {
  return <span className={`riskBadge ${level}`}>{level}</span>;
}
