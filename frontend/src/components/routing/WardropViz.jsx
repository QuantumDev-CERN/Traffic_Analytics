import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

export default function WardropViz({ routes = [] }) {
  const data = routes.length ? routes : [{ percentage: 52 }, { percentage: 29 }, { percentage: 19 }];
  const colors = ["#0f766e", "#2563eb", "#d97706", "#64748b"];
  return (
    <div className="donut">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="percentage" innerRadius={42} outerRadius={64}>
            {data.map((_, i) => <Cell key={i} fill={colors[i % colors.length]} />)}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
