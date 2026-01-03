<template>
  <div>
    <header class="topbar">
      <div class="brand" @click="go('/')">智能商城客服模拟系统</div>

      <div class="nav">
        <div 
          class="search-wrapper" 
          :class="{ 'search-expanded': isSearchExpanded }"
        >
          <div class="search-box">
            <input
              class="search-input"
              v-model="keyword"
              placeholder="搜索商品 / 类目 / 店铺..."
              @keyup.enter="handleSearchEnter"
              @focus="expandSearch"
              @blur="collapseSearch"
            />
            <span class="search-icon" @click="toggleSearch">🔍︎</span>
          </div>
        </div>
        <button class="navbtn" @click="go('/')">首页</button>
        <button class="navbtn" @click="go('/orders')">我的订单</button>
        <button class="navbtn" @click="go('/chat')">联系客服</button>
        <button class="navbtn" @click="go('/admin')">管理后台</button>
      </div>
    </header>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, provide } from "vue";
const router = useRouter();
const go = (path) => router.push(path);

// 搜索状态管理，提供给子组件使用
const keyword = ref("");
provide('searchKeyword', keyword);

// 搜索框展开状态
const isSearchExpanded = ref(false);

// 处理搜索框回车事件
const handleSearchEnter = () => {
  // 按回车直接返回首页
  go('/');
};

// 展开搜索框
const expandSearch = () => {
  isSearchExpanded.value = true;
};

// 收起搜索框
const collapseSearch = () => {
  if (keyword.value.trim() === '') {
    isSearchExpanded.value = false;
  }
};

// 点击搜索图标跳转首页
const toggleSearch = () => {
  go('/');
};
</script>

<style scoped>
.topbar{
  height:64px;
  background: linear-gradient(135deg, #ff6a00 0%, #ff8c00 100%);
  color:#fff;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 20px;
  box-shadow: 0 4px 20px rgba(255, 106, 0, 0.3);
}
.brand{
  font-weight:900;
  cursor:pointer;
  user-select:none;
  min-width: 200px;
  font-size: 18px;
  letter-spacing: 0.5px;
  transition: transform 0.2s ease;
}
.brand:hover {
  transform: scale(1.05);
}
.nav{ 
  display:flex; 
  gap:12px;
  margin-left: auto;
  align-items:center;
}
.navbtn{
  border: 2px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.2);
  color:#fff;
  padding:8px 16px;
  border-radius:12px;
  cursor:pointer;
  font-weight:700;
  transition: all 0.3s ease;
  font-size: 14px;
  letter-spacing: 0.5px;
}
.navbtn:hover{ 
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.search-wrapper{
  position: relative;
  width: 200px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  margin-right: 10px;
  min-width: 200px;
}
.search-wrapper.search-expanded {
  width: 350px;
  margin-left: -150px;
}
.search-box{
  position:relative;
  width:100%;
  display: flex;
  align-items: center;
}
.search-input{
  width:100%;
  padding:10px 40px 10px 15px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  outline:none;
  font-size:14px;
  background: rgba(255, 255, 255, 0.7);
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
}
.search-wrapper.search-expanded .search-input {
  opacity: 1;
}
.search-input:focus {
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.search-input::placeholder {
  color: #999;
  font-weight: 400;
}
.search-icon{
  position:absolute;
  right: 5px;
  top:50%;
  transform:translateY(-50%);
  color:#ff6a00;
  font-size:18px;
  transition: all 0.3s ease;
  cursor: pointer;
  z-index: 10;
  background: rgba(255, 255, 255, 0.7);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
.search-icon:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-50%) scale(1.05);
  color: #ff8c00;
}
.search-wrapper.search-expanded .search-icon {
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  width: 32px;
  height: 32px;
  right: 5px;
  border-radius: 50%;
}
.search-wrapper.search-expanded .search-icon:hover {
  transform: translateY(-50%) scale(1.05);
  background: rgba(255, 255, 255, 1);
}
.main{ background:#f8f9fa; min-height: calc(100vh - 64px); overflow: hidden; }
</style>