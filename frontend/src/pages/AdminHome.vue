<template>
  <div class="admin-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>商城管理后台</h2>
      </div>
      <div class="menu">
        <div 
          v-for="item in menuItems" 
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="router.push(item.path)"
        >
          <span class="menu-icon">{{ item.icon }}</span>
          <span class="menu-text">{{ item.title }}</span>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="header">
        <h1>{{ currentPageTitle }}</h1>
      </div>
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const menuItems = [
  {
    path: '/admin/orders',
    title: '订单管理',
    icon: '📋'
  },
  {
    path: '/admin/products',
    title: '商品管理',
    icon: '🛍️'
  }
];

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.path === route.path);
  return currentItem ? currentItem.title : '管理后台';
});
</script>

<style scoped>
.admin-container {
  display: flex;
  height: 100vh;
  background-color: #f8f9fa;
}

/* Sidebar Styles */
.sidebar {
  width: 260px;
  height: 92%;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.15);
  border-radius: 20px;
  overflow: hidden;
  margin: 10px;
}

.sidebar-header {
  padding: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #ffffff;
  text-align: center;
  letter-spacing: 1px;
}

.menu {
  flex: 1;
  padding: 20px 10px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  margin: 5px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  border-left: 4px solid transparent;
  margin-left: 10px;
  margin-right: 10px;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.12);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.menu-item.active {
  background: linear-gradient(135deg, #ff6a00 0%, #ff8c00 100%);
  border-left-color: #ffd700;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(255, 106, 0, 0.4);
  transform: translateX(5px);
}

.menu-icon {
  margin-right: 12px;
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 15px;
  letter-spacing: 0.5px;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f8f9fa;
}

.header {
  padding: 25px 35px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  margin: 10px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.content {
  flex: 1;
  padding: 25px 35px;
  overflow-y: auto;
}
</style>