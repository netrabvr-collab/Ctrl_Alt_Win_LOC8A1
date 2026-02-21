// App.jsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { month: "Jan", sales: 4000 },
  { month: "Feb", sales: 3000 },
  { month: "Mar", sales: 5000 },
  { month: "Apr", sales: 4000 },
];

export default function App() {
  return (
    <div className="flex h-screen font-sans bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg flex flex-col p-6">
        <h1 className="text-2xl font-bold mb-8 text-blue-600">TradeSwipe</h1>
        <nav className="flex flex-col gap-4">
          <a href="#" className="hover:bg-blue-100 rounded px-3 py-2">Dashboard</a>
          <a href="#" className="hover:bg-blue-100 rounded px-3 py-2">Products</a>
          <a href="#" className="hover:bg-blue-100 rounded px-3 py-2">Buyers</a>
          <a href="#" className="hover:bg-blue-100 rounded px-3 py-2">Analytics</a>
          <a href="#" className="hover:bg-blue-100 rounded px-3 py-2">Profile</a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        <h2 className="text-3xl font-semibold mb-6">Dashboard</h2>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <h3 className="text-gray-500 mb-2">Top Buyer</h3>
            <p className="text-2xl font-bold">USA</p>
            <p className="text-green-500">$12,000</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <h3 className="text-gray-500 mb-2">Top Product</h3>
            <p className="text-2xl font-bold">Electronics</p>
            <p className="text-green-500">₹9,500</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <h3 className="text-gray-500 mb-2">Monthly Sales</h3>
            <p className="text-2xl font-bold">$25,400</p>
            <p className="text-green-500">+12% from last month</p>
          </div>
        </div>

        {/* Charts */}
        <div className="bg-white p-6 rounded-xl shadow mb-8">
          <h3 className="text-gray-700 font-semibold mb-4">Sales Trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="sales" stroke="#1E88E5" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Buyers Table */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h3 className="text-gray-700 font-semibold mb-4">Recent Buyers</h3>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2">Buyer</th>
                <th className="px-4 py-2">Country</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Date</th>
              </tr>
            </thead>
            <tbody>
              <tr className="hover:bg-gray-50">
                <td className="px-4 py-2">ABC Traders</td>
                <td className="px-4 py-2">USA</td>
                <td className="px-4 py-2">$5,000</td>
                <td className="px-4 py-2">2026-02-20</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-4 py-2">Global Exporters</td>
                <td className="px-4 py-2">Germany</td>
                <td className="px-4 py-2">$3,200</td>
                <td className="px-4 py-2">2026-02-19</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-4 py-2">India Exports</td>
                <td className="px-4 py-2">India</td>
                <td className="px-4 py-2">$2,800</td>
                <td className="px-4 py-2">2026-02-18</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}