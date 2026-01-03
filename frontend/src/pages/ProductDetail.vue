<template>
  <div class="page">
    <button class="back" @click="router.back()">← 返回</button>

    <div v-if="loading" class="hint">加载中…</div>
    <div v-else-if="!p" class="hint">商品不存在</div>

    <div v-else class="content-wrapper">
      <!-- Image Carousel -->
      <div class="carousel-container">
        <div class="carousel">
          <div class="carousel-main">
            <div class="carousel-inner" :style="carouselStyle">
              <div v-for="(img, index) in displayImages" :key="index" class="carousel-item">
                <img :src="fullUrl(img)" :alt="p.title + ' ' + (index + 1)" class="carousel-img">
              </div>
            </div>
          </div>
          
          <!-- Carousel Controls -->
          <button v-if="displayImages.length > 1" class="carousel-control prev" @click="prevSlide">
            &lt;
          </button>
          <button v-if="displayImages.length > 1" class="carousel-control next" @click="nextSlide">
            &gt;
          </button>
        </div>
        
        <!-- Carousel Thumbs -->
        <div v-if="displayImages.length > 1" class="carousel-thumbs">
          <div v-for="(img, index) in displayImages" :key="index" 
               class="thumb-item" 
               :class="{ active: currentIndex === index }"
               @click="goToSlide(index)">
            <img :src="fullUrl(img)" :alt="p.title + ' ' + (index + 1)" class="thumb-img">
          </div>
        </div>
      </div>

      <div class="info-container">
        <div class="product-info">
          <h2 class="name">{{ p.title }}</h2>
          <div class="meta">
            <span>店铺：{{ p.shop_id || "-" }}</span>
            <span>商品ID：{{ p.product_id }}</span>
          </div>

          <div class="price">¥ {{ p.price ?? "--" }}</div>
          <div class="desc">{{ p.description || "暂无介绍" }}</div>

          <div class="specs">
            <h3>参数</h3>
            <div v-if="specEntries.length === 0" class="hint2">暂无参数</div>
            <div v-else class="spec-grid">
              <div v-for="[k, v] in specEntries" :key="k" class="spec-item">
                <div class="k">{{ k }}</div>
                <div class="v">{{ v }}</div>
              </div>
            </div>
          </div>

          <div class="btn-row">
            <button class="chat" @click="goChat">联系客服</button>
            <button class="buy" @click="buyNow">立刻购买</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchProductDetail } from "../api/shop";
import { createOrder } from "../api/order"; // 注意：路径按你项目结构来

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const p = ref(null);
const currentIndex = ref(0);

function fullUrl(path) {
  if (!path) return "";
  // 如果是完整URL直接返回，否则使用相对路径
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return path;
}

onMounted(async () => {
  try {
    p.value = await fetchProductDetail(route.params.id);
  } finally {
    loading.value = false;
  }
});

// 计算显示的轮播图片，优先使用 carousel_images，没有则使用单个 image_url 或 image
const displayImages = computed(() => {
  if (!p.value) return [];
  
  // 如果有轮播图，使用轮播图
  if (p.value.carousel_images && p.value.carousel_images.length > 0) {
    return p.value.carousel_images;
  }
  
  // 否则使用单个图片
  const singleImage = p.value.image_url || p.value.image;
  return singleImage ? [singleImage] : [];
});

// 轮播图样式计算
const carouselStyle = computed(() => {
  return {
    transform: `translateX(-${currentIndex.value * 100}%)`,
    transition: 'transform 0.3s ease'
  };
});

// 轮播图控制方法
function prevSlide() {
  currentIndex.value = (currentIndex.value - 1 + displayImages.value.length) % displayImages.value.length;
}

function nextSlide() {
  currentIndex.value = (currentIndex.value + 1) % displayImages.value.length;
}

function goToSlide(index) {
  currentIndex.value = index;
}

const specEntries = computed(() => {
  const s = p.value?.specs || {};
  return Object.entries(s);
});

function goChat() {
  router.push({
    path: "/chat",
    query: {
      product_id: p.value.product_id,
      shop_id: p.value.shop_id,
    },
  });
}

async function buyNow() {
  if (!p.value) return;

  try {
    const resp = await createOrder({
      product_id: p.value.product_id,
      qty: 1,
      receiver: "演示用户",
      phone_tail: "8899",
    });

    alert(`购买成功！订单号：${resp.order_no}`);
    router.push("/orders");
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || "未知错误";
    alert("下单失败：" + msg);
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f6f6f6;
  padding: 20px;
}

.back {
  border: none;
  background: white;
  color: #333;
  cursor: pointer;
  font-size: 16px;
  padding: 10px 16px;
  border-radius: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.back:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hint {
  padding: 24px;
  color: #666;
  background: white;
  border-radius: 16px;
  margin: 20px auto;
  max-width: 1200px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
}

/* Carousel Styles */
.carousel-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.carousel {
  position: relative;
  width: 100%;
  height: 420px;
  overflow: hidden;
  border-radius: 16px;
  background: #f8f8f8;
}

.carousel-main {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.carousel-inner {
  display: flex;
  height: 100%;
  transition: transform 0.3s ease;
}

.carousel-item {
  flex: 0 0 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.carousel-control:hover {
  background: white;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.carousel-control.prev {
  left: 16px;
}

.carousel-control.next {
  right: 16px;
}

.carousel-thumbs {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  overflow-x: auto;
  padding: 12px 0;
  justify-content: center;
}

.carousel-thumbs::-webkit-scrollbar {
  height: 6px;
}

.carousel-thumbs::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.carousel-thumbs::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.thumb-item {
  flex: 0 0 88px;
  height: 66px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  opacity: 0.7;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.thumb-item:hover {
  opacity: 0.9;
  transform: scale(1.05);
}

.thumb-item.active {
  opacity: 1;
  border-color: #ff6a00;
  transform: scale(1.05);
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Product Info Styles */
.info-container {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.product-info {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.name {
  margin: 0 0 12px;
  font-size: 24px;
  color: #333;
  line-height: 1.3;
}

.meta {
  display: flex;
  gap: 16px;
  color: #777;
  font-size: 13px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.price {
  color: #ff6a00;
  font-weight: 900;
  font-size: 28px;
  margin: 12px 0;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.desc {
  color: #444;
  line-height: 1.7;
  margin: 16px 0;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  font-size: 14px;
}

.specs {
  margin: 20px 0;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
}

.specs h3 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #333;
}

.hint2 {
  color: #888;
  font-size: 14px;
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.spec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 520px) {
  .spec-grid {
    grid-template-columns: 1fr;
  }
}

.spec-item {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px;
  background: white;
  transition: all 0.3s ease;
}

.spec-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.k {
  font-size: 13px;
  color: #777;
  margin-bottom: 6px;
}

.v {
  font-weight: 700;
  font-size: 14px;
  color: #333;
}

.btn-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.chat,
.buy {
  width: 100%;
  height: 50px;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 800;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.chat {
  background: white;
  border: 2px solid #ff6a00;
  color: #ff6a00;
}

.chat:hover {
  background: #fff3ec;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.2);
}

.buy {
  background: #ff6a00;
  color: white;
}

.buy:hover {
  background: #ff8533;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.3);
}
</style>