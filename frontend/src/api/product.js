import axios from "axios";

export async function listProductsDB() {
  const { data } = await axios.get("/api/products_db");
  return data;
}

export async function uploadImage(file) {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await axios.post("/api/admin/upload", fd);
  return data; // {url:"/uploads/xxx.png"}
}

export async function createProduct(form) {
  const fd = new FormData();
  Object.entries(form).forEach(([k, v]) => {
    if (k === "product_id") return;
    if (k === "carousel_images" || k === "specs_json") {
      // 确保数组和JSON对象转换为字符串
      fd.append(k, typeof v === "string" ? v : JSON.stringify(v));
    } else {
      fd.append(k, v ?? "");
    }
  });
  const { data } = await axios.post("/api/admin/products", fd);
  return data;
}

export async function updateProduct(pid, form) {
  const fd = new FormData();
  Object.entries(form).forEach(([k, v]) => {
    if (k === "carousel_images" || k === "specs_json") {
      // 确保数组和JSON对象转换为字符串
      fd.append(k, typeof v === "string" ? v : JSON.stringify(v));
    } else {
      fd.append(k, v ?? "");
    }
  });
  const { data } = await axios.put(`/api/admin/products/${pid}`, fd);
  return data;
}

export async function deleteProduct(pid) {
  const { data } = await axios.delete(`/api/admin/products/${pid}`);
  return data;
}

export async function toggleProduct(productId, isActive) {
  const { data } = await axios.post(`/api/admin/products/${productId}/toggle`, {
    is_active: isActive,
  });
  return data;
}
