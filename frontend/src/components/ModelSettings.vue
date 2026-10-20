<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const opened = ref(false)
const baseUrl = ref('https://api.deepseek.com')
const model = ref('deepseek-v4-pro')
const apiKey = ref('')
const keyConfigured = ref(false)
const busy = ref(false)
const feedback = ref('')
const success = ref(false)

const openSettings = async () => {
  opened.value = true
  apiKey.value = ''
  feedback.value = ''
  busy.value = true
  try {
    const { data } = await axios.get('/api/settings/model')
    baseUrl.value = data.base_url
    model.value = data.model
    keyConfigured.value = data.key_configured
  } catch {
    feedback.value = '读取配置失败，请检查服务是否运行。'
    success.value = false
  } finally {
    busy.value = false
  }
}

const submitSettings = async (test: boolean) => {
  busy.value = true
  feedback.value = ''
  try {
    const { data } = await axios.post(`/api/settings/model${test ? '/test' : ''}`, {
      base_url: baseUrl.value,
      model: model.value,
      api_key: apiKey.value,
    })
    success.value = test ? data.ok : true
    feedback.value = data.message
    if (!test) {
      apiKey.value = ''
      keyConfigured.value = true
    }
  } catch (error: any) {
    success.value = false
    const detail = error.response?.data?.detail
    feedback.value = typeof detail === 'string' ? detail : '请求失败，请检查配置和网络后重试。'
  } finally {
    busy.value = false
  }
}

const closeSettings = () => {
  if (busy.value) return
  apiKey.value = ''
  opened.value = false
}
</script>

<template>
  <button class="settings-trigger" @click="openSettings">⚙ 模型设置</button>
  <div v-if="opened" class="settings-overlay" @click.self="closeSettings" @keydown.esc="closeSettings">
    <section class="settings-panel" role="dialog" aria-modal="true" aria-labelledby="settings-title">
      <div class="settings-heading">
        <div>
          <h2 id="settings-title">DeepSeek 模型设置</h2>
          <p>填写你的接口信息，即可开始深度搜索。</p>
        </div>
        <button class="settings-close" :disabled="busy" aria-label="关闭模型设置" @click="closeSettings">×</button>
      </div>
      <form @submit.prevent="submitSettings(false)">
        <label for="model-api-key">API Key</label>
        <input id="model-api-key" v-model="apiKey" type="password" autocomplete="off" spellcheck="false"
          :disabled="busy" :placeholder="keyConfigured ? '已保存密钥，留空则保持不变' : '请输入你的 DeepSeek API Key'" />
        <p class="settings-hint">{{ keyConfigured ? '已配置密钥。' : '尚未配置密钥。' }} 密钥保存在本机，页面不会回显。</p>

        <label for="model-base-url">Base URL</label>
        <input id="model-base-url" v-model="baseUrl" type="url" required :disabled="busy" spellcheck="false" />
        <p class="settings-hint">官方接口已预填；使用兼容服务时可修改。</p>

        <label for="model-name">模型名称</label>
        <input id="model-name" v-model="model" list="deepseek-models" required :disabled="busy" spellcheck="false" />
        <datalist id="deepseek-models">
          <option value="deepseek-v4-pro">DeepSeek V4 Pro</option>
          <option value="deepseek-flash">DeepSeek Flash</option>
        </datalist>
        <p class="settings-hint">默认使用 V4 Pro，也可填写你的服务支持的模型名称。</p>

        <p v-if="feedback" class="settings-feedback" :class="{ success }" role="status">{{ feedback }}</p>
        <div class="settings-actions">
          <button type="button" :disabled="busy" @click="submitSettings(true)">{{ busy ? '处理中…' : '测试连接' }}</button>
          <button class="settings-save" type="submit" :disabled="busy">保存设置</button>
        </div>
        <p class="settings-note">测试连接会发送一条简短请求。保存后，下次提问立即生效。</p>
      </form>
    </section>
  </div>
</template>

<style scoped>
.settings-trigger { position: fixed; top: 20px; right: 24px; z-index: 15; color: #e3e3e3; background: #25272b; border: 1px solid #45484d; border-radius: 10px; padding: 10px 16px; cursor: pointer; font-size: 14px; }
.settings-trigger:hover { background: #34373d; }
.settings-overlay { position: fixed; inset: 0; z-index: 30; display: flex; align-items: center; justify-content: center; padding: 20px; background: #0009; }
.settings-panel { box-sizing: border-box; width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto; border: 1px solid #444; border-radius: 18px; background: #1e1f20; padding: 28px; color: #e3e3e3; box-shadow: 0 20px 80px #0008; }
.settings-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 24px; }
.settings-heading h2 { font-size: 20px; margin: 0 0 8px; }
.settings-heading p { font-size: 13px; color: #a5a9b0; margin: 0; }
.settings-close { color: #a5a9b0; background: none; border: none; font-size: 28px; cursor: pointer; line-height: 1; }
label { display: block; font-size: 14px; margin-bottom: 8px; }
input { box-sizing: border-box; display: block; width: 100%; background: #131415; color: #eee; border: 1px solid #444; border-radius: 8px; padding: 12px; font-size: 14px; }
input:focus { outline: 2px solid #7898ed; outline-offset: 1px; }
.settings-hint { font-size: 12px; color: #a5a9b0; line-height: 1.6; margin: 7px 0 20px; }
.settings-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.settings-actions button { border: 1px solid #53565b; border-radius: 8px; padding: 10px 18px; background: #2c2e33; color: #eee; cursor: pointer; }
.settings-actions .settings-save { background: #b8ccff; color: #14264f; border-color: #b8ccff; }
button:disabled { opacity: .5; cursor: wait; }
.settings-feedback { font-size: 13px; line-height: 1.6; color: #ffb4ab; background: #ffb4ab0a; padding: 12px; border-radius: 8px; }
.settings-feedback.success { color: #9dd7ad; background: #9dd7ad0a; }
.settings-note { font-size: 12px; line-height: 1.6; color: #a5a9b0; margin-bottom: 0; }
@media (max-width: 540px) { .settings-panel { padding: 22px; } .settings-trigger { top: 12px; right: 12px; } }
</style>
