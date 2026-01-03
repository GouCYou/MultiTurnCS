import { http } from "./http";

export async function fetchProducts() {
  const res = await http.get("/api/products");
  return res.data;
}

export async function fetchProductDetail(id) {
  const res = await http.get(`/api/products/${id}`);
  return res.data;
}
