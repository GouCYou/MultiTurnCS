import { createRouter, createWebHistory } from "vue-router";

import Home from "../pages/Home.vue";
import ProductDetail from "../pages/ProductDetail.vue";
import Orders from "../pages/Orders.vue";
import Chat from "@/pages/Chat.vue";
import AdminHome from "../pages/AdminHome.vue";
import AdminOrders from "../pages/Admin.vue";
import AdminProducts from "../pages/AdminProducts.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/product/:id", component: ProductDetail, props: true },
  { path: "/orders", name: "orders", component: Orders },
  { path: "/chat", name: "chat", component: Chat },
  { 
    path: "/admin", 
    component: AdminHome,
    children: [
      { path: "orders", component: AdminOrders, name: "adminOrders" },
      { path: "products", component: AdminProducts, name: "adminProducts" },
      { path: "", redirect: "/admin/orders" }
    ]
  }
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
