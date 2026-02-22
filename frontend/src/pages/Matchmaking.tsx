import { useEffect, useState } from "react";
import { getMatchmaking } from "../lib/api";

interface Buyer {
  name: string;
  region: string;
  risk_level: string;
  trade_volume: number;
  match_score: number;
}

export default function Matchmaking() {
  const [buyers, setBuyers] = useState<Buyer[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getMatchmaking();
        setBuyers(data);
      } catch (error) {
        console.error("Error fetching matchmaking data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Matchmaking</h1>

      {buyers.length === 0 && (
        <p className="text-gray-500">No matches available.</p>
      )}

      {buyers.map((buyer, index) => (
        <div
          key={index}
          className="p-4 mb-4 border rounded-lg flex justify-between items-center"
        >
          <div>
            <h2 className="font-semibold">{buyer.name}</h2>
            <p>{buyer.region}</p>
            <p>Risk: {buyer.risk_level}</p>
            <p>Trade Volume: ${buyer.trade_volume}</p>
          </div>

          <div className="text-right">
            <p className="text-xl font-bold text-green-600">
              {buyer.match_score}%
            </p>
            <button className="mt-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded">
              Connect
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
