<template>
  <div class="page">
    <div class="grid">
      <div class="card">
        <h3>新增商品</h3>

        <div class="row">
          <label>店铺ID</label>
          <input v-model="form.shop_id" placeholder="S001" />
        </div>
        <div class="row">
          <label>标题</label>
          <input v-model="form.title" placeholder="商品名" />
        </div>
        <div class="row">
          <label>类目</label>
          <input v-model="form.category" placeholder="CPU/手机…" />
        </div>
        <div class="row">
          <label>价格</label>
          <input v-model="form.price" type="number" step="0.01" />
        </div>
        <div class="row">
          <label>描述</label>
          <textarea v-model="form.description" rows="3" />
        </div>

        <div class="row">
          <label>参数JSON</label>
          <textarea v-model="form.specs_json" rows="4" placeholder='{"核心/线程":"8/16","接口":"AM5"}' />
        </div>

        <div class="row">
          <label>轮播图 (最多5张)</label>
          <input type="file" accept="image/*" multiple @change="onPickCarousel" />
          <div v-if="form.carousel_images && form.carousel_images.length > 0" class="img-grid">
            <div v-for="(img, index) in form.carousel_images" :key="index" class="img-item">
              <img :src="fullUrl(img)" />
              <button class="btn-remove" @click="removeCarouselImage(index)">×</button>
            </div>
          </div>
        </div>

        <div class="button-group">
          <button class="btn primary" @click="doSubmit">提交新增</button>
        </div>
      </div>

      <div class="card">
        <div class="head">
          <h3>商品列表</h3>
          <button class="btn" @click="load">刷新</button>
        </div>

        <div v-if="loading">加载中...</div>

        <div v-else class="list">
          <div v-for="p in products" :key="p.product_id" class="item">
            <img class="thumb" v-if="p.image_url" :src="fullUrl(p.image_url)" />
            <div class="info">
              <div class="t">{{ p.title }} <span class="muted">({{ p.product_id }})</span></div>
              <div class="muted">店铺：{{ p.shop_id }} ｜ 类目：{{ p.category }} ｜ ¥{{ p.price }}</div>
            </div>
            <div class="ops">
              <button class="btn" @click="doToggle(p)">
                {{ isRowActive(p) ? "下架" : "上架" }}
              </button>
              <button class="btn danger" @click="doDelete(p.product_id)">删除</button>
            </div>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { listProductsDB, uploadImage, createProduct, deleteProduct, toggleProduct } from "@/api/product";

const loading = ref(true);
const products = ref([]);



const form = ref({
  shop_id: "",
  title: "",
  category: "",
  price: 0,
  description: "",
  specs_json: "{}",
  image_url: "",
  carousel_images: [],
});

function fullUrl(path) {
  // 如果是完整URL直接返回，否则使用相对路径
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return path;
}

async function load() {
  loading.value = true;
  try {
    products.value = await listProductsDB();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

async function onPick(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const resp = await uploadImage(file);
  form.value.image_url = resp.url;
}

async function onPickCarousel(e) {
  const files = e.target.files;
  if (!files || files.length === 0) return;
  
  // 限制最多5张
  const remaining = 5 - form.value.carousel_images.length;
  if (remaining <= 0) {
    alert('轮播图最多只能上传5张');
    return;
  }
  
  const filesToUpload = Array.from(files).slice(0, remaining);
  
  for (const file of filesToUpload) {
    try {
      const resp = await uploadImage(file);
      form.value.carousel_images.push(resp.url);
    } catch (e) {
      alert('图片上传失败：' + (e?.message || '未知错误'));
      break;
    }
  }
}

function removeCarouselImage(index) {
  form.value.carousel_images.splice(index, 1);
}



async function doSubmit() {
  try {
    // 确保JSON格式正确
    try {
      JSON.parse(form.value.specs_json);
    } catch (jsonError) {
      alert('参数JSON格式错误');
      return;
    }
    
    // 新增模式
    const resp = await createProduct(form.value);
    alert("新增成功，商品ID：" + (resp.product_id || ""));
    form.value = {
      shop_id: "",
      title: "",
      category: "",
      price: 0,
      description: "",
      specs_json: "{}",
      image_url: "",
      carousel_images: [],
    };
    await load();
  } catch (e) {
    alert("新增失败：" + (e?.response?.data?.detail || e.message));
  }
}

async function doDelete(pid) {
  if (!confirm("确定删除该商品？")) return;
  try {
    await deleteProduct(pid);
    alert("已删除");
    await load();
  } catch (e) {
    alert("删除失败：" + (e?.response?.data?.detail || e.message));
  }
}

function isRowActive(p) {
  return p?.is_active === 1 || p?.is_active === true;
}



async function doToggle(p) {
  const nextActive = !isRowActive(p);
  try {
    await toggleProduct(p.product_id, nextActive);
    alert(nextActive ? "已上架" : "已下架");
    await load();
  } catch (e) {
    alert("操作失败：" + (e?.response?.data?.detail || e.message));
  }
}
</script>

<style scoped>
.page{ padding:16px; }
.grid{ display:grid; grid-template-columns: 420px 1fr; gap:14px; }
@media (max-width: 980px){ .grid{ grid-template-columns:1fr; } }
.card{ background:#fff; border-radius:12px; padding:12px; box-shadow:0 4px 14px rgba(0,0,0,.06); }
.row{ display:grid; gap:6px; margin:10px 0; }
label{ font-size:12px; color:#777; }
input, textarea{ border:1px solid #ddd; border-radius:10px; padding:8px 10px; }
.btn{ border:1px solid #ddd; background:#fff; padding:8px 12px; border-radius:10px; cursor:pointer; }
.btn.primary{ background:#ff6a00; border-color:#ff6a00; color:#fff; font-weight:800; }
.btn.danger{ border-color:#ff3b30; color:#ff3b30; }
.button-group{ display:flex; gap:10px; margin-top:10px; }
.head{ display:flex; align-items:center; justify-content:space-between; }
.list{ display:grid; gap:10px; margin-top:10px; }
.item{ display:flex; gap:10px; align-items:center; border:1px solid #eee; border-radius:12px; padding:10px; }
.thumb{ width:56px; height:56px; border-radius:10px; object-fit:cover; border:1px solid #eee; }
.info{ flex:1; }
.t{ font-weight:800; }
.muted{ color:#777; font-size:12px; }
.ops{ display:flex; gap:8px; }
.imgwrap img{ width:100%; max-height:180px; object-fit:cover; border-radius:12px; border:1px solid #eee; }
.img-grid{ display:grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap:10px; margin-top:10px; }
.img-item{ position:relative; width:100%; aspect-ratio:1/1; border-radius:10px; overflow:hidden; border:1px solid #eee; }
.img-item img{ width:100%; height:100%; object-fit:cover; }
.btn-remove{ position:absolute; top:4px; right:4px; width:20px; height:20px; border:none; border-radius:50%; background:rgba(0,0,0,0.6); color:white; font-size:14px; cursor:pointer; display:flex; align-items:center; justify-content:center; z-index:10; }
.btn-remove:hover{ background:rgba(0,0,0,0.8); }
.hint{ margin-top:10px; color:#999; font-size:12px; }
</style>