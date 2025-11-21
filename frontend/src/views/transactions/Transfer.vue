<!--
转账功能页面
@version: v1.0.0
@date: 2024-12-06
-->
<template>
  <div class="transfer-money">
    <div class="page-header">
      <h1>转账汇款</h1>
      <p>安全便捷的校园转账服务</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧转账表单 -->
      <el-col :xs="24" :lg="16">
        <el-card class="transfer-card">
          <template #header>
            <div class="card-header">
              <h3>转账信息</h3>
              <el-tag type="success">余额: ¥{{ userBalance }}</el-tag>
            </div>
          </template>

          <el-form
            ref="transferFormRef"
            :model="transferForm"
            :rules="formRules"
            label-width="100px"
            label-position="left"
          >
            <el-form-item label="收款人" prop="recipient">
              <div class="recipient-input">
                <el-select
                  v-model="transferForm.recipient"
                  placeholder="选择收款人或输入学号"
                  filterable
                  allow-create
                  remote
                  :remote-method="searchRecipient"
                  :loading="searching"
                  style="width: 100%"
                  @change="handleRecipientChange"
                >
                  <el-option
                    v-for="user in recipientList"
                    :key="user.id"
                    :label="`${user.name} (${user.studentId})`"
                    :value="user.studentId"
                  >
                    <div style="display: flex; justify-content: space-between">
                      <span>{{ user.name }}</span>
                      <span style="color: var(--text-color-secondary)">{{ user.studentId }}</span>
                    </div>
                  </el-option>
                </el-select>
                
                <el-button
                  type="primary"
                  style="margin-left: 8px"
                  @click="showContactDialog"
                >
                  选择联系人
                </el-button>
              </div>
              
              <div v-if="recipientInfo" class="recipient-info">
                <el-alert
                  :title="`收款人: ${recipientInfo.name} (${recipientInfo.department})`"
                  type="info"
                  :closable="false"
                  show-icon
                />
              </div>
            </el-form-item>

            <el-form-item label="转账金额" prop="amount">
              <div class="amount-input">
                <el-input
                  v-model="transferForm.amount"
                  placeholder="请输入转账金额"
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="10000"
                >
                  <template #prefix>¥</template>
                </el-input>
                
                <div class="quick-amounts">
                  <el-button
                    v-for="amount in quickAmounts"
                    :key="amount"
                    size="small"
                    @click="setQuickAmount(amount)"
                  >
                    ¥{{ amount }}
                  </el-button>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="转账类型" prop="type">
              <el-radio-group v-model="transferForm.type">
                <el-radio value="normal">普通转账</el-radio>
                <el-radio value="urgent">加急转账 (+¥2手续费)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="转账用途" prop="purpose">
              <el-select
                v-model="transferForm.purpose"
                placeholder="选择转账用途"
                style="width: 100%"
              >
                <el-option label="学习费用" value="study" />
                <el-option label="生活费用" value="living" />
                <el-option label="借款还款" value="loan" />
                <el-option label="活动费用" value="activity" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>

            <el-form-item label="转账备注" prop="note">
              <el-input
                v-model="transferForm.note"
                type="textarea"
                :rows="3"
                placeholder="请输入转账备注（可选）"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="支付密码" prop="password">
              <el-input
                v-model="transferForm.password"
                type="password"
                placeholder="请输入支付密码"
                show-password
                maxlength="20"
              />
            </el-form-item>

            <el-form-item>
              <div class="transfer-summary">
                <div class="summary-item">
                  <span>转账金额:</span>
                  <span class="amount">¥{{ transferForm.amount || '0.00' }}</span>
                </div>
                <div class="summary-item">
                  <span>手续费:</span>
                  <span class="fee">¥{{ transferFee }}</span>
                </div>
                <div class="summary-item total">
                  <span>总计:</span>
                  <span class="total-amount">¥{{ totalAmount }}</span>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <div class="form-actions">
                <el-button
                  type="primary"
                  size="large"
                  :loading="transferring"
                  @click="confirmTransfer"
                >
                  <el-icon><CreditCard /></el-icon>
                  确认转账
                </el-button>
                
                <el-button size="large" @click="resetForm">
                  <el-icon><RefreshRight /></el-icon>
                  重置
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧信息面板 -->
      <el-col :xs="24" :lg="8">
        <!-- 安全提示 -->
        <el-card class="info-card" style="margin-bottom: 20px">
          <template #header>
            <h4>安全提示</h4>
          </template>
          <ul class="security-tips">
            <li>转账前请确认收款人信息</li>
            <li>请妥善保管您的支付密码</li>
            <li>如有疑问请联系客服</li>
            <li>转账记录可在交易历史中查看</li>
          </ul>
        </el-card>

        <!-- 最近转账记录 -->
        <el-card class="info-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <h4>最近转账</h4>
              <el-link type="primary" @click="$router.push('/transactions/history')">
                查看全部
              </el-link>
            </div>
          </template>
          
          <div class="recent-transfers">
            <div
              v-for="record in recentTransfers"
              :key="record.id"
              class="transfer-record"
              @click="setFromRecord(record)"
            >
              <div class="record-info">
                <div class="recipient">{{ record.recipientName }}</div>
                <div class="amount">¥{{ record.amount }}</div>
              </div>
              <div class="record-meta">
                <div class="time">{{ formatTime(record.time) }}</div>
                <el-tag :type="getStatusType(record.status)" size="small">
                  {{ record.status }}
                </el-tag>
              </div>
            </div>
            
            <el-empty
              v-if="recentTransfers.length === 0"
              description="暂无转账记录"
              :image-size="60"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 联系人选择对话框 -->
    <el-dialog
      v-model="contactDialogVisible"
      title="选择联系人"
      width="500px"
    >
      <el-input
        v-model="contactSearch"
        placeholder="搜索联系人..."
        prefix-icon="Search"
        style="margin-bottom: 16px"
      />
      
      <div class="contact-list">
        <div
          v-for="contact in filteredContacts"
          :key="contact.id"
          class="contact-item"
          @click="selectContact(contact)"
        >
          <el-avatar :size="32">{{ contact.name.charAt(0) }}</el-avatar>
          <div class="contact-info">
            <div class="name">{{ contact.name }}</div>
            <div class="student-id">{{ contact.studentId }}</div>
          </div>
          <div class="contact-type">{{ contact.department }}</div>
        </div>
      </div>
    </el-dialog>

    <!-- 转账确认对话框 -->
    <el-dialog
      v-model="confirmDialogVisible"
      title="确认转账"
      width="400px"
      :before-close="handleConfirmClose"
    >
      <div class="confirm-content">
        <el-alert
          title="请确认转账信息"
          type="warning"
          :closable="false"
          show-icon
        />
        
        <div class="confirm-details">
          <div class="detail-item">
            <span>收款人:</span>
            <span>{{ recipientInfo?.name || transferForm.recipient }}</span>
          </div>
          <div class="detail-item">
            <span>转账金额:</span>
            <span class="amount">¥{{ transferForm.amount }}</span>
          </div>
          <div class="detail-item">
            <span>手续费:</span>
            <span>¥{{ transferFee }}</span>
          </div>
          <div class="detail-item total">
            <span>总计:</span>
            <span class="total-amount">¥{{ totalAmount }}</span>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="confirmDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="transferring"
          @click="executeTransfer"
        >
          确认转账
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CreditCard, RefreshRight, Search } from '@element-plus/icons-vue'

const router = useRouter()

// 表单引用
const transferFormRef = ref()

// 响应式数据
const transferring = ref(false)
const searching = ref(false)
const contactDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const contactSearch = ref('')
const userBalance = ref(1234.56)
const recipientList = ref([])
const recipientInfo = ref(null)

// 表单数据
const transferForm = reactive({
  recipient: '',
  amount: '',
  type: 'normal',
  purpose: '',
  note: '',
  password: ''
})

// 表单验证规则
const formRules = {
  recipient: [
    { required: true, message: '请选择收款人', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入转账金额', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!value || isNaN(value) || parseFloat(value) <= 0) {
          callback(new Error('请输入有效的转账金额'))
        } else if (parseFloat(value) > userBalance.value) {
          callback(new Error('转账金额不能超过账户余额'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  type: [
    { required: true, message: '请选择转账类型', trigger: 'change' }
  ],
  purpose: [
    { required: true, message: '请选择转账用途', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入支付密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 快捷金额
const quickAmounts = [10, 50, 100, 200, 500, 1000]

// 模拟联系人数据
const contacts = ref([
  { id: 1, name: '张同学', studentId: '2021001', department: '计算机系' },
  { id: 2, name: '李同学', studentId: '2021002', department: '数学系' },
  { id: 3, name: '王同学', studentId: '2021003', department: '物理系' },
  { id: 4, name: '赵同学', studentId: '2021004', department: '化学系' },
  { id: 5, name: '陈同学', studentId: '2021005', department: '英语系' }
])

// 模拟最近转账记录
const recentTransfers = ref([
  {
    id: 1,
    recipientName: '张同学',
    amount: 50.00,
    status: '成功',
    time: new Date().getTime() - 1000 * 60 * 30
  },
  {
    id: 2,
    recipientName: '李同学', 
    amount: 100.00,
    status: '成功',
    time: new Date().getTime() - 1000 * 60 * 60 * 2
  },
  {
    id: 3,
    recipientName: '王同学',
    amount: 25.00,
    status: '处理中',
    time: new Date().getTime() - 1000 * 60 * 60 * 24
  }
])

// 计算属性
const transferFee = computed(() => {
  if (transferForm.type === 'urgent') {
    return '2.00'
  }
  return '0.00'
})

const totalAmount = computed(() => {
  const amount = parseFloat(transferForm.amount) || 0
  const fee = parseFloat(transferFee.value) || 0
  return (amount + fee).toFixed(2)
})

const filteredContacts = computed(() => {
  if (!contactSearch.value) return contacts.value
  
  const query = contactSearch.value.toLowerCase()
  return contacts.value.filter(contact =>
    contact.name.toLowerCase().includes(query) ||
    contact.studentId.includes(query) ||
    contact.department.toLowerCase().includes(query)
  )
})

// 方法
const searchRecipient = async (query) => {
  if (!query) {
    recipientList.value = []
    return
  }
  
  searching.value = true
  try {
    // 模拟搜索API
    await new Promise(resolve => setTimeout(resolve, 500))
    recipientList.value = contacts.value.filter(contact =>
      contact.name.includes(query) || contact.studentId.includes(query)
    )
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    searching.value = false
  }
}

const handleRecipientChange = async (value) => {
  // 根据学号获取用户信息
  const user = contacts.value.find(contact => contact.studentId === value)
  if (user) {
    recipientInfo.value = user
  } else {
    recipientInfo.value = null
  }
}

const setQuickAmount = (amount) => {
  transferForm.amount = amount.toString()
}

const showContactDialog = () => {
  contactDialogVisible.value = true
  contactSearch.value = ''
}

const selectContact = (contact) => {
  transferForm.recipient = contact.studentId
  recipientInfo.value = contact
  contactDialogVisible.value = false
}

const setFromRecord = (record) => {
  const contact = contacts.value.find(c => c.name === record.recipientName)
  if (contact) {
    transferForm.recipient = contact.studentId
    recipientInfo.value = contact
    transferForm.amount = record.amount.toString()
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status) => {
  const statusMap = {
    '成功': 'success',
    '失败': 'danger',
    '处理中': 'warning'
  }
  return statusMap[status] || 'info'
}

const confirmTransfer = async () => {
  try {
    const valid = await transferFormRef.value.validate()
    if (!valid) return

    confirmDialogVisible.value = true
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleConfirmClose = (done) => {
  if (transferring.value) {
    ElMessage.warning('转账正在进行中，请稍候...')
    return
  }
  done()
}

const executeTransfer = async () => {
  try {
    transferring.value = true

    // 模拟转账处理
    await new Promise(resolve => setTimeout(resolve, 3000))

    // 模拟成功
    ElMessage.success('转账成功！')
    
    // 更新余额
    userBalance.value -= parseFloat(totalAmount.value)
    
    // 重置表单
    resetForm()
    confirmDialogVisible.value = false
    
    // 跳转到交易记录
    router.push('/transactions/history')
    
  } catch (error) {
    console.error('转账失败:', error)
    ElMessage.error('转账失败，请重试')
  } finally {
    transferring.value = false
  }
}

const resetForm = () => {
  transferFormRef.value?.resetFields()
  recipientInfo.value = null
  recipientList.value = []
}

// 组件挂载
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
.transfer-money {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  h1 {
    margin: 0 0 8px 0;
    color: var(--text-color-primary);
  }
  p {
    margin: 0;
    color: var(--text-color-regular);
  }
}

.transfer-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    color: var(--text-color-primary);
  }
}

.recipient-input {
  display: flex;
  align-items: center;
}

.recipient-info {
  margin-top: 8px;
}

.amount-input {
  .quick-amounts {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
}

.transfer-summary {
  background: var(--fill-color-lighter);
  padding: 16px;
  border-radius: 8px;
  
  .summary-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    &.total {
      font-weight: 600;
      font-size: 16px;
      border-top: 1px solid var(--border-color-light);
      padding-top: 8px;
      margin-top: 8px;
    }
  }
  
  .amount, .fee, .total-amount {
    color: var(--color-primary);
  }
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 24px;
}

.info-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  h4 {
    margin: 0;
    color: var(--text-color-primary);
  }
}

.security-tips {
  margin: 0;
  padding-left: 20px;
  
  li {
    margin-bottom: 8px;
    color: var(--text-color-regular);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

.recent-transfers {
  .transfer-record {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border: 1px solid var(--border-color-lighter);
    border-radius: 6px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: var(--color-primary);
      background-color: var(--color-primary-light-9);
    }
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .record-info {
    .recipient {
      font-weight: 500;
      margin-bottom: 4px;
    }
    
    .amount {
      color: var(--color-primary);
      font-size: 14px;
    }
  }
  
  .record-meta {
    text-align: right;
    
    .time {
      font-size: 12px;
      color: var(--text-color-secondary);
      margin-bottom: 4px;
    }
  }
}

.contact-list {
  max-height: 300px;
  overflow-y: auto;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: var(--fill-color-lighter);
  }
  
  .contact-info {
    flex: 1;
    margin-left: 12px;
    
    .name {
      font-weight: 500;
      margin-bottom: 4px;
    }
    
    .student-id {
      font-size: 14px;
      color: var(--text-color-secondary);
    }
  }
  
  .contact-type {
    font-size: 12px;
    color: var(--text-color-secondary);
  }
}

.confirm-content {
  .confirm-details {
    margin-top: 16px;
    
    .detail-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--border-color-lighter);
      
      &:last-child {
        border-bottom: none;
      }
      
      &.total {
        font-weight: 600;
        font-size: 16px;
        color: var(--color-primary);
      }
    }
  }
}

@media (max-width: 768px) {
  .transfer-money {
    padding: 10px;
  }
  
  .recipient-input {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .form-actions {
    flex-direction: column;
    
    .el-button {
      width: 100%;
    }
  }
}
</style> 