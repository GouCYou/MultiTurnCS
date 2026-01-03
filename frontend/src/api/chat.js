import axios from "axios";

export async function chat(payload) {
  const { data } = await axios.post("/chat", payload);
  return data;
}
