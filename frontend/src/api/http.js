import axios from "axios";

export const http = axios.create({
  baseURL: "/", // 走 vite proxy
  timeout: 20000,
});
