<template>
  <div class="page">
    <div v-if="loading">加载中...</div>

    <div v-else class="order-list">
      <div v-for="o in orders" :key="o.order_no" class="order-card">
        <div class="order-head">
          <div>
            <div class="order-no">订单号：{{ o.order_no }}</div>
            <div class="order-meta">
              当前状态：
              <span class="badge">{{ o.status }}</span>
              ｜ 金额：¥{{ o.total_amount }}
            </div>
          </div>
          <div class="order-time">{{ o.created_at }}</div>
        </div>

        <div class="items">
          <div v-for="it in o.items" :key="it.product_id" class="item">
            <div class="title">{{ it.title }}</div>
            <div class="sub">x{{ it.qty }} ｜ ¥{{ it.price }} ｜ 店铺：{{ it.shop_id }}</div>
          </div>
        </div>

        <div class="actions">
          <select v-model="o._nextStatus" class="select">
            <option disabled value="">选择新状态</option>
            <option v-for="s in allowStatuses" :key="s" :value="s">{{ s }}</option>
          </select>

          <button class="btn primary" @click="applyStatus(o)" :disabled="!o._nextStatus">
            更新状态
          </button>
          
          <button class="btn danger" @click="deleteOrder(o)">
            删除订单
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { listOrders, adminUpdateOrder, adminDeleteOrder } from "@/api/order";

const orders = ref([]);
const loading = ref(true);

const allowStatuses = ["PAID", "SHIPPED", "DELIVERED", "CANCELLED", "REFUNDING", "REFUNDED"];

async function load() {
  loading.value = true;
  try {
    const data = await listOrders();
    // 给每条订单加一个临时字段 _nextStatus
    orders.value = (data || []).map(o => ({ ...o, _nextStatus: "" }));
  } finally {
    loading.value = false;
  }
}

onMounted(load);

async function applyStatus(o) {
  try {
    await adminUpdateOrder(o.order_no, o._nextStatus);
    alert(`已更新：${o.order_no} -> ${o._nextStatus}`);
    await load();
  } catch (e) {
    alert("更新失败：" + (e?.response?.data?.detail || e.message));
  }
}

async function deleteOrder(o) {
  if (!confirm(`确定要删除订单 ${o.order_no} 吗？此操作不可恢复。`)) {
    return;
  }
  
  try {
    await adminDeleteOrder(o.order_no);
    alert(`订单 ${o.order_no} 已删除`);
    await load();
  } catch (e) {
    alert("删除失败：" + (e?.response?.data?.detail || e.message));
  }
}
</script>

<style scoped>
.page { padding: 16px; }
.order-list { display: grid; gap: 12px; }
.order-card { background: #fff; border-radius: 12px; padding: 12px; box-shadow: 0 4px 14px rgba(0,0,0,.06); }
.order-head { display:flex; justify-content:space-between; gap:12px; padding-bottom:10px; border-bottom:1px solid #eee; }
.order-no { font-weight: 700; }
.order-meta { color:#666; font-size: 13px; margin-top:4px; }
.order-time { color:#999; font-size: 12px; white-space: nowrap; }
.items { padding: 10px 0; display:grid; gap: 8px; }
.item .title { font-weight: 600; }
.item .sub { color:#666; font-size: 13px; }
.actions { display:flex; gap: 10px; justify-content: flex-end; align-items:center; }
.select { padding: 8px 10px; border-radius: 10px; border:1px solid #ddd; background:#fff; }
.btn { border:1px solid #ddd; background:#fff; padding:8px 12px; border-radius: 10px; cursor:pointer; }
.btn.primary { background:#ff6a00; border-color:#ff6a00; color:#fff; font-weight:700; }
.btn.danger { background:#ff4444; border-color:#ff4444; color:#fff; font-weight:700; }
.badge { display:inline-block; padding: 2px 8px; border-radius: 999px; background:#fff3ea; color:#ff6a00; font-weight:700; }
</style>
