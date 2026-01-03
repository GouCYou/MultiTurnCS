<template>
  <div class="page">
    <div v-if="loading">加载中...</div>

    <div v-else class="order-list">
      <div v-for="o in orders" :key="o.order_no" class="order-card">
        <div class="order-head">
          <div>
            <div class="order-no">订单号：{{ o.order_no }}</div>
            <div class="order-meta">状态：{{ o.status }} ｜ 金额：¥{{ o.total_amount }}</div>
          </div>
          <div class="order-time">{{ o.created_at }}</div>
        </div>

        <div class="items">
          <div
            v-for="it in o.items"
            :key="it.product_id"
            class="item"
            @click="goToProductDetail(it.product_id)"
          >
            <img
              v-if="it.image_url"
              class="thumb"
              :src="fullUrl(it.image_url)"
              :alt="it.title"
            />
            <div v-else class="thumb placeholder">暂无图片</div>
            <div class="info">
              <div class="t">{{ it.title }}</div>
              <div class="muted">x{{ it.qty }} ｜ ¥{{ it.price }} ｜ 店铺：{{ it.shop_id }}</div>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn delete" @click="doDeleteOrder(o.order_no)">删除订单</button>
          <button class="btn" @click="doRefund(o.order_no)">退货退款</button>
          <button class="btn" @click="repurchase(o)">再次购买</button>
          <button class="btn primary" @click="goChatByOrder(o.order_no)">联系客服</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { listOrders, createOrder, refundOrder, deleteOrder } from "@/api/order";

const router = useRouter();
const orders = ref([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    orders.value = await listOrders();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

function goChatByOrder(orderNo) {
  router.push({ path: "/chat", query: { order_no: orderNo } });
}

function goToProductDetail(productId) {
  router.push({ path: `/product/${productId}` });
}

function fullUrl(path) {
  if (!path) return "";
  // 如果是完整URL直接返回，否则使用相对路径
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return path;
}

async function doRefund(orderNo) {
  const reason = prompt("请输入退款原因（可留空）", "不想要了/拍错了");
  if (reason === null) return;

  try {
    const resp = await refundOrder(orderNo, reason);
    alert(`已提交退货退款：${resp.after_sale_no}\n订单已变更为：${resp.status}`);
    await load();
  } catch (e) {
    alert("退货退款失败：" + (e?.response?.data?.detail || e.message));
  }
}

async function repurchase(order) {
  const first = order.items?.[0];
  if (!first) return alert("订单没有商品项");

  try {
    const resp = await createOrder({
      product_id: first.product_id,
      qty: first.qty || 1,
      receiver: order.receiver || "演示用户",
      phone_tail: order.phone_tail || "8899",
    });
    alert(`再次购买成功！新订单号：${resp.order_no}`);
    router.push("/orders");
    await load();
  } catch (e) {
    alert("再次购买失败：" + (e?.response?.data?.detail || e.message));
  }
}

async function doDeleteOrder(orderNo) {
  if (!confirm("确定要删除该订单吗？此操作不可恢复。")) return;

  try {
    await deleteOrder(orderNo);
    alert("订单已删除");
    await load();
  } catch (e) {
    alert("删除订单失败：" + (e?.response?.data?.detail || e.message));
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
.items { padding: 10px 0; display:grid; gap: 10px; }
.item {
  display: flex;
  gap: 10px;
  align-items: center;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 10px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0,0,0,.05);
}
.thumb {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #eee;
  background: #f5f5f5;
}
.thumb.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
}
.info { flex: 1; min-width: 0; }
.t { font-weight: 600; margin-bottom: 4px; }
.muted { color:#666; font-size: 13px; }
.btn.link {
  border-color: #ffe2d1;
  background: #fff7f0;
  color: #ff6a00;
  font-weight: 700;
  white-space: nowrap;
}
.actions { display:flex; gap: 10px; justify-content: flex-end; }
.btn { border:1px solid #ddd; background:#fff; padding:8px 12px; border-radius: 10px; cursor:pointer; }
.btn.primary { background:#ff6a00; border-color:#ff6a00; color:#fff; font-weight:700; }
</style>