import axios from "axios";

// 走 vite proxy：/api -> http://127.0.0.1:8000/api
const api = axios.create({ baseURL: "/api" });

export async function createOrder(payload) {
  const { data } = await api.post("/orders", payload);
  return data;
}

export async function listOrders() {
  const { data } = await api.get("/orders");
  return data;
}

export async function refundOrder(orderNo, reason = "不想要了/拍错了") {
  const { data } = await api.post(`/orders/${orderNo}/refund`, { reason });
  return data;
}

export async function adminUpdateOrder(orderNo, status) {
  const { data } = await api.patch(`/admin/orders/${orderNo}`, { status });
  return data;
}

export async function deleteOrder(orderNo) {
  const { data } = await api.delete(`/orders/${orderNo}`);
  return data;
}

export async function adminDeleteOrder(orderNo) {
  const { data } = await api.delete(`/admin/orders/${orderNo}`);
  return data;
}
