import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000
});

export function fetchProducts() {
  return api.get("/api/products");
}

export function fetchProductDetail(id) {
  return api.get(`/api/products/${id}`);
}

export function sendChat(data) {
  return api.post("/chat", data);
}
