import { LucideIcon } from "lucide-react";

type Props = {
  icon: LucideIcon;
  label: string;
  value: string;
  tone?: "default" | "warn" | "danger";
};

export function KpiCard({ icon: Icon, label, value, tone = "default" }: Props) {
  return (
    <section className={`kpi kpi-${tone}`}>
      <div className="iconBox">
        <Icon size={20} />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </section>
  );
}
