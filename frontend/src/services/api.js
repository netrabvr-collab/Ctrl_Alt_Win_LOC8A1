import axios from "axios";

const API_BASE = "http://127.0.0.1:5000"; // Flask backend

export const getLeads = async () => {
  try {
    const response = await axios.get(`${API_BASE}/leads`);
    return response.data;
  } catch (error) {
    console.error("Error fetching leads:", error);
    return [];
  }
};