<template>
  <div v-if="product" class="container">
    <img :src="getProductImage(product)" class="img"/>
    <h2>{{ product.title }}</h2>
    <p class="price">￥{{ product.price }}</p>

    <h4>商品参数</h4>
    <ul>
      <li v-for="(v, k) in product.specs" :key="k">
        {{ k }}：{{ v }}
      </li>
    </ul>

    <p>{{ product.description }}</p>

    <button @click="goChat">联系客服</button>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchProductDetail } from "../api/backend";

const route = useRoute();
const router = useRouter();
const product = ref(null);

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
  const res = await fetchProductDetail(route.params.id);
  product.value = res.data;
});

function goChat() {
  router.push({
    path: "/chat",
    query: {
      product_id: product.value.product_id,
      shop_id: product.value.shop_id
    }
  });
}
</script>

<style scoped>
.container { padding: 20px; }
.img { max-width: 300px; }
.price { color: #e1251b; font-size: 20px; }
button {
  margin-top: 20px;
  padding: 10px 16px;
}
</style>
