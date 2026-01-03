<template>
  <div>

    <div v-if="loading" class="hint">加载中…</div>
    <div v-else-if="filtered.length === 0" class="hint">暂无商品</div>

    <div class="grid">
      <div
        v-for="p in filtered"
        :key="p.product_id"
        class="card"
        @click="goDetail(p.product_id)"
      >
        <div class="thumb">
          <img :src="getProductImage(p)" :alt="p.title" class="product-img">
          <span class="tag">{{ p.category || "商品" }}</span>
        </div>

        <div class="info">
          <div class="name">{{ p.title }}</div>
          <div class="desc">{{ p.description || "暂无介绍" }}</div>

          <div class="bottom">
            <div class="price">¥ {{ p.price ?? "--" }}</div>
            <div class="shop">店铺：{{ p.shop_id ?? "-" }}</div>
          </div>
        </div>
      </div>
    </div>


    <div class="foot">提示：点击任意商品进入详情页</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, inject } from "vue";
import { useRouter } from "vue-router";
import { fetchProducts } from "../api/shop";

const router = useRouter();

const loading = ref(true);
const products = ref([]);
const keyword = inject('searchKeyword', ref(""));

function fullUrl(path) {
  if (!path) return "";
  // 如果是完整URL直接返回，否则使用相对路径
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return path;
}

function getProductImage(product) {
  // 优先使用image_url
  if (product.image_url) {
    return fullUrl(product.image_url);
  }
  // 如果没有image_url，使用轮播图的第一张
  if (product.carousel_images && product.carousel_images.length > 0) {
    return fullUrl(product.carousel_images[0]);
  }
  // 如果都没有，返回空字符串
  return "";
}

onMounted(async () => {
  try {
    products.value = await fetchProducts();
  } finally {
    loading.value = false;
  }
});

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase();
  if (!k) return products.value;
  return products.value.filter((p) => {
    return (
      String(p.title || "").toLowerCase().includes(k) ||
      String(p.category || "").toLowerCase().includes(k) ||
      String(p.shop_id || "").toLowerCase().includes(k)
    );
  });
});

function goDetail(id) {
  router.push(`/product/${id}`);
}
</script>

<style scoped>

.hint {
  padding: 16px;
  color: #666;
}
.grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  padding: 16px;
}
@media (max-width: 1400px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
  }
}
@media (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}
@media (max-width: 520px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 12px;
  }
}

.card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
.thumb {
  aspect-ratio: 1 / 1;
  background: linear-gradient(135deg, #f8f8f8, #ffffff);
  position: relative;
  overflow: hidden;
}
.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.card:hover .product-img {
  transform: scale(1.05);
}
.tag {
  position: absolute;
  left: 12px;
  top: 12px;
  background: #ff5000;
  color: white;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
  z-index: 1;
}
.info {
  padding: 14px;
}
.name {
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 8px;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.price {
  color: #ff5000;
  font-weight: 800;
  font-size: 18px;
}
.shop {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.foot {
  margin: 16px;
  color: #888;
  font-size: 12px;
  text-align: center;
}
</style>
