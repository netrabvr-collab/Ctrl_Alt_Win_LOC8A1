import React from "react";

const LeadTable = ({ leads }) => (
  <div className="overflow-x-auto">
    <table className="min-w-full bg-white shadow-md rounded-lg">
      <thead className="bg-blue-600 text-white">
        <tr>
          <th className="py-2 px-4">Lead ID</th>
          <th className="py-2 px-4">Product</th>
          <th className="py-2 px-4">Country</th>
          <th className="py-2 px-4">Score</th>
        </tr>
      </thead>
      <tbody>
        {leads.map((lead, idx) => (
          <tr key={idx} className="border-b">
            <td className="py-2 px-4">{lead.lead_id}</td>
            <td className="py-2 px-4">{lead.product}</td>
            <td className="py-2 px-4">{lead.country}</td>
            <td className="py-2 px-4">{lead.score}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default LeadTable;