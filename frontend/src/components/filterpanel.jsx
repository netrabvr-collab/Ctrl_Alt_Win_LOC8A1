import React, { useState } from "react";

const FilterPanel = ({ onFilter }) => {
  const [country, setCountry] = useState("");
  const [minScore, setMinScore] = useState("");

  const handleFilter = () => {
    onFilter({ country, minScore });
  };

  return (
    <div className="flex gap-4 mb-4">
      <input
        type="text"
        placeholder="Country"
        value={country}
        onChange={(e) => setCountry(e.target.value)}
        className="border px-2 py-1 rounded"
      />
      <input
        type="number"
        placeholder="Min Score"
        value={minScore}
        onChange={(e) => setMinScore(e.target.value)}
        className="border px-2 py-1 rounded"
      />
      <button
        onClick={handleFilter}
        className="bg-blue-600 text-white px-4 py-1 rounded"
      >
        Apply
      </button>
    </div>
  );
};

export default FilterPanel;