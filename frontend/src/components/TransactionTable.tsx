import { Transaction } from "../lib/api";
import { RiskBadge } from "./RiskBadge";

export function TransactionTable({ transactions }: { transactions: Transaction[] }) {
  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Account</th>
            <th>Merchant</th>
            <th>Amount</th>
            <th>Channel</th>
            <th>Risk</th>
            <th>Reasons</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td>{new Date(tx.occurred_at).toLocaleTimeString()}</td>
              <td>{tx.account_id}</td>
              <td>{tx.merchant}</td>
              <td>
                {tx.currency} {tx.amount.toLocaleString()}
              </td>
              <td>{tx.channel}</td>
              <td>
                <RiskBadge level={tx.risk_level} /> <span className="score">{tx.risk_score}</span>
              </td>
              <td>{tx.reasons.slice(0, 2).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
