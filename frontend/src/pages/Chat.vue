<template>
  <div class="page">
    <div class="chat-container">
      <!-- 左侧聊天区域 -->
      <div class="chat-main">
        <div class="head">
          <div class="ctx" v-if="ctxText">{{ ctxText }}</div>
        </div>

        <div class="box" ref="boxRef">
          <div v-for="(m, i) in messages" :key="i" class="msg" :class="[m.role, { 'thinking': m.isThinking }]">
            <div v-if="m.role === 'assistant'" class="avatar">
              <span>🤖</span>
            </div>
            <div class="bubble">
              <div class="role">{{ m.role === "user" ? "我" : "客服" }}</div>
              <div class="content">{{ m.content }}</div>
            </div>
            <div v-if="m.role === 'user'" class="avatar">
              <span>👤</span>
            </div>
          </div>
        </div>

        <div class="bar">
          <button class="btn" @click="resetChat">重置</button>
          <input
            class="input"
            v-model="input"
            placeholder="请输入..."
            @keydown.enter.prevent="send"
          />
          <button class="btn primary" :disabled="sending" @click="send">
            {{ sending ? "发送中..." : "发送" }}
          </button>
        </div>
      </div>

      <!-- 右侧会话记录区域 -->
      <div class="session-sidebar">
        <div class="sidebar-header">
          <h3>会话记录</h3>
          <div class="sidebar-actions">
            <button class="new-session-btn" @click="createNewSession">
              <span class="icon">+</span> 新会话
            </button>
            <button class="clear-sessions-btn" @click="clearAllSessions">
              <span class="icon">🗑️</span> 清空
            </button>
          </div>
        </div>
        
        <div class="session-list">
          <div 
            v-for="session in sessions" 
            :key="session.id" 
            class="session-item"
            :class="{ active: session.id === currentSessionId }"
          >
            <div class="session-avatar">
              <span>🤖</span>
            </div>
            <div class="session-info" @click="switchSession(session.id)">
              <div class="session-title">
                <span>{{ session.title }}</span>
                <span class="session-time">{{ session.time }}</span>
              </div>
              <div class="session-last-msg">{{ session.lastMessage }}</div>
            </div>
            <button 
              class="session-clear-btn" 
              @click.stop="clearSession(session.id)"
              title="清空会话"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { chat } from "@/api/chat";

const route = useRoute();

// 聊天相关数据
const sessionId = ref(localStorage.getItem("chat_session_id") || "");
const messages = ref([]);
const input = ref("");
const sending = ref(false);
const boxRef = ref(null);

// 会话相关数据
const currentSessionId = ref(sessionId.value || "current");
const sessions = ref([]);

const productId = computed(() => route.query.product_id || "");
const shopId = computed(() => route.query.shop_id || "");
const orderNo = computed(() => route.query.order_no || "");

const ctxText = computed(() => {
  if (orderNo.value) return `当前订单：${orderNo.value}`;
  if (productId.value) return `当前商品：${productId.value}（店铺：${shopId.value || "-"}）`;
  return "";
});

// 加载会话列表
const loadSessions = () => {
  // 从localStorage加载会话列表
  const savedSessions = localStorage.getItem("chat_sessions");
  if (savedSessions) {
    sessions.value = JSON.parse(savedSessions);
  } else {
    // 初始化默认会话
    sessions.value = [{
      id: "current",
      title: "新会话",
      time: new Date().toLocaleString(),
      lastMessage: "开始新的对话..."
    }];
    saveSessions();
  }
};

// 保存会话列表
const saveSessions = () => {
  localStorage.setItem("chat_sessions", JSON.stringify(sessions.value));
};

// 创建新会话
const createNewSession = () => {
  const newSessionId = `session_${Date.now()}`;
  const newSession = {
    id: newSessionId,
    title: "新会话",
    time: new Date().toLocaleString(),
    lastMessage: "开始新的对话..."
  };
  
  sessions.value.unshift(newSession);
  switchSession(newSessionId);
  saveSessions();
};

// 切换会话
const switchSession = (sessionId) => {
  currentSessionId.value = sessionId;
  // 从localStorage加载该会话的消息
  const savedMessages = localStorage.getItem(`chat_messages_${sessionId}`);
  if (savedMessages) {
    messages.value = JSON.parse(savedMessages);
  } else {
    messages.value = [];
  }
  // 保存当前会话ID
  localStorage.setItem("chat_session_id", sessionId);
  
  // 滚动到底部
  scrollToBottom();
};

// 保存消息到localStorage
const saveMessages = () => {
  localStorage.setItem(`chat_messages_${currentSessionId.value}`, JSON.stringify(messages.value));
};

// 更新会话的最后一条消息
const updateSessionLastMessage = (message) => {
  const sessionIndex = sessions.value.findIndex(s => s.id === currentSessionId.value);
  if (sessionIndex !== -1) {
    sessions.value[sessionIndex].lastMessage = message;
    sessions.value[sessionIndex].time = new Date().toLocaleString();
    // 如果不是当前会话列表的第一个，将其移到第一个
    if (sessionIndex !== 0) {
      const session = sessions.value.splice(sessionIndex, 1)[0];
      sessions.value.unshift(session);
    }
    saveSessions();
  }
};

// 清空单个会话
const clearSession = (sessionId) => {
  // 确认删除
  if (confirm("确定要清空这个会话吗？")) {
    // 删除会话的消息
    localStorage.removeItem(`chat_messages_${sessionId}`);
    
    // 如果清空的是当前会话，重置消息
    if (sessionId === currentSessionId.value) {
      messages.value = [];
      sendAutoHelloIfEmpty();
    }
    
    // 更新会话的最后一条消息
    const sessionIndex = sessions.value.findIndex(s => s.id === sessionId);
    if (sessionIndex !== -1) {
      sessions.value[sessionIndex].lastMessage = "会话已清空";
      sessions.value[sessionIndex].time = new Date().toLocaleString();
      saveSessions();
    }
  }
};

// 清空所有会话
const clearAllSessions = () => {
  // 确认删除
  if (confirm("确定要清空所有会话吗？")) {
    // 删除所有会话的消息
    sessions.value.forEach(session => {
      localStorage.removeItem(`chat_messages_${session.id}`);
    });
    
    // 重置当前会话
    messages.value = [];
    localStorage.removeItem(`chat_messages_${currentSessionId.value}`);
    
    // 重置会话列表
    sessions.value = [{
      id: "current",
      title: "新会话",
      time: new Date().toLocaleString(),
      lastMessage: "开始新的对话..."
    }];
    
    // 切换到默认会话
    switchSession("current");
    
    // 保存会话列表
    saveSessions();
    
    // 发送自动问候
    sendAutoHelloIfEmpty();
  }
};

function scrollToBottom() {
  nextTick(() => {
    if (!boxRef.value) return;
    boxRef.value.scrollTop = boxRef.value.scrollHeight;
  });
}

async function sendAutoHelloIfEmpty() {
  if (messages.value.length > 0) return;

  // 根据上下文，给一个更像真实客服入口的首句
  if (orderNo.value) {
    input.value = `我想咨询一下订单 ${orderNo.value} 的状态，以及是否可以退货退款。`;
    await send();
    return;
  }
  if (productId.value) {
    input.value = `我在看商品 ${productId.value}，想了解一下这款的亮点、适合人群，以及有没有优惠？`;
    await send();
    return;
  }
}

async function send() {
  const text = input.value.trim();
  if (!text) return;

  messages.value.push({ role: "user", content: text });
  input.value = "";
  scrollToBottom();
  
  // 保存消息到localStorage
  saveMessages();
  
  // 更新会话的最后一条消息
  updateSessionLastMessage(text);

  sending.value = true;
  
  // 添加"正在思考中..."的临时消息
  const thinkingMessageIndex = messages.value.length;
  messages.value.push({ role: "assistant", content: "正在思考中...", isThinking: true });
  scrollToBottom();
  
  try {
    const resp = await chat({
      session_id: currentSessionId.value === "current" ? (sessionId.value || null) : currentSessionId.value,
      message: text,
      reset: false,
      product_id: productId.value || null,
      shop_id: shopId.value || null,
      order_no: orderNo.value || null,
    });

    sessionId.value = resp.session_id;
    localStorage.setItem("chat_session_id", resp.session_id);

    // 移除"正在思考中..."的消息，添加实际回复
    messages.value.splice(thinkingMessageIndex, 1);
    messages.value.push({ role: "assistant", content: resp.answer });
    scrollToBottom();
    
    // 保存消息到localStorage
    saveMessages();
    
    // 更新会话的最后一条消息
    updateSessionLastMessage(resp.answer);
  } catch (e) {
    // 移除"正在思考中..."的消息，添加错误信息
    messages.value.splice(thinkingMessageIndex, 1);
    messages.value.push({
      role: "assistant",
      content: "请求失败：" + (e?.response?.data?.detail || e.message),
    });
    scrollToBottom();
    
    // 保存消息到localStorage
    saveMessages();
  } finally {
    sending.value = false;
  }
}

async function resetChat() {
  messages.value = [];
  try {
    const resp = await chat({
      session_id: currentSessionId.value === "current" ? (sessionId.value || null) : currentSessionId.value,
      message: "重置会话",
      reset: true,
      product_id: productId.value || null,
      shop_id: shopId.value || null,
      order_no: orderNo.value || null,
    });
    sessionId.value = resp.session_id;
    localStorage.setItem("chat_session_id", resp.session_id);
  } catch (_) {}
  await sendAutoHelloIfEmpty();
  
  // 保存消息到localStorage
  saveMessages();
  
  // 更新会话的最后一条消息
  updateSessionLastMessage("会话已重置");
}

onMounted(async () => {
  // 加载会话列表
  loadSessions();
  
  // 如果当前会话ID不在会话列表中，添加它
  if (!sessions.value.some(s => s.id === currentSessionId.value)) {
    const newSession = {
      id: currentSessionId.value,
      title: "当前会话",
      time: new Date().toLocaleString(),
      lastMessage: "正在进行的对话..."
    };
    sessions.value.unshift(newSession);
    saveSessions();
  }
  
  // 加载当前会话的消息
  const savedMessages = localStorage.getItem(`chat_messages_${currentSessionId.value}`);
  if (savedMessages) {
    messages.value = JSON.parse(savedMessages);
  } else {
    await sendAutoHelloIfEmpty();
  }
  
  // 滚动到底部
  scrollToBottom();
});

// 如果你在同一个 chat 页面里切换 query（比如从订单点进来又从商品点进来）
// 自动清空并重新发一条开场
watch(
  () => [productId.value, shopId.value, orderNo.value],
  async () => {
    messages.value = [];
    await sendAutoHelloIfEmpty();
    
    // 保存消息到localStorage
    saveMessages();
  }
);
</script>

<style scoped>
/* 页面根元素样式 */
.page {
  padding: 0;
  height: calc(100vh - 64px); /* 减去顶部导航栏高度 */
  overflow: hidden !important;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 聊天容器样式 */
.chat-container {
  display: grid;
  grid-template-columns: 1fr 320px;
  height: 90%;
  width: 90%;
  max-width: 1200px;
  overflow: hidden !important;
  background-color: #f5f5f5;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 左侧聊天区域样式 */
.chat-main {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background-color: #f5f5f5;
  overflow: hidden !important;
  height: 100%;
}

/* 聊天消息容器 */
.box {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
  max-height: calc(100% - 50px); /* 减去头部和输入栏的高度 */
}

/* 右侧会话记录区域样式 */
.session-sidebar {
  background-color: white;
  border-left: 1px solid #e0e0e0;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 会话列表 */
.session-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 16px;
  padding-right: 4px;
}

.head {
  margin-bottom: 8px;
}

.ctx {
  color: #666;
  font-size: 14px;
  background-color: #fff;
  padding: 6px 10px;
  border-radius: 8px;
  display: inline-block;
}



.msg {
  display: flex;
  margin: 12px 0;
  align-items: flex-start;
  gap: 12px;
}

.msg.user {
  justify-content: flex-end;
}

.msg.assistant {
  justify-content: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.msg.user .avatar {
  background-color: #ff6a00;
  color: white;
}

.bubble {
  max-width: 70%;
  border-radius: 18px;
  padding: 12px 16px;
  position: relative;
}

.msg.assistant .bubble {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 18px;
}

.msg.user .bubble {
  background: #ff6a00;
  border: 1px solid #ff6a00;
  color: white;
  border-bottom-right-radius: 18px;
}

.role {
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
  font-weight: 500;
}

.msg.user .role {
  color: rgba(255, 255, 255, 0.8);
}

.content {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
}

/* 正在思考中的样式 */
.msg.thinking .content {
  font-style: italic;
  color: #888;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.bar {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
}

.input {
  flex: 1;
  height: 44px;
  border-radius: 22px;
  border: 2px solid #e0e0e0;
  padding: 0 16px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.input:focus {
  outline: none;
  border-color: #ff6a00;
}

.btn {
  border: 2px solid #e0e0e0;
  background: #fff;
  height: 44px;
  padding: 0 18px;
  border-radius: 22px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #ff6a00;
  color: #ff6a00;
}

.btn.primary {
  background: #ff6a00;
  border-color: #ff6a00;
  color: #fff;
  font-weight: 600;
}

.btn.primary:hover {
  background: #ff8533;
  border-color: #ff8533;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  border-color: #e0e0e0;
  color: #999;
  background: #f5f5f5;
}

/* 右侧会话记录区域样式 */
.session-sidebar {
  background-color: #fff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow: hidden !important;
  border-radius: 16px 0 0 16px; /* 添加圆角 */
  height: 100%;
}

.sidebar-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.sidebar-actions {
  display: flex;
  gap: 8px;
}

.new-session-btn {
  background-color: #ff6a00;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background-color 0.3s;
}

.new-session-btn:hover {
  background-color: #ff8533;
}

.new-session-btn .icon {
  font-size: 14px;
  font-weight: bold;
}

.clear-sessions-btn {
  background-color: #fff;
  color: #ff3b30;
  border: 1px solid #ff3b30;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s;
}

.clear-sessions-btn:hover {
  background-color: #ff3b30;
  color: white;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  max-height: calc(100% - 100px); /* 减去头部高度 */
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 4px;
  border: 2px solid transparent;
  position: relative;
}

.session-item:hover {
  background-color: #f5f5f5;
}

.session-item.active {
  background-color: #fff3ec;
  border-color: #ff6a00;
}

.session-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.session-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.session-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.session-title span:first-child {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.session-last-msg {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-clear-btn {
  background: transparent;
  border: none;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
  flex-shrink: 0;
}

.session-item:hover .session-clear-btn {
  opacity: 1;
  color: #ff3b30;
}

.session-clear-btn:hover {
  background-color: #ffebee;
}

/* 滚动条样式 */
.box::-webkit-scrollbar,
.session-list::-webkit-scrollbar {
  width: 6px;
}

.box::-webkit-scrollbar-track,
.session-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.box::-webkit-scrollbar-thumb,
.session-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.box::-webkit-scrollbar-thumb:hover,
.session-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>